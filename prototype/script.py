import pandas as pd
import faiss
import numpy as np
import sys
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

##############################################
#                                            #
#    Need to use Docker Image in Prod/Dev    #
#                                            #
##############################################

# Get Prior Jobs Data
jobs_data = pd.read_csv("jobs_data/data_job_posts.csv")
# Clean the data
jobs_data = jobs_data[["Title", "JobDescription"]].dropna(
    subset=['JobDescription'])

# Create TF-IDF vectorizer
vectorizer = TfidfVectorizer()

job_tfidf = vectorizer.fit_transform(jobs_data['JobDescription'])

# Build an index for job descriptions using faiss
index = faiss.IndexFlatIP(job_tfidf.shape[1])
job_tfidf_np = job_tfidf.astype(
    'float32').toarray()  # conversion to numpy array
index.add(job_tfidf_np.astype('float32'))
matches = []


def find_matches(resume_text):
    # Transform the current resume
    resume_tfidf = vectorizer.transform([resume_text])

    # Convert the sparse matrix to a dense NumPy array of float32
    resume_tfidf_np = resume_tfidf.toarray().astype('float32')  # Change this line

    # Perform approximate nearest neighbor search for the top 5 matches
    _, best_job_indices = index.search(resume_tfidf_np, 5)

    # Extract the top 5 job titles and their corresponding similarity scores
    top_5_job_titles = []
    top_5_similarity_scores = []

    for best_job_index in best_job_indices[0]:
        try:
            # Retrieve the job title and similarity score for the current index
            best_job_title = jobs_data.loc[best_job_index, 'Title']
            similarity_score = cosine_similarity(
                resume_tfidf, job_tfidf[best_job_index])[0, 0]
        except KeyError:
            # Handle the KeyError by passing over the current index
            continue

        top_5_job_titles.append(best_job_title)
        top_5_similarity_scores.append(similarity_score)

    # Store the top 5 matches in the list
    matches.append({'Resume': resume_text, 'Top5JobTitles': top_5_job_titles,
                   'Top5SimilarityScores': top_5_similarity_scores})


resume_text = sys.argv[0]
find_matches(resume_text)
print(matches)