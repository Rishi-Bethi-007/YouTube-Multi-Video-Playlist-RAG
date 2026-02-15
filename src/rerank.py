import json
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from src.config import CHAT_MODEL, OPENAI_API_KEY, TOP_K

_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You are a reranking model. Given a question and candidate passages, select the best passages for answering.\n"
     "Return a JSON object ONLY with key 'keep' as an array of integer indices (0-based), length up to {top_k}.\n"
     "Choose passages that are most directly relevant and non-redundant."),
    ("user",
     "Question:\n{question}\n\nCandidates:\n{candidates}\n\nReturn JSON only.")
])

def rerank(question: str, candidates: list[str], top_k: int = TOP_K) -> list[int]:
    if not candidates:
        return []
    if len(candidates) <= top_k:
        return list(range(len(candidates)))

    llm = ChatOpenAI(model=CHAT_MODEL, api_key=OPENAI_API_KEY, temperature=0)
    cand_text = "\n\n".join([f"[{i}] {c}" for i, c in enumerate(candidates)])
    msg = _PROMPT.format_messages(question=question, candidates=cand_text, top_k=top_k)
    raw = llm.invoke(msg).content.strip()

    try:
        obj = json.loads(raw)
        keep = obj.get("keep", [])
        keep = [int(i) for i in keep if isinstance(i, (int, float, str))]
        keep = [i for i in keep if 0 <= i < len(candidates)]
        # ensure uniqueness & cap
        out = []
        for i in keep:
            if i not in out:
                out.append(i)
        return out[:top_k] if out else list(range(min(top_k, len(candidates))))
    except Exception:
        return list(range(min(top_k, len(candidates))))
