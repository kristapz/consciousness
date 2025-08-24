#!/usr/bin/env python3
"""
GPT-5 Theory Analysis Script
Analyzes scientific papers against 50 consciousness-related claims
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import sys

from openai import OpenAI
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential

# ================================
# Configuration and Setup
# ================================

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('theory_analysis.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Get the project root directory (parent of scripts folder)
PROJECT_ROOT = Path(__file__).parent.parent.absolute()

# Load environment variables
env_path = PROJECT_ROOT / 'config' / '.env'
if env_path.exists():
    load_dotenv(env_path)
    logging.info(f"Loaded .env from: {env_path}")
else:
    logging.error(f".env file not found at: {env_path}")
    sys.exit(1)

# Verify API key exists
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    logging.error("OPENAI_API_KEY not found in environment after loading .env")
    logging.error(f"Please check the .env file at: {env_path}")
    sys.exit(1)

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Directory paths - now absolute based on project root
PROMPTS_DIR = PROJECT_ROOT / "prompts"
OUTPUT_DIR = PROJECT_ROOT / "output" / "analysis_results"

# Create output directory if it doesn't exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ================================
# Utility Functions
# ================================

def read_file(filepath: Path) -> str:
    """Read content from a file with error handling"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        logging.info(f"Successfully read {filepath.name}")
        return content
    except FileNotFoundError:
        logging.error(f"File not found: {filepath}")
        raise
    except Exception as e:
        logging.error(f"Error reading {filepath}: {e}")
        raise


def save_json(data: Dict, filename: str) -> Path:
    """Save JSON data to output directory"""
    output_path = OUTPUT_DIR / filename
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logging.info(f"Results saved to {output_path}")
        return output_path
    except Exception as e:
        logging.error(f"Error saving results: {e}")
        raise


def generate_output_filename(link: str) -> str:
    """Generate a unique filename based on timestamp and link"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Extract a clean identifier from the link
    link_id = link.split('/')[-1][:30] if link else "unknown"
    link_id = ''.join(c for c in link_id if c.isalnum() or c in '-_')
    return f"analysis_{timestamp}_{link_id}.json"


# ================================
# GPT-5 API Interaction
# ================================

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=2, min=10, max=120)  # Longer waits for rate limits
)
def call_gpt5(prompt: str, model: str = "gpt-5") -> Dict:
    """
    Call GPT-5 API with retry logic

    Args:
        prompt: The combined prompt with paper content
        model: GPT-5 model variant (gpt-5, gpt-5-mini, gpt-5-nano)

    Returns:
        Parsed JSON response from GPT-5
    """
    logging.info(f"Calling GPT-5 API with model: {model}")

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a scientific analyzer specializing in consciousness research. Always respond with valid JSON matching the specified format."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            # temperature=1.0 is the default and only supported value for GPT-5
            response_format={"type": "json_object"}  # Force JSON output
            # Note: reasoning_effort and verbosity parameters may not be available yet
        )

        # Extract and parse the response
        response_text = response.choices[0].message.content
        logging.info(f"Received response from GPT-5 (tokens used: {response.usage.total_tokens})")

        # Parse JSON response
        try:
            result = json.loads(response_text)
            return result
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse JSON response: {e}")
            logging.debug(f"Raw response: {response_text[:500]}...")
            raise

    except Exception as e:
        if "429" in str(e):
            logging.warning("Rate limit hit. Waiting before retry...")
        logging.error(f"GPT-5 API call failed: {e}")
        raise


# ================================
# Main Analysis Function
# ================================

def analyze_paper_theories(model: str = "gpt-5") -> Dict:
    """
    Main function to analyze a paper against consciousness theories

    Args:
        model: GPT-5 model variant to use

    Returns:
        Analysis results dictionary
    """
    logging.info("Starting paper analysis...")

    # Read input files
    try:
        theory_prompt = read_file(PROMPTS_DIR / "theory_analysis.txt")
        paper_content = read_file(PROMPTS_DIR / "article.txt")
        paper_link = read_file(PROMPTS_DIR / "link.txt")
    except Exception as e:
        logging.error(f"Failed to read input files: {e}")
        return None

    # Validate inputs
    if not paper_content:
        logging.error("Paper content is empty")
        return None

    # Combine prompt with paper content and link
    full_prompt = f"""{theory_prompt}

PAPER CONTENT:
{paper_content}

PAPER LINK: {paper_link}"""

    # Log prompt size for monitoring
    prompt_tokens = len(full_prompt.split())
    logging.info(f"Prompt size: ~{prompt_tokens} words")

    # Call GPT-5
    try:
        result = call_gpt5(full_prompt, model)

        # Add metadata
        result['_metadata'] = {
            'analysis_timestamp': datetime.now().isoformat(),
            'model_used': model,
            'paper_link': paper_link,
            'prompt_tokens_estimate': prompt_tokens
        }

        # Save results
        output_filename = generate_output_filename(paper_link)
        output_path = save_json(result, output_filename)

        # Log summary
        logging.info("Analysis complete!")
        logging.info(f"Theory synthesis: {result.get('theory_synthesis', 'N/A')}")
        logging.info(f"Supported claims: {result.get('supported_claims', [])}")
        logging.info(f"Number of evidence details: {len(result.get('evidence_details', {}))}")

        return result

    except Exception as e:
        logging.error(f"Analysis failed: {e}")
        return None


# ================================
# Command Line Interface
# ================================

def print_summary(result: Dict):
    """Print a human-readable summary of the analysis"""
    if not result:
        return

    print("\n" + "=" * 60)
    print("ANALYSIS SUMMARY")
    print("=" * 60)

    # Paper metadata
    metadata = result.get('paper_metadata', {})
    print(f"\nPaper: {metadata.get('title', 'Unknown')}")
    print(f"Link: {metadata.get('link', 'N/A')}")

    # Theory synthesis
    print(f"\nTheory Synthesis:")
    print(f"  {result.get('theory_synthesis', 'N/A')}")

    # Supported claims
    supported = result.get('supported_claims', [])
    print(f"\nSupported Claims ({len(supported)} total): {', '.join(map(str, supported))}")

    # Evidence summary
    evidence = result.get('evidence_details', {})
    print(f"\nEvidence Details:")
    for claim_num, details in evidence.items():
        print(f"\n  Claim {claim_num}: {details.get('claim_text', '')[:80]}...")
        print(f"    Strength: {details.get('strength', 'N/A')}")
        print(f"    Quotes: {len(details.get('direct_quotes', []))} found")

    # Additional insights
    insights = result.get('additional_or_contradictory_insights', [])
    if insights:
        print(f"\nAdditional Insights: {len(insights)} found")

    print("\n" + "=" * 60)


# ================================
# Entry Point
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
        '--summary',
        action='store_true',
        help='Print summary to console'
    )

    args = parser.parse_args()

    # Run analysis
    print(f"Starting analysis with {args.model}...")
    result = analyze_paper_theories(model=args.model)

    if result:
        print("Analysis completed successfully!")
        if args.summary:
            print_summary(result)
    else:
        print("Analysis failed. Check the logs for details.")
        sys.exit(1)