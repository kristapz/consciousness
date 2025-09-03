#!/usr/bin/env python3
import os, sys, glob, time, json, logging
from pathlib import Path
from typing import List, Dict, Optional
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from openai import OpenAI
from httpx import ReadTimeout, ConnectTimeout, HTTPError

# ----------------------------
# Config
# ----------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = PROJECT_ROOT / "config" / ".env"
PAPERS_DIR = PROJECT_ROOT / "papers"  # /Users/.../Consciousness_analysis/papers
OUTPUT_JSON = PROJECT_ROOT / "output" / "analysis_results" / "summaries.json"
OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)

MODEL = "gpt-5"
OPENAI_DEFAULT_TIMEOUT = 120.0  # seconds for connect+read

SUMMARY_PROMPT = (
    "You are an expert scientific summarizer. Read the attached paper via retrieval and "
    "Explain figure 1 in detail. Each part of it"
)

# ----------------------------
# Logging
# ----------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
log = logging.getLogger("summary")

# ----------------------------
# Env & client
# ----------------------------
if ENV_PATH.exists():
    load_dotenv(ENV_PATH)
    log.info(f"Loaded .env from {ENV_PATH}")
else:
    log.error(f".env not found at {ENV_PATH}")
    sys.exit(1)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    log.error("OPENAI_API_KEY missing after loading .env")
    sys.exit(1)

# Set client with global timeout
client = OpenAI(api_key=OPENAI_API_KEY, timeout=OPENAI_DEFAULT_TIMEOUT)

# ----------------------------
# Helpers
# ----------------------------
def list_pdfs(folder: Path) -> List[Path]:
    return [Path(p) for p in glob.glob(str(folder / "*.pdf"))]

def _size_mb(p: Path) -> float:
    try:
        return p.stat().st_size / (1024 * 1024)
    except FileNotFoundError:
        return -1.0

# ----------------------------
# API wrappers with retries
# ----------------------------
retryable = retry(
    stop=stop_after_attempt(4),
    wait=wait_exponential(multiplier=1.8, min=2, max=60),
    retry=retry_if_exception_type((ReadTimeout, ConnectTimeout, HTTPError, TimeoutError)),
    reraise=True,
)

@retryable
def upload_file(pdf: Path):
    t0 = time.time()
    size_mb = _size_mb(pdf)
    log.info(f"[UPLOAD] {pdf.name} | size={size_mb:.2f} MB")
    with open(pdf, "rb") as fh:
        f = client.files.create(file=fh, purpose="assistants")
    dt = time.time() - t0
    log.info(f"[UPLOAD] {pdf.name} | file_id={f.id} | {dt:.2f}s")
    return f

@retryable
def vs_add_file(vector_store_id: str, file_id: str):
    t0 = time.time()
    client.vector_stores.files.create(vector_store_id=vector_store_id, file_id=file_id)
    log.info(f"[VS-ADD] file_id={file_id} -> vs={vector_store_id} | {time.time()-t0:.2f}s")

@retryable
def summarize_with_store(vector_store_id: str, filename: str) -> str:
    t0 = time.time()
    log.info(f"[SUMMARIZE] starting | file={filename}")
    resp = client.responses.create(
        model=MODEL,
        input=SUMMARY_PROMPT + f"\n\nFocus only on: {filename}",
        tools=[{"type": "file_search", "vector_store_ids": [vector_store_id]}],
        # include retrievals if you want to debug which chunks were used:
        # include=["output[*].file_search_call.search_results"]
    )
    text = getattr(resp, "output_text", "") or ""
    log.info(f"[SUMMARIZE] done | file={filename} | {time.time()-t0:.2f}s")
    return text.strip()

# ----------------------------
# Main
# ----------------------------
def main():
    log.info(f"PAPERS_DIR={PAPERS_DIR}")
    pdfs = list_pdfs(PAPERS_DIR)
    log.info(f"Found {len(pdfs)} PDF(s) in {PAPERS_DIR}")

    if not pdfs:
        return

    # One vector store for all PDFs reduces overhead
    vs = client.vector_stores.create(name="consciousness_papers_vs")
    log.info(f"[VS] created | id={vs.id}")

    results: List[Dict] = []

    for pdf in pdfs:
        try:
            # Upload with retries and timeouts
            file_obj = upload_file(pdf)

            # Attach to the shared vector store
            vs_add_file(vector_store_id=vs.id, file_id=file_obj.id)

            # Summarize (explicit focus hint on filename)
            summary = summarize_with_store(vector_store_id=vs.id, filename=pdf.name)

            results.append({
                "filename": pdf.name,
                "file_id": file_obj.id,
                "vector_store_id": vs.id,
                "size_mb": round(_size_mb(pdf), 2),
                "summary": summary
            })

            # Console output
            print("\n" + "-" * 60)
            print(f"Summary for {pdf.name}:\n{summary}\n")

        except (ReadTimeout, ConnectTimeout) as e:
            log.warning(f"[TIMEOUT] {pdf.name} | {e}")
            results.append({
                "filename": pdf.name,
                "error": "timeout",
                "detail": str(e)
            })
        except KeyboardInterrupt:
            log.error("Interrupted by user (SIGINT). Exiting gracefully.")
            break
        except Exception as e:
            log.exception(f"[ERROR] {pdf.name} failed")
            results.append({
                "filename": pdf.name,
                "error": "exception",
                "detail": str(e)
            })

    # Persist summaries
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    log.info(f"Wrote {len(results)} records -> {OUTPUT_JSON}")

if __name__ == "__main__":
    main()
