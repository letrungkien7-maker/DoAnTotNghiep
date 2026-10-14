import os
import sys

# Ensure backend directory is in sys.path
backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.scripts.seed_demo_data import seed_database

if __name__ == "__main__":
    seed_database()
