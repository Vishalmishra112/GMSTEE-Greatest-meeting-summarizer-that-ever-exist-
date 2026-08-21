import os
import json
import shutil
import subprocess
from datetime import datetime
from typing import List
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import whisper
import ollama
import PyPDF2
import docx

app = FastAPI(title="AI powered GMSTEE API")

STORAGE_DIR = "storage"
os.makedirs(STORAGE_DIR, exist_ok=True)

print("Loading Whisper ASR model...")
asr_model = whisper.load_model("base")
print("Whisper model loaded successfully.")

@app.get("/health")
def system_health_check():
    return {"status": "online"}

@app.post("/process-meeting")
async def process_meeting(files: List[UploadFile] = File(...)):
    allowed_audio = [".mp3", ".wav", ".m4a", ".ogg", ".flac"]
    allowed_video = [".mp4", ".mkv", ".avi", ".mov"]
    allowed_docs = [".pdf", ".docx"]
    allowed_extensions = allowed_audio + allowed_video + allowed_docs

    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded.")

    combined_transcript = ""

    # Loop through every uploaded file and extract text/audio
    for file in files:
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            continue # Skip unsupported files in the batch

        temp_path = os.path.join(STORAGE_DIR, f"temp_{file.filename}")
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        try:
            transcript_text = ""
            print(f"Processing {file.filename}...")

            # 1. Handle Documents (PDF & DOCX)
            if file_ext in allowed_docs:
                if file_ext == ".pdf":
                    reader = PyPDF2.PdfReader(temp_path)
                    for page in reader.pages:
                        text = page.extract_text()
                        if text:
                            transcript_text += text + "\n"
                elif file_ext == ".docx":
                    doc = docx.Document(temp_path)
                    for para in doc.paragraphs:
                        if para.text.strip():
                            transcript_text += para.text + "\n"

            # 2. Handle Video & Audio via Whisper
            else:
                audio_path = temp_path
                
                if file_ext in allowed_video:
                    audio_path = os.path.join(STORAGE_DIR, f"extracted_{file.filename}.wav")
                    subprocess.run([
                        "ffmpeg", "-i", temp_path, "-q:a", "0", "-map", "a", audio_path, "-y"
                    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
                transcription_result = asr_model.transcribe(audio_path)
                transcript_text = transcription_result.get("text", "").strip()
                
                if file_ext in allowed_video and os.path.exists(audio_path):
                    os.remove(audio_path)

            # Add this file's content to the master transcript
            if transcript_text.strip():
                combined_transcript += f"\n\n--- Source: {file.filename} ---\n{transcript_text}"

        except Exception as e:
            print(f"Error processing {file.filename}: {e}")
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    if not combined_transcript.strip():
        raise HTTPException(status_code=400, detail="Could not extract any text from the provided files.")

    # 3. Generate Unified Summary via Ollama
    print("Generating unified summary via Ollama...")
    prompt = f"""
    You are analyzing a meeting that includes multiple sources (documents, audio, video). 
    Summarize the entire combined transcript into key decisions and action items.

    Combined Meeting Content:
    {combined_transcript}

    Return the output exactly in this format:
    SUMMARY:
    <Brief summary of the entire meeting>

    ACTION ITEMS:
    - <Task 1>
    - <Task 2>
    """

    try:
        response = ollama.chat(
            model='llama3',
            messages=[{'role': 'user', 'content': prompt}]
        )
        llm_output = response['message']['content']

        summary_part = ""
        action_items_part = ""
        if "ACTION ITEMS:" in llm_output:
            parts = llm_output.split("ACTION ITEMS:")
            summary_part = parts[0].replace("SUMMARY:", "").strip()
            action_items_part = parts[1].strip()
        else:
            summary_part = llm_output.strip()
            action_items_part = "No explicit action items parsed."

        record_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        record_data = {
            "id": record_id,
            "filename": "Multipart_Meeting",
            "transcript": combined_transcript.strip(),
            "summary": summary_part,
            "action_items": action_items_part,
            "created_at": datetime.now().isoformat()
        }

        save_path = os.path.join(STORAGE_DIR, f"meeting_{record_id}.json")
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(record_data, f, indent=4)

        return {"status": "success", "data": record_data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM Error: {str(e)}")

@app.get("/")
def serve_frontend():
    return FileResponse("index.html")