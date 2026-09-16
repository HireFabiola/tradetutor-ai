import ollama

def ask_model(prompt: str, model: str = "llama3.2:1b") -> str:
    response = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    return response["message"]["content"]

# Practice: call ask_model() with a hardcoded question and print the result
if __name__ == "__main__":
    print(ask_model("What is a stop-loss in trading?"))