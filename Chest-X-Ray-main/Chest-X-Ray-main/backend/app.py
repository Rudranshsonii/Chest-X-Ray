from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from routes import router, initialize_model

from fastapi import FastAPI
from contextlib import asynccontextmanager

import logging

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application initialization...")
    await initialize_model()
    logger.info("Model initialized successfully")
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(router)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.middleware("http")
async def agent_context_middleware(request: Request, call_next):
    response = await call_next(request)
    return response

@app.get("/heartbeat")
async def heartbeat():
    return JSONResponse({"status": "ok", "version": "1.0.0"})