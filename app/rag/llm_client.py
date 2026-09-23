import ollama
from app.rag.retriever import retrieve_chunks

SYSTEM_PROMPT = """You are TradeTutor, an educational assistant that teaches beginner traders about risk management concepts.

RULES:
1. Answer ONLY using the CONTEXT provided below. Do not use outside knowledge, even if you know the answer.
2. Do not introduce unsupported trading rules, numerical ranges, performance claims, or statistics that are not explicitly stated in the CONTEXT.
3. NEVER recommend buying, selling, or holding any specific security, stock, or asset. If asked for a specific investment recommendation, respond: "I can explain trading concepts, but I can't recommend specific investments."
4. NEVER predict future prices or market movements.
5. NEVER give personalized financial advice. If asked for advice about someone's personal money or portfolio, redirect them to a licensed financial advisor.
6. This application is for education only. If the user seems to be treating your answers as real trading advice, remind them this is a learning tool, not financial guidance.

TONE:
- Explain concepts in plain language, as if teaching someone with no prior trading experience.
- Answer in no more than 3 sentences unless the question genuinely requires more detail.
- Avoid jargon; if you must use a trading term, briefly define it the first time you use it.

CONTEXT:
{retrieved_chunks}

USER QUESTION:
{user_question}
"""

DISTANCE_THRESHOLD = 1.0
NO_ANSWER_MESSAGE = (
    "I can only answer questions about risk/reward ratios, stop losses, or "
    "win rates based on this lesson's content; your question may be covered "
    "in a later module. However, please note I cannot recommend specific investments."
)


def is_context_relevant(distances: list[float]) -> bool:
    return min(distances) < DISTANCE_THRESHOLD


def ask_model(question: str, retrieved_chunks: str, model: str = "llama3.2:1b") -> str:
    prompt = SYSTEM_PROMPT.format(retrieved_chunks=retrieved_chunks, user_question=question)
    try:
        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}],
        )
        return response["message"]["content"]
    except ConnectionError:
        return (
            "I couldn't reach the local Ollama model. Please make sure Ollama is "
            "installed and running, then try again."
        )
    except Exception:
        return (
            f"The model '{model}' is unavailable or returned an unexpected response. "
            "Please check that the model is installed in Ollama and try again."
        )


def answer_question(question: str) -> str:
    results = retrieve_chunks(question, n_results=3)
    documents = results["documents"][0]
    distances = results["distances"][0]

    if not is_context_relevant(distances):
        return NO_ANSWER_MESSAGE

    retrieved_text = "\n\n".join(documents)
    return ask_model(question, retrieved_chunks=retrieved_text)


if __name__ == "__main__":
    test_questions = [
        "What is a stop-loss in trading?",
        "How does position sizing affect risk management?",
        "What is a risk/reward ratio?",
        "What is a good risk/reward ratio for a trade?",
        "What is a good stock for me to buy right now",
    ]

    for question in test_questions:
        print(f"Q: {question}")
        print(f"A: {answer_question(question)}")
        print("-" * 40)