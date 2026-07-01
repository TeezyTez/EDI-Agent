from pathlib import Path

from dotenv import load_dotenv
import os


load_dotenv()


PROJECT_DIR = Path(__file__).resolve().parents[1]
WORKSPACE_DIR = PROJECT_DIR / os.getenv("WORKSPACE_DIR", "workspace")
UPLOAD_DIR = WORKSPACE_DIR / "uploads"
GENERATED_DIR = WORKSPACE_DIR / "generated"
REPORT_DIR = WORKSPACE_DIR / "reports"
TEST_DIR = WORKSPACE_DIR / "tests"
KNOWLEDGE_DIR = WORKSPACE_DIR / "knowledge"

CONFIDENCE_AUTO_CONFIRM = float(os.getenv("CONFIDENCE_AUTO_CONFIRM", "0.90"))
CONFIDENCE_NEED_REVIEW = float(os.getenv("CONFIDENCE_NEED_REVIEW", "0.70"))
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
MIMO_API_KEY = os.getenv("MIMO_API_KEY", "")
MIMO_BASE_URL = os.getenv("MIMO_BASE_URL", "")
MIMO_MODEL = os.getenv("MIMO_MODEL", "mimo-vl")
MIMO_PDF_MAX_PAGES = int(os.getenv("MIMO_PDF_MAX_PAGES", "14"))
LLM_CANDIDATE_LIMIT = int(os.getenv("LLM_CANDIDATE_LIMIT", "8"))
LLM_KNOWLEDGE_CHUNK_CHARS = int(os.getenv("LLM_KNOWLEDGE_CHUNK_CHARS", "12000"))


def ensure_workspace() -> None:
    """Create runtime folders used by uploads, generated code, tests, and reports."""
    for folder in (UPLOAD_DIR, GENERATED_DIR, REPORT_DIR, TEST_DIR, KNOWLEDGE_DIR):
        folder.mkdir(parents=True, exist_ok=True)
