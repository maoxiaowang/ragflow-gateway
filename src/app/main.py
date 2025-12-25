from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.api.v1 import v1_router
from app.core.exception_handlers import register_exception_handlers
from app.core.lifespan import lifespan
from app.core.logging import setup_logging
from app.core.settings import settings

# Setup logging
setup_logging()

# Initialize app
app = FastAPI(title="RAGFlow Gateway", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        str(o).rstrip("/")
        for o in settings.cors_origins
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
register_exception_handlers(app)

# Routes
app.include_router(v1_router)
