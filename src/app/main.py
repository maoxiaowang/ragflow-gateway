from fastapi import FastAPI

from app.api.v1 import v1_router
from app.core.exception_handlers import register_exception_handlers
from app.core.lifespan import lifespan
from app.core.logging import setup_logging

# Setup logging
setup_logging()

# Initialize app
app = FastAPI(title="RAGFlow Gateway", lifespan=lifespan)

# Exception handlers
register_exception_handlers(app)

# Routes
app.include_router(v1_router)
