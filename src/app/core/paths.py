import os
from pathlib import Path

# 项目根目录（ragflow-gateway/）
ROOT_DIR = Path(__file__).resolve().parents[3]

# 常用路径集中管理
SRC_DIR = ROOT_DIR / "src"
APP_DIR = SRC_DIR / "app"
DEFAULT_CONFIG_DIR = ROOT_DIR / "configs"
DEFAULT_UPLOAD_DIR = ROOT_DIR / "uploads"
DEFAULT_LOG_DIR = ROOT_DIR / "logs"
