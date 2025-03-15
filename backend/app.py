from flask import Flask, request, jsonify, send_file
import os
from transcribe import transcribe_audio
from process_transcript import detect_offensive_words
from audio_processing import extract_audio, censor_audio, merge_audio_with_video

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
PROCESSED_FOLDER = "processed"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

@app.route("/upload", methods=["POST"])
def upload_video():
    """Handles file upload, transcription, and audio censoring"""
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    video_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(video_path)

    # 1️⃣ **Extract Audio**
    audio_path = extract_audio(video_path)  
    if not audio_path:
        return jsonify({"error": "Failed to extract audio"}), 500  

    # 2️⃣ **Transcribe Audio**
    transcript_output = transcribe_audio(audio_path)  
    transcript_text = transcript_output["original_text"]
    word_timestamps = transcript_output["word_timestamps"]

    # 3️⃣ **Detect Offensive Words**
    offensive_words_output = detect_offensive_words(transcript_text, word_timestamps)
    transcript_json = offensive_words_output["output_json"]

    # 4️⃣ **Censor Audio**
    censored_audio_path = censor_audio(audio_path, transcript_json)  

    # 5️⃣ **Merge Censored Audio Back to Video**
    censored_video_path = merge_audio_with_video(video_path, censored_audio_path)

    return jsonify({
        "original_text": transcript_text,
        "censored_text": offensive_words_output["censored_text"],
        "censored_audio": censored_audio_path,
        "censored_video": censored_video_path
    })

@app.route("/download/<filename>")
def download_file(filename):
    """Allows users to download processed files"""
    file_path = os.path.join(PROCESSED_FOLDER, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return jsonify({"error": "File not found"}), 404

if __name__ == "__main__":
    app.run(debug=True)
