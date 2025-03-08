import os
import ffmpeg
import whisper
import re
import numpy as np
from pydub import AudioSegment
from pydub.generators import Sine

# Load Whisper Model
model = whisper.load_model("base")

# ✅ STEP 1: Extract Audio from Video
def extract_audio(video_path, output_audio="extracted_audio.wav"):
    """Extracts audio from a video using FFmpeg"""
    try:
        ffmpeg.input(video_path).output(output_audio, format='wav', acodec='pcm_s16le', ar='16000').run(overwrite_output=True)
        return output_audio
    except Exception as e:
        print(f"Error extracting audio: {e}")
        return None

# ✅ STEP 2: Transcribe Audio using Whisper
def transcribe_audio(audio_path):
    """Transcribes audio and extracts word timestamps"""
    result = model.transcribe(audio_path, word_timestamps=True)
    
    word_timestamps = []
    for segment in result.get("segments", []):
        for word in segment.get("words", []):
            if all(k in word for k in ["word", "start", "end"]):  # Ensure all keys exist
                word_timestamps.append((word["word"], word["start"], word["end"]))
    
    return result["text"], word_timestamps

# ✅ STEP 3: Censor Bad Words & Collect Beep Positions
def censor_text(text, words):
    """Replaces detected bad words with '****' and returns beep timestamps"""
    bad_words = ["badword1", "badword2", "news", "information"]  # Customize this list
    beep_positions = []

    censored_text = text
    for word, start_time, end_time in words:
        clean_word = word.lower().strip()  # Convert to lowercase and remove extra spaces
        for bad_word in bad_words:
            if re.search(rf'\b{re.escape(bad_word)}\b', clean_word, re.IGNORECASE):
                censored_text = re.sub(rf'\b{re.escape(bad_word)}\b', "****", censored_text, flags=re.IGNORECASE)
                beep_positions.append((int(start_time * 1000), int(end_time * 1000)))  # Convert to milliseconds

    print("Beep positions after text censoring:", beep_positions)  # Debugging
    return censored_text, beep_positions


# ✅ STEP 4: Generate Beep Sound if Not Exists
def generate_beep(duration=500):
    """Generate a beep sound and save it if missing"""
    beep_path = "static/beep.mp3"
    if not os.path.exists(beep_path):
        os.makedirs("static", exist_ok=True)
        beep = Sine(1000).to_audio_segment(duration=duration)  # 1000 Hz tone
        beep.export(beep_path, format="mp3")
    return beep_path

# ✅ STEP 5: Mute & Replace Words with Beep
def mute_and_beep_words(audio_path, beep_positions, buffer_ms=50):
    """Mutes censored words with a buffer and replaces them with a beep"""
    audio = AudioSegment.from_wav(audio_path)
    beep = AudioSegment.from_file(generate_beep())  # Load beep sound

    print("Muting and replacing words with beep at positions:", beep_positions)  # Debugging

    for start_time, end_time in beep_positions:
        start_time = max(0, int(start_time - buffer_ms))  # Extend mute at the start
        end_time = min(len(audio), int(end_time + buffer_ms))  # Extend mute at the end
        duration = end_time - start_time

        # Create a silence segment of the same duration
        silence = AudioSegment.silent(duration=duration)

        # Adjust beep to match duration
        beep_sound = beep[:duration] if len(beep) > duration else beep

        # Apply silence first (to remove the word)
        audio = audio[:start_time] + silence + audio[end_time:]

        # Overlay beep at the exact start time
        audio = audio.overlay(beep_sound, position=start_time)

    censored_audio_path = "censored_audio.wav"
    audio.export(censored_audio_path, format="wav")
    return censored_audio_path


# ✅ STEP 6: Full Pipeline Function
def process_video(video_path):
    """Processes a video to extract, transcribe, censor, and beep audio"""
    audio_path = extract_audio(video_path)
    if not audio_path:
        return None

    original_text, word_timestamps = transcribe_audio(audio_path)
    censored_text, beep_positions = censor_text(original_text, word_timestamps)
    censored_audio_path = mute_and_beep_words(audio_path, beep_positions)

    return {
        "original_text": original_text,
        "censored_text": censored_text,
        "censored_audio": censored_audio_path
    }

# ✅ Run the pipeline
if __name__ == "__main__":
    video_file = "input_video.mp4"  # Change to your file
    result = process_video(video_file)

    print("Original Text:", result["original_text"])
    print("Censored Text:", result["censored_text"])
    print("Censored Audio File:", result["censored_audio"])
