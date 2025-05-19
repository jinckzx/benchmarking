from pathlib import Path

# Resolve base project directory (benchmarking_tool/)
BASE_DIR = Path(__file__).resolve().parents[2]

# Define the relative path to the database
DB_ROOT_PATH = BASE_DIR / "dataset" / "spider_data" / "spider_data" / "database"