from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from src.config import CHAT_MODEL, OPENAI_API_KEY

_SUMMARY_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You maintain a compact conversation summary for a video-grounded chatbot.\n"
     "Update the summary using the new messages. Keep it short (max ~1500 characters).\n"
     "Include: user goals, entities, and unresolved questions.\n"
     "Do NOT invent facts. If unsure, omit.\n"
     "Return ONLY the updated summary text."),
    ("user",
     "Current summary:\n{summary}\n\n"
     "New messages:\n{new_messages}\n\n"
     "Updated summary:")
])

def update_summary(summary: str, new_messages: list[dict], max_chars: int = 1500) -> str:
    """
    new_messages: [{"role":"user"|"assistant", "content": "..."}]
    """
    if not new_messages:
        return summary or ""

    llm = ChatOpenAI(model=CHAT_MODEL, api_key=OPENAI_API_KEY, temperature=0)

    formatted = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in new_messages])
    out = llm.invoke(_SUMMARY_PROMPT.format_messages(summary=summary or "", new_messages=formatted)).content.strip()

    # hard cap (defensive)
    if len(out) > max_chars:
        out = out[:max_chars].rsplit(" ", 1)[0]
    return out
