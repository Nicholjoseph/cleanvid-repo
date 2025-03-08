from flask import Flask, request, jsonify, send_file
import os
from audio_processing import extract_audio, transcribe_audio, censor_text, mute_and_beep_words


app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
PROCESSED_FOLDER = "processed"
STATIC_FOLDER = "static"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

os.makedirs(STATIC_FOLDER, exist_ok=True)

@app.route("/upload", methods=["POST"])
def upload_video():
    """Handles video file upload"""
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    video_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(video_path)

    extracted_audio = extract_audio(video_path)
    if extracted_audio:
        transcribed_text, word_timestamps = transcribe_audio(extracted_audio)
        censored_text, beep_positions = censor_text(transcribed_text, word_timestamps)

        censored_audio = mute_and_beep_words(extracted_audio, beep_positions)

        return jsonify({
            "original_text": transcribed_text,
            "censored_text": censored_text,
            "censored_audio": censored_audio
        })
    else:
        return jsonify({"error": "Failed to process audio"}), 500

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
