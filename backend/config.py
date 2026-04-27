import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Data directories
UPLOAD_DIR = os.path.join(BASE_DIR, "data", "uploads")
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "outputs")
CHARTS_DIR = os.path.join(OUTPUT_DIR, "charts")
MODELS_DIR = os.path.join(BASE_DIR, "backend", "models_store")

# Ensure directories exist
for _dir in [UPLOAD_DIR, OUTPUT_DIR, CHARTS_DIR, MODELS_DIR]:
    os.makedirs(_dir, exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {"csv", "xlsx", "xls"}

# SQLite database path
DATABASE_PATH = os.path.join(BASE_DIR, "insightforge.db")

# Max file size: 50 MB
MAX_CONTENT_LENGTH = 50 * 1024 * 1024

# Preview row count
PREVIEW_ROWS = 10
