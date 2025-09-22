# CleanVid Project
## Overview
**CleanVid** is a web application that detects offensive words in audio/video content.
It consists of:
  - **Frontend**: React.js appplication for user interface.
  - **Backend**: Python Flask server for audio processing and NLP-based offensive word detection
  - **NLP MOdel**: Pre-trained model for offensive word detection(stored in 'backend/offensive_word_model-main').


---

## Prerequisites
Make sure you have the following installed:
- **Node.js**(v14+ recommended)
- **npm**(comes with Node.js)
- **Python 3.8+**
- **pip** (python package manager)

Optional:'virtualenv' for Python environment isolation

---

## Project Structure

cleanvid-repo/
├── frontend/
│ ├── src/
│ ├── public/
│ ├── package.json
│ └── node_modules/ (ignored)
├── backend/
│ ├── app.py
│ ├── audio_processing.py
│ ├── process_transcript.py
│ ├── transcribe.py
│ ├── requirements.txt
│ └── offensive_word_model-main/ (NLP model)
├── uploads/ (ignored)
├── processed/ (ignored)
└── .gitignore

---

## Setup & Run

### 1. Backend
1. Navigate to backend folder
2. (Optional) Create and activate a virtual environment
3. Install dependencies:
   - pip install -r requiremnets.txt
3.Run the backend server:
   - python app.py(by default the server will run at http://127.0.0.1:5000)

### 2.Frontend
1.Navigate to frontend folder
2.Install dependencies 
  -npm install
3.Run the frontend:
  -npm start(The app will open in your browser at http://localhost:3000)

### 3.NLP Model 

The project uses a finetuned Distilbert model that is finetuned to recognize offensive words with contextual awareness.
Model is located at backend/offensive_word_model-main.

Included in this repo:
 - config.json
 - tokenizer.json
 - tokenizer_config.json
 - special_tokens_map.json

Not included:
 - model.safetensors
 - training_args.bin
   
You can download the weights later from [your hosted location] and place them in backend/offensive_word_model-main/.

---

## Usage 
1. Upload an audio/video file through the frontend.
2. The backend will process the audio, transcribe it, and detect offensive words using the NLP model.
3. Results will be displayed on the frontend interface.
 ---
## Notes

- Ensure uploads/ and processed/ folders exist(they are ignored in Git).
- you may need to adjust file paths if running on a different OS


