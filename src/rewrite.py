from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from src.config import CHAT_MODEL, OPENAI_API_KEY
from src.cache import get_json, set_json, sha1

_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "Rewrite the user question into a clean, specific search query for retrieving relevant transcript passages.\n"
     "Use the conversation summary + recent turns to resolve pronouns and follow-ups.\n"
     "Return ONLY the rewritten query text."),
    ("user",
     "Conversation summary:\n{summary}\n\n"
     "Recent turns:\n{recent}\n\n"
     "User question:\n{question}\n\n"
     "Rewritten search query:")
])

def rewrite_query(question: str, namespace: str, summary: str, recent_turns: list[dict]) -> tuple[str, bool]:
    # cache key must include memory context, otherwise follow-ups cache wrong
    recent_text = "\n".join([f"{m['role']}:{m['content']}" for m in (recent_turns or [])])
    key = f"rewrite:{namespace}:{sha1(summary or '')}:{sha1(recent_text)}:{sha1(question)}"
    cached = get_json(key)
    if cached:
        return cached["q"], True

    llm = ChatOpenAI(model=CHAT_MODEL, api_key=OPENAI_API_KEY, temperature=0)
    recent_fmt = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in (recent_turns or [])])

    out = llm.invoke(_PROMPT.format_messages(
        summary=summary or "",
        recent=recent_fmt or "(none)",
        question=question
    )).content.strip()

    set_json(key, {"q": out}, ttl_seconds=24 * 3600)  # 1 day is enough for chat sessions
    return out, False
