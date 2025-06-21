# Handles LLM querying using LangChain, Gemini API, vector retrieval,and logs metrics + query logs via internal/external services.

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os, time, uuid, traceback

from rag_module.rag_chain import get_vectorstore, create_chain_from_retriever
from rag_module.metrics_client import send_metrics
from aws_service.query_log_handler import log_query


# Rate limiting
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

# App setup
limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#Custom limit
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})

@app.post("/query")
@limiter.limit("10/minute")
async def query(request: Request):
    # Accepts a question + file key
    try:
        data = await request.json()
        question = data.get("query", "").strip()
        file_id = data.get("file_key")


        if not question:
            raise HTTPException(status_code=400, detail="Empty query.")

        # Access vectorstore
        vectorstore = get_vectorstore()
        # Retriever
        retriever = vectorstore.as_retriever()
        # Create ragchain 
        chain = create_chain_from_retriever(retriever)

        run_id = str(uuid.uuid4())
        start = time.time()
        result = chain.invoke(question)
        latency = time.time() - start

        # Send metrices to dynamodb
        send_metrics(
            run_id=run_id,
            tokens_used=345,
            confidence=0.92,
            response_time=latency,
            file_id=file_id
        )
        # Log the full query and response
        log_query(
            run_id=run_id,
            query_text=question,
            response_text=result,
            confidence_score=0.92,
            file_id=file_id
        )


        return {"run_id": run_id, "reply": result}

    except HTTPException as he:
        raise he
    except Exception as e:
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e)})
