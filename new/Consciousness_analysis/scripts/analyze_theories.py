#!/usr/bin/env python3
"""
GPT-5 Theory Analysis Script - Updated to remove full-paper extraction
Analyzes scientific papers against consciousness phenomena framework
Directly uses the theory prompt with file_search access to the PDF
"""

import os, sys, glob, time, json, logging, hashlib
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from openai import OpenAI
from httpx import ReadTimeout, ConnectTimeout, HTTPError

# ================================
# Configuration and Setup
# ================================

# Get the project root directory (parent of scripts folder)
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    handlers=[
        logging.FileHandler(PROJECT_ROOT / 'theory_analysis.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
log = logging.getLogger("theory_analyzer")

# Load environment variables
ENV_PATH = PROJECT_ROOT / 'config' / '.env'
if ENV_PATH.exists():
    load_dotenv(ENV_PATH)
    log.info(f"Loaded .env from: {ENV_PATH}")
else:
    log.error(f".env file not found at: {ENV_PATH}")
    sys.exit(1)

# Verify API key exists
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    log.error("OPENAI_API_KEY not found in environment after loading .env")
    sys.exit(1)

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY, timeout=380.0)

# Directory paths
PROMPTS_DIR = PROJECT_ROOT / "prompts"
PAPERS_DIR = PROJECT_ROOT / "papers"
OUTPUT_DIR = PROJECT_ROOT / "output" / "analysis_results"
PROCESSED_LOG = OUTPUT_DIR / "processed_papers.json"

# Create output directory if it doesn't exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Model configuration
MODEL = "gpt-5"


# ================================
# Processing History Management
# ================================

def load_processed_papers() -> Dict:
    """Load the record of processed papers"""
    if PROCESSED_LOG.exists():
        try:
            with open(PROCESSED_LOG, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_processed_paper(pdf_path: Path, output_file: str, paper_title: str):
    """Save record that a paper has been processed"""
    processed = load_processed_papers()

    # Create hash of PDF file for unique identification
    with open(pdf_path, 'rb') as f:
        file_hash = hashlib.md5(f.read()).hexdigest()

    processed[pdf_path.name] = {
        'file_hash': file_hash,
        'processed_at': datetime.now().isoformat(),
        'output_file': output_file,
        'paper_title': paper_title
    }

    with open(PROCESSED_LOG, 'w') as f:
        json.dump(processed, f, indent=2)


def is_already_processed(pdf_path: Path) -> bool:
    """Check if a PDF has already been processed"""
    processed = load_processed_papers()

    if pdf_path.name not in processed:
        return False

    # Check if file hash matches (in case file was updated)
    with open(pdf_path, 'rb') as f:
        current_hash = hashlib.md5(f.read()).hexdigest()

    stored_hash = processed[pdf_path.name].get('file_hash')

    if current_hash != stored_hash:
        log.info(f"File {pdf_path.name} has been modified since last processing")
        return False

    # Check if output file still exists
    output_file = processed[pdf_path.name].get('output_file')
    if output_file and (OUTPUT_DIR / output_file).exists():
        log.info(f"Paper {pdf_path.name} already processed as {output_file}")
        return True

    return False


# ================================
# Utility Functions
# ================================

def read_file(filepath: Path) -> str:
    """Read content from a file with error handling"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        log.info(f"Successfully read {filepath.name}")
        return content
    except FileNotFoundError:
        log.error(f"File not found: {filepath}")
        raise
    except Exception as e:
        log.error(f"Error reading {filepath}: {e}")
        raise


def save_json(data: Dict, filename: str) -> Path:
    """Save JSON data to output directory"""
    output_path = OUTPUT_DIR / filename
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        log.info(f"Results saved to {output_path}")
        return output_path
    except Exception as e:
        log.error(f"Error saving results: {e}")
        raise


def sanitize_filename(title: str) -> str:
    """Convert paper title to valid filename"""
    # Remove or replace invalid filename characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        title = title.replace(char, '')

    # Replace spaces with underscores and limit length
    title = title.replace(' ', '_').replace(',', '').replace('.', '')
    title = title[:100]  # Limit filename length

    return title


def _size_mb(p: Path) -> float:
    """Get file size in MB"""
    try:
        return p.stat().st_size / (1024 * 1024)
    except FileNotFoundError:
        return -1.0


# ================================
# API wrappers and helpers
# ================================

# Retry configuration
retryable = retry(
    stop=stop_after_attempt(4),
    wait=wait_exponential(multiplier=1.8, min=2, max=60),
    retry=retry_if_exception_type((ReadTimeout, ConnectTimeout, HTTPError, TimeoutError)),
    reraise=True,
)


@retryable
def upload_file(pdf: Path):
    """Upload PDF file"""
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
    """Add file to vector store"""
    t0 = time.time()
    client.vector_stores.files.create(vector_store_id=vector_store_id, file_id=file_id)
    log.info(f"[VS-ADD] file_id={file_id} -> vs={vector_store_id} | {time.time() - t0:.2f}s")


@retryable
def analyze_with_store(vector_store_id: str, theory_prompt: str) -> Dict:
    """
    Analyze the paper against consciousness phenomena using only the theory prompt.
    The model retrieves from the vector store as needed. No full-paper extraction.
    """
    t0 = time.time()
    log.info(f"[ANALYZE] starting with file_search access")

    # Mirror the working pattern: no response_format argument
    resp = client.responses.create(
        model=MODEL,
        input=theory_prompt,
        tools=[{"type": "file_search", "vector_store_ids": [vector_store_id]}],
        # include=["output[*].file_search_call.search_results"]  # optional debugging
    )

    response_text = getattr(resp, "output_text", "") or ""
    log.info(f"[ANALYZE] done | {time.time() - t0:.2f}s")

    # Try to parse JSON. If it is not valid JSON, return a stub.
    try:
        result = json.loads(response_text)
        return result
    except json.JSONDecodeError as e:
        log.error(f"Failed to parse JSON response: {e}")
        log.debug(f"Raw response: {response_text[:500]}...")
        return {
            "error": "Failed to parse response",
            "raw_response": response_text[:1000]
        }


# ================================
# Main Analysis Function
# ================================

def analyze_paper_from_pdf(pdf_path: Path, model: str = "gpt-5") -> Dict:
    """
    Main function to analyze a PDF paper against consciousness theories.
    Uses theory_analysis.txt directly with file_search access to the PDF.
    """
    log.info(f"\n{'=' * 60}")
    log.info(f"Starting analysis of: {pdf_path.name}")
    log.info(f"{'=' * 60}")

    # Check if already processed
    if is_already_processed(pdf_path):
        log.info(f"Skipping {pdf_path.name} - already processed")
        return None

    try:
        # Step 1: Read the consciousness phenomena prompt
        theory_prompt = read_file(PROMPTS_DIR / "theory_analysis.txt")

        # Step 2: Create vector store
        vs = client.vector_stores.create(name=f"analysis_{pdf_path.stem}")
        log.info(f"[VS] created | id={vs.id}")

        # Step 3: Upload PDF
        file_obj = upload_file(pdf_path)

        # Step 4: Add file to vector store
        vs_add_file(vector_store_id=vs.id, file_id=file_obj.id)
        time.sleep(3)  # Allow indexing time

        # Step 5: Analyze against consciousness phenomena using theory prompt only
        result = analyze_with_store(
            vector_store_id=vs.id,
            theory_prompt=theory_prompt
        )

        # Add metadata
        if isinstance(result, dict):
            result['_metadata'] = {
                'analysis_timestamp': datetime.now().isoformat(),
                'model_used': model,
                'pdf_filename': pdf_path.name,
                'vector_store_id': vs.id,
                'file_id': file_obj.id,
                'content_length': None  # no full extraction performed
            }

            # Step 6: Save results using paper title if present, else fallback to stem
            paper_title = result.get('paper_metadata', {}).get('title', pdf_path.stem)
            safe_title = sanitize_filename(paper_title)
            output_filename = f"{safe_title}.json"
            output_path = save_json(result, output_filename)

            # Step 7: Log this paper as processed
            save_processed_paper(pdf_path, output_filename, paper_title)

            # Step 8: Print summary to console
            print_analysis_summary(result)

        # Optional cleanup would go here
        return result

    except (ReadTimeout, ConnectTimeout) as e:
        log.warning(f"[TIMEOUT] {pdf_path.name} | {e}")
        return None
    except KeyboardInterrupt:
        log.error("Interrupted by user (SIGINT). Exiting gracefully.")
        raise
    except Exception as e:
        log.exception(f"[ERROR] {pdf_path.name} failed")
        return None


# ================================
# Output Display Functions
# ================================

def print_analysis_summary(result: Dict):
    """Print a comprehensive summary of the analysis to console"""
    if not result:
        return

    print("\n" + "=" * 80)
    print("CONSCIOUSNESS PHENOMENA ANALYSIS RESULTS")
    print("=" * 80)

    # Check for errors first
    if 'error' in result:
        print(f"\n⚠️  ERROR: {result.get('error')}")
        if 'raw_response' in result:
            print(f"Raw response preview: {result.get('raw_response')[:200]}...")
        return

    # Paper metadata
    metadata = result.get('paper_metadata', {})
    print(f"\n📄 Paper Title: {metadata.get('title', 'Unknown')}")
    print(f"👥 Authors: {', '.join(metadata.get('authors', ['Unknown']))[:100]}...")
    print(f"📅 Year: {metadata.get('year', 'N/A')}")
    print(f"🔗 DOI/ArXiv: {metadata.get('doi_or_arxiv', 'N/A')}")
    print(f"🔬 Domain: {metadata.get('domain', 'N/A')}")

    # Evidence summary
    evidence_items = result.get('evidence', [])
    print(f"\n📊 Total Evidence Items Found: {len(evidence_items)}")

    if evidence_items:
        print("\n" + "-" * 80)
        print("EVIDENCE BY PHENOMENON:")
        print("-" * 80)

        # Group evidence by phenomenon
        phenomena_evidence = {}
        for item in evidence_items:
            phenomenon_id = item.get('phenomenon_id', 'unknown')
            if phenomenon_id not in phenomena_evidence:
                phenomena_evidence[phenomenon_id] = []
            phenomena_evidence[phenomenon_id].append(item)

        for phenomenon_id, items in phenomena_evidence.items():
            print(f"\n🧠 {phenomenon_id.upper().replace('_', ' ')}")
            print(f"   Found {len(items)} piece(s) of evidence")

            for i, item in enumerate(items, 1):
                print(f"\n   Evidence #{i}:")
                print(f"   - System: {item.get('system_type', 'N/A')}")
                print(f"   - Species/Model: {item.get('species_or_model', 'N/A')}")
                print(f"   - Mechanism: {item.get('brief_mechanism', 'N/A')[:100]}...")
                print(f"   - Method: {item.get('method', 'N/A')}")
                print(f"   - State: {item.get('state', 'N/A')}")

                # Show first quote if available
                text_refs = item.get('text_refs', [])
                if text_refs and len(text_refs) > 0:
                    first_quote = text_refs[0]
                    quote_preview = first_quote.get('quote', '')[:150]
                    if len(first_quote.get('quote', '')) > 150:
                        quote_preview += "..."
                    print(f"   - Quote: \"{quote_preview}\"")
                    print(f"   - Section: {first_quote.get('section_title', 'N/A')}")

                # Note figures and tables
                figure_refs = item.get('figure_refs', [])
                table_refs = item.get('table_refs', [])
                if figure_refs:
                    figures = [f.get('figure_label', '') for f in figure_refs]
                    print(f"   - Figures: {', '.join(figures)}")
                if table_refs:
                    tables = [t.get('table_label', '') for t in table_refs]
                    print(f"   - Tables: {', '.join(tables)}")

    # Metadata
    analysis_meta = result.get('_metadata', {})
    print("\n" + "-" * 80)
    print("ANALYSIS METADATA:")
    print(f"- Timestamp: {analysis_meta.get('analysis_timestamp', 'N/A')}")
    print(f"- Model Used: {analysis_meta.get('model_used', 'N/A')}")
    print(f"- PDF File: {analysis_meta.get('pdf_filename', 'N/A')}")
    print(f"- Content Length: {analysis_meta.get('content_length', 'N/A')}")

    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80 + "\n")


# ================================
# Main Entry Point
# ================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Analyze papers using GPT-5")
    parser.add_argument(
        '--model',
        choices=['gpt-5', 'gpt-5-mini', 'gpt-5-nano'],
        default='gpt-5',
        help='GPT-5 model variant to use (default: gpt-5)'
    )
    parser.add_argument(
        '--pdf',
        type=str,
        help='Specific PDF file to process (optional, otherwise processes all)'
    )
    parser.add_argument(
        '--reprocess',
        action='store_true',
        help='Reprocess papers even if already analyzed'
    )

    args = parser.parse_args()

    # Clear processed log if reprocessing
    if args.reprocess and PROCESSED_LOG.exists():
        PROCESSED_LOG.unlink()
        print("Cleared processing history for reprocessing")

    if args.pdf:
        # Process specific PDF
        pdf_path = PAPERS_DIR / args.pdf
        if not pdf_path.exists():
            print(f"Error: PDF file not found: {pdf_path}")
            sys.exit(1)

        print(f"Processing single PDF: {args.pdf}")
        result = analyze_paper_from_pdf(pdf_path, model=args.model)

        if result:
            print("✅ Analysis completed successfully!")
        else:
            print("❌ Analysis failed or paper already processed")
    else:
        # Process all PDFs in papers directory
        pdf_files = list(PAPERS_DIR.glob("*.pdf"))

        if not pdf_files:
            print(f"No PDF files found in {PAPERS_DIR}")
            sys.exit(0)

        print(f"Found {len(pdf_files)} PDF file(s) to process")

        successful = 0
        skipped = 0
        failed = 0

        for pdf_path in pdf_files:
            result = analyze_paper_from_pdf(pdf_path, model=args.model)

            if result is None:
                if is_already_processed(pdf_path):
                    skipped += 1
                else:
                    failed += 1
            else:
                successful += 1

        # Final summary
        print("\n" + "=" * 80)
        print("BATCH PROCESSING SUMMARY")
        print("=" * 80)
        print(f"✅ Successfully processed: {successful}")
        print(f"⏭️  Skipped (already processed): {skipped}")
        print(f"❌ Failed: {failed}")
        print(f"📊 Total: {len(pdf_files)}")
        print("=" * 80)
