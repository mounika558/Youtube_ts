# 🎬 YouTube Video Summarizer

Paste a YouTube link and get an AI summary in your preferred language,
including regional Indian languages.

Built with Python, LangChain, LangGraph, Gemini and Streamlit.

## Features
- Summarizes videos from their captions
- Falls back to Gemini analyzing the video directly when captions are missing
- Summary in many languages (choose one or type your own)
- Traced with LangSmith

## Setup
1. Clone the repo and create a virtual environment (Python 3.10)
2. `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and add your API keys
4. `streamlit run app.py`

## Limitations
- Public videos only
- Free-tier API limits apply

<img width="1027" height="557" alt="image" src="https://github.com/user-attachments/assets/2ec9755e-59c0-4527-bf68-d12703a09730" />
<img width="1061" height="732" alt="image" src="https://github.com/user-attachments/assets/9c4cb02b-7462-4c30-807b-64a64d7f4d6a" />

<img width="1917" height="908" alt="image" src="https://github.com/user-attachments/assets/8ce35183-2848-45fc-9872-06c9f9fc18c8" />

