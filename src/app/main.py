from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.api.v1 import v1_router
from app.core.exception_handlers import register_exception_handlers
from app.core.lifespan import lifespan
from app.core.logging import setup_logging

# Setup logging
setup_logging()

# Initialize app
app = FastAPI(title="RAGFlow Gateway", lifespan=lifespan)

origins = [
    "http://localhost:5173",  # 前端地址
    # "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
register_exception_handlers(app)

# Routes
app.include_router(v1_router)
