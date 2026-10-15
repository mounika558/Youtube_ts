import os
from typing import TypedDict

from dotenv import load_dotenv
from google import genai
from google.genai import types
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END

from transcript import get_transcript, extract_video_id

load_dotenv()

MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


# 1) STATE
class State(TypedDict, total=False):
    url: str
    language: str       # language the user wants
    transcript: str
    summary: str
    source: str         # "transcript" or "video"
    error: str


# 2) THE LLMs
llm = ChatGoogleGenerativeAI(model=MODEL, temperature=0.2)
genai_client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))


# 3) HELPERS
SUMMARY_FORMAT = (
    "Write the summary in English. Start directly with the content, "
    "with no introduction line.\n"
    "Format:\n"
    "1. A 2-3 sentence overview\n"
    "2. Key points as bullet points\n"
    "3. One-line takeaway"
)


def to_text(content) -> str:
    if isinstance(content, list):
        return "".join(
            p if isinstance(p, str) else p.get("text", "") for p in content
        )
    return content


# 4) NODES
def fetch_transcript(state: State) -> dict:
    try:
        return {"transcript": get_transcript(state["url"])}
    except ValueError as e:
        return {"error": str(e)}
    except Exception:
        return {}


def summarize(state: State) -> dict:
    prompt = (
        "Summarize the YouTube video transcript below.\n"
        f"{SUMMARY_FORMAT}\n\n"
        f"TRANSCRIPT:\n{state['transcript']}"
    )
    response = llm.invoke(prompt)
    return {"summary": to_text(response.content), "source": "transcript"}


def summarize_video(state: State) -> dict:
    video_id = extract_video_id(state["url"])
    clean_url = f"https://www.youtube.com/watch?v={video_id}"
    prompt = f"Watch this YouTube video and summarize it.\n{SUMMARY_FORMAT}"
    try:
        response = genai_client.models.generate_content(
            model=MODEL,
            contents=types.Content(
                parts=[
                    types.Part(file_data=types.FileData(file_uri=clean_url)),
                    types.Part(text=prompt),
                ]
            ),
        )
        return {"summary": response.text, "source": "video"}
    except Exception as e:
        return {
            "error": (
                "No captions were available, and Gemini couldn't analyze the "
                f"video directly either. Details: {e}"
            )
        }


def translate(state: State) -> dict:
    # Nothing to do if something failed earlier or English was requested
    if state.get("error") or state["language"].strip().lower() == "english":
        return {}
    prompt = (
        f"Translate the following text into {state['language']}.\n"
        f"Your entire reply must be written in {state['language']}, "
        "using its own script.\n"
        "Keep the same structure and bullet formatting. "
        "Output only the translation, with no introduction.\n\n"
        f"TEXT:\n{state['summary']}"
    )
    response = llm.invoke(prompt)
    return {"summary": to_text(response.content)}


# 5) ROUTING
def route_after_fetch(state: State) -> str:
    if state.get("error"):
        return "stop"
    if state.get("transcript"):
        return "has_transcript"
    return "no_transcript"


# 6) BUILD THE GRAPH
builder = StateGraph(State)
builder.add_node("fetch_transcript", fetch_transcript)
builder.add_node("summarize", summarize)
builder.add_node("summarize_video", summarize_video)
builder.add_node("translate", translate)

builder.add_edge(START, "fetch_transcript")
builder.add_conditional_edges(
    "fetch_transcript",
    route_after_fetch,
    {
        "has_transcript": "summarize",
        "no_transcript": "summarize_video",
        "stop": END,
    },
)
builder.add_edge("summarize", "translate")
builder.add_edge("summarize_video", "translate")
builder.add_edge("translate", END)

graph = builder.compile()