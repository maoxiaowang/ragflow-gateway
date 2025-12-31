import os
from logging.config import dictConfig
from logging.handlers import TimedRotatingFileHandler

from app.core.settings import settings

os.makedirs(settings.log_dir, exist_ok=True)

LOG_FORMAT = "[%(asctime)s] [%(levelname)s] [%(name)s] [%(filename)s:%(lineno)d] - %(message)s"


def setup_logging():
    dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {"format": LOG_FORMAT},
        },
        "handlers": {
            "console_info": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "level": "INFO",
                "stream": "ext://sys.stdout"
            },
            "console_error": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "level": "WARNING",
                "stream": "ext://sys.stderr"
            },
            "file_info": {
                "()": TimedRotatingFileHandler,
                "formatter": "default",
                "filename": os.path.join(settings.log_dir, f"app-{settings.env}.log"),
                "when": "midnight",
                "backupCount": 7,
                "encoding": "utf-8",
                "level": "INFO"
            },
            "file_error": {
                "()": TimedRotatingFileHandler,
                "formatter": "default",
                "filename": os.path.join(settings.log_dir, f"error-{settings.env}.log"),
                "when": "midnight",
                "backupCount": 7,
                "encoding": "utf-8",
                "level": "WARNING"
            },
        },
        "loggers": {
            "app": {
                "handlers": ["console_info", "console_error", "file_info", "file_error"],
                "level": "INFO",
                "propagate": False
            },
            "uvicorn": {
                "handlers": ["console_info", "console_error"],
                "level": "INFO",
                "propagate": False
            },
            "uvicorn.error": {
                "handlers": ["console_info", "console_error"],
                "level": "INFO",
                "propagate": False
            },
            "uvicorn.access": {
                "handlers": ["console_info"],
                "level": "INFO",
                "propagate": False
            },
        },
        "root": {
            "handlers": ["console_info", "console_error", "file_info", "file_error"],
            "level": "WARNING"
        }
    })