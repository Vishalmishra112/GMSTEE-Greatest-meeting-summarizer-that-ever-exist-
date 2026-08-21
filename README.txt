							AI-Powered GMSTEE (Greatest Meeting Summarizer That Ever Exists)

AI-Powered GMSTEE is a robust, fully local, full-stack application designed to transform lengthy meetings and multi-format resources into actionable intelligence. Built with privacy and performance in mind, the system operates entirely offline. It utilizes OpenAI's Whisper for highly accurate audio transcription and Llama 3 via Ollama to distill massive amounts of text into key decisions. The application features a responsive dashboard, unified multimodal data ingestion, and direct exports to JSON, Markdown, or Text files.

--------------------------------------------------
REQUIREMENTS & PROJECT STRUCTURE
--------------------------------------------------

[Hardware]
Minimum: Intel Core i3 (2nd Gen) or equivalent, 8GB RAM (required to hold AI models in memory), and 10GB free storage. Note: Running Llama 3 and Whisper without a dedicated GPU will work, but processing and generation times will be significantly slower.

[Software Core]
Python 3.8+, FFmpeg (for media conversion), Ollama (with the llama3 model downloaded).

[Python Classes/Modules]
fastapi, uvicorn, python-multipart, openai-whisper, ollama, PyPDF2, python-docx.

[Project Structure]
* main.py: The FastAPI backend handling the REST endpoints, file parsing, and AI inference pipeline.
* index.html: The frontend user interface featuring the configuration panel, dynamic file manager, and result display.
* storage/: An auto-generated directory used by the backend for temporary uploads and saving the final JSON records.

--------------------------------------------------
SETUP & EXECUTION
--------------------------------------------------

To create and run this project, execute these exact steps:
1. Install FFmpeg on your machine and ensure it is added to your system's PATH.
2. Install Ollama, open your terminal, and run "ollama run llama3" to pull the necessary LLM.
3. Create a Python virtual environment, activate it, and install all required Python libraries using pip.
4. Save the provided backend code as "main.py" and the frontend code as "index.html" in your root directory.
5. Start the local server by executing "python -m uvicorn main:app --reload --port 8000" in your terminal.
6. Open a web browser and navigate to http://127.0.0.1:8000 to access your new dashboard.

--------------------------------------------------
TROUBLESHOOTING COMMON ISSUES
--------------------------------------------------

If the system malfunctions during processing, investigate these common culprits:
* FFmpeg Not Found: If video-to-audio extraction fails instantly, it means FFmpeg is not correctly configured in your system's Environment Variables.
* Backend Disconnection: If the frontend health check displays a red offline badge, verify that Uvicorn is actively running in your terminal and no port conflicts exist.
* Memory Exhaustion: If processing large stitched files crashes on a minimum-spec machine (like 8GB RAM), try processing files individually to prevent memory overflow during model loading.