import os
import tempfile
from pathlib import Path


# Configure writable, isolated runtime paths before application modules are imported.
TEST_ROOT = Path(tempfile.gettempdir()) / "repo-study-ai-tests"
TEST_ROOT.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("DATABASE_URL", f"sqlite:///{(TEST_ROOT / 'test.db').as_posix()}")
os.environ.setdefault("DATA_DIR", str(TEST_ROOT / "data"))
os.environ.setdefault("REPOS_DIR", str(TEST_ROOT / "repos"))
os.environ.setdefault("VECTOR_STORE_DIR", str(TEST_ROOT / "vector_store"))
