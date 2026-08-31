# router/app.py
from fastapi import FastAPI
import os
import httpx

app = FastAPI(title="Mock Semantic Router")
EMBEDDING_URL = os.getenv("EMBEDDING_SERVICE_URL", "http://embedding-service")

@app.post("/orchestrate")
async def orchestrate(payload: dict):
    user_query = payload.get("query", "")
    
    # Forward to internal embedding service
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{EMBEDDING_URL}/embed", json={"text": user_query})
        embedding_data = response.json()
        
    return {
        "status": "success",
        "route": "finance_knowledge_base",
        "vector_dimensions": len(embedding_data.get("embedding", [])),
        "received_embedding": embedding_data
    }