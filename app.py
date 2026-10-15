import streamlit as st
from graph import graph

LANGUAGES = [
    "English", "Tamil", "Hindi", "Telugu", "Malayalam", "Kannada",
    "Bengali", "Marathi", "Gujarati", "Punjabi", "Urdu",
]
OTHER = "Other (type your own)"

st.set_page_config(page_title="YouTube Summarizer", page_icon="🎬")
st.title("🎬 YouTube Video Summarizer")
st.write("Paste a YouTube link and get a quick summary.")

url = st.text_input("YouTube URL", placeholder="https://www.youtube.com/watch?v=...")

choice = st.selectbox("Summary language", LANGUAGES + [OTHER])

if choice == OTHER:
    language = st.text_input(
        "Type your language",
        placeholder="e.g. Tulu, Konkani, Assamese, Odia, Sinhala, Swahili...",
    ).strip()[:40]  # trim spaces and cap the length
else:
    language = choice

if st.button("Summarize"):
    if not url.strip():
        st.warning("Please paste a URL first.")
    elif not language:
        st.warning("Please type a language.")
    else:
        with st.spinner("Working on it (videos without captions take longer)..."):
            result = graph.invoke({"url": url.strip(), "language": language})

        if result.get("error"):
            st.error(result["error"])
        else:
            if result.get("source") == "video":
                st.info("No captions found, so Gemini analyzed the video directly.")
            st.subheader(f"Summary ({language})")
            st.markdown(result["summary"])