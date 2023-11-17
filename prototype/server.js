const { spawn } = require("child_process");
const express = require("express");
const app = express();
const bodyParser = require("body-parser");

const PYTHON = "python"; // Replace this with the actual path to your Python executable

app.use(bodyParser.json());

app.post("/job_match", (req, res) => {
  const x = req.get("resume_text");
  const python = spawn(PYTHON, ["./script.py", x]);

  python.stdout.on("data", function (data) {
    res.send(data.toString());
  });

  python.stderr.on("data", function (data) {
    console.error(`Error: ${data}`);
    res.status(500).send("Internal Server Error");
  });

  python.on("close", (code) => {
    if (code !== 0) {
      console.error(`Script exited with code ${code}`);
      res.status(500).send("Internal Server Error");
    }
  });

  python.on("error", (err) => {
    console.error(`Failed to start script: ${err}`);
    res.status(500).send("Internal Server Error");
  });
});

const PORT = 3000; // Change this to the desired port
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
