import ollama

def ask_model(prompt: str, model: str = "llama3.2:1b") -> str:
    try:
        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}],
        )
        return response["message"]["content"]
    except ConnectionError:
        return (
            "I couldn’t reach the local Ollama model. Please make sure Ollama is "
            "installed and running, then try again."
        )
    except Exception:
        return (
            f"The model '{model}' is unavailable or returned an unexpected response. "
            "Please check that the model is installed in Ollama and try again."
        )

if __name__ == "__main__":
    print(ask_model("What is a stop-loss in trading?"))