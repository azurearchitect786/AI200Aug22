# embedding/app.py
from fastapi import FastAPI
import random

app = FastAPI(title="Mock Embedding Engine")

@app.post("/embed")
async def embed(payload: dict):
    text = payload.get("text", "")
    # Mocking a 384-dimensional vector (e.g., MiniLM-L6-v2 size)
    mock_vector = [round(random.uniform(-1.0, 1.0), 6) for _ in range(384)]
    return {
        "model": "mock-bge-large-v1.5",
        "input_length": len(text),
        "embedding": mock_vector
    }