#!/usr/bin/env python3
"""
Theory Update Script - Iterative Consciousness Theory Refinement
Updates a cumulative theory based on new paper evidence
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
        logging.FileHandler('theory_update.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Get the project root directory
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
    logging.error("OPENAI_API_KEY not found in environment")
    sys.exit(1)

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Directory paths
OUTPUT_DIR = PROJECT_ROOT / "output" / "analysis_results"
THEORY_DIR = PROJECT_ROOT / "output" / "cumulative_theory"
THEORY_FILE = THEORY_DIR / "current_theory.json"

# Create directories if they don't exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
THEORY_DIR.mkdir(parents=True, exist_ok=True)


# ================================
# Utility Functions
# ================================

def load_current_theory() -> Dict:
    """Load the current cumulative theory"""
    if THEORY_FILE.exists():
        try:
            with open(THEORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Error loading current theory: {e}")
            return None
    return None


def save_theory(theory: Dict) -> None:
    """Save the updated theory"""
    # Save current version
    try:
        with open(THEORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(theory, f, indent=2, ensure_ascii=False)

        # Also save timestamped backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = THEORY_DIR / f"theory_backup_{timestamp}.json"
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(theory, f, indent=2, ensure_ascii=False)

        logging.info(f"Theory saved to {THEORY_FILE} with backup at {backup_file}")
    except Exception as e:
        logging.error(f"Error saving theory: {e}")
        raise


def load_all_analyses() -> List[Dict]:
    """Load all previous analysis results"""
    analyses = []

    if not OUTPUT_DIR.exists():
        return analyses

    json_files = sorted(OUTPUT_DIR.glob("analysis_*.json"))

    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                data['_filename'] = json_file.name
                analyses.append(data)
                logging.info(f"Loaded analysis: {json_file.name}")
        except Exception as e:
            logging.error(f"Error loading {json_file.name}: {e}")

    return analyses


def find_latest_analysis(analyses: List[Dict]) -> Optional[Dict]:
    """Find the most recent analysis that hasn't been incorporated into theory"""
    if not analyses:
        return None

    # Sort by timestamp
    sorted_analyses = sorted(
        analyses,
        key=lambda x: x.get('_metadata', {}).get('analysis_timestamp', ''),
        reverse=True
    )

    # Get current theory to check what's been incorporated
    current_theory = load_current_theory()
    if not current_theory:
        return sorted_analyses[0] if sorted_analyses else None

    incorporated_files = set(current_theory.get('incorporated_analyses', []))

    # Find first analysis not yet incorporated
    for analysis in sorted_analyses:
        if analysis.get('_filename') not in incorporated_files:
            return analysis

    return None


def summarize_analysis(analysis: Dict) -> Dict:
    """Create a concise summary of an analysis for the prompt"""
    return {
        'paper': analysis.get('paper_metadata', {}).get('title', 'Unknown'),
        'link': analysis.get('paper_metadata', {}).get('link', ''),
        'theory_synthesis': analysis.get('theory_synthesis'),
        'supported_claims': analysis.get('supported_claims', []),
        'evidence_strength': {
            claim: details.get('strength', 'unknown')
            for claim, details in analysis.get('evidence_details', {}).items()
        },
        'key_insights': [
            insight.get('finding', '')
            for insight in analysis.get('additional_or_contradictory_insights', [])[:3]
        ]
    }


# ================================
# GPT-5 Theory Update Function
# ================================

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=2, min=10, max=120)
)
def update_theory_with_gpt5(current_theory: Dict, all_analyses: List[Dict],
                            new_analysis: Dict, model: str = "gpt-5") -> Dict:
    """Call GPT-5 to update the theory based on new evidence"""

    # Create summaries of all analyses
    all_summaries = [summarize_analysis(a) for a in all_analyses]
    new_summary = summarize_analysis(new_analysis)

    # Build the prompt
    prompt = f"""You are a consciousness researcher tasked with maintaining and updating a cumulative theory of consciousness based on accumulating evidence from scientific papers.

PREVIOUS ANALYSES AND THEIR THEORIES:
{json.dumps(all_summaries, indent=2)}

CURRENT CUMULATIVE THEORY OF CONSCIOUSNESS:
{json.dumps(current_theory.get('theory', {}), indent=2) if current_theory else "No theory developed yet - this is the first analysis."}

NEW PAPER ANALYSIS:
{json.dumps(new_summary, indent=2)}

FULL EVIDENCE DETAILS FROM NEW PAPER:
{json.dumps(new_analysis.get('evidence_details', {}), indent=2)}

TASK:
Based on the new evidence, update the cumulative theory of consciousness. Consider:
1. Does the new evidence support, contradict, or extend the current theory?
2. Are there new mechanisms or principles that should be incorporated?
3. Should any aspects of the current theory be revised or rejected?
4. What is the overall confidence level in different aspects of the theory?

Respond with a JSON object in this format:
{{
    "theory": {{
        "core_principles": ["List of fundamental principles supported by evidence"],
        "mechanisms": {{
            "ion_channels": "Role and evidence summary",
            "cytoskeleton": "Role and evidence summary",
            "em_fields": "Role and evidence summary",
            "microtubules": "Role and evidence summary",
            "signaling_pathways": "Role and evidence summary",
            "perturbation_effects": "Role and evidence summary"
        }},
        "integration_framework": "How these mechanisms work together",
        "key_predictions": ["Testable predictions from the theory"],
        "confidence_levels": {{
            "high": ["Well-supported aspects"],
            "moderate": ["Aspects with some support"],
            "low": ["Speculative aspects"]
        }}
    }},
    "changes_from_previous": {{
        "additions": ["New elements added to theory"],
        "modifications": ["Elements that were modified"],
        "rejections": ["Elements removed or contradicted"],
        "strengthened": ["Elements with increased support"],
        "weakened": ["Elements with decreased support"]
    }},
    "synthesis": "A 2-3 sentence summary of the current unified theory",
    "next_research_priorities": ["Key questions that need investigation"]
}}

If the new paper doesn't add anything meaningful, indicate minimal changes but still provide the complete current theory."""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a scientific theory builder specializing in consciousness research. Respond only with valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)

        # Add metadata
        result['_metadata'] = {
            'update_timestamp': datetime.now().isoformat(),
            'model_used': model,
            'papers_incorporated': len(all_analyses),
            'latest_paper': new_analysis.get('paper_metadata', {}).get('title', 'Unknown')
        }

        # Track incorporated analyses
        incorporated = current_theory.get('incorporated_analyses', []) if current_theory else []
        incorporated.append(new_analysis.get('_filename', ''))
        result['incorporated_analyses'] = incorporated

        return result

    except Exception as e:
        logging.error(f"GPT-5 API call failed: {e}")
        raise


# ================================
# Main Update Function
# ================================

def update_cumulative_theory(model: str = "gpt-5", specific_analysis: Optional[str] = None) -> Dict:
    """Main function to update the cumulative theory"""

    logging.info("Starting theory update process...")

    # Load current theory
    current_theory = load_current_theory()

    # Load all analyses
    all_analyses = load_all_analyses()
    if not all_analyses:
        logging.error("No analyses found to process")
        return None

    # Find the analysis to process
    if specific_analysis:
        # Find specific analysis file
        new_analysis = None
        for analysis in all_analyses:
            if analysis.get('_filename') == specific_analysis:
                new_analysis = analysis
                break
        if not new_analysis:
            logging.error(f"Analysis file {specific_analysis} not found")
            return None
    else:
        # Find latest unprocessed analysis
        new_analysis = find_latest_analysis(all_analyses)
        if not new_analysis:
            logging.info("All analyses have been incorporated into the theory")
            return current_theory

    logging.info(f"Processing new analysis: {new_analysis.get('_filename')}")

    # Update theory with GPT-5
    try:
        updated_theory = update_theory_with_gpt5(
            current_theory,
            all_analyses,
            new_analysis,
            model
        )

        # Save updated theory
        save_theory(updated_theory)

        # Log summary
        logging.info("Theory update complete!")
        logging.info(f"Synthesis: {updated_theory.get('synthesis', 'N/A')}")
        changes = updated_theory.get('changes_from_previous', {})
        logging.info(f"Additions: {len(changes.get('additions', []))}")
        logging.info(f"Modifications: {len(changes.get('modifications', []))}")

        return updated_theory

    except Exception as e:
        logging.error(f"Theory update failed: {e}")
        return None


def print_theory_summary(theory: Dict):
    """Print a human-readable summary of the theory"""
    if not theory:
        return

    print("\n" + "=" * 60)
    print("CUMULATIVE CONSCIOUSNESS THEORY")
    print("=" * 60)

    # Synthesis
    print(f"\nSynthesis:\n{theory.get('synthesis', 'N/A')}")

    # Core principles
    print("\nCore Principles:")
    for i, principle in enumerate(theory.get('theory', {}).get('core_principles', []), 1):
        print(f"  {i}. {principle}")

    # Changes
    changes = theory.get('changes_from_previous', {})
    if any(changes.values()):
        print("\nRecent Changes:")
        for change_type, items in changes.items():
            if items:
                print(f"  {change_type.title()}: {len(items)} items")

    # Research priorities
    print("\nNext Research Priorities:")
    for i, priority in enumerate(theory.get('next_research_priorities', [])[:3], 1):
        print(f"  {i}. {priority}")

    print("\n" + "=" * 60)


# ================================
# Entry Point
# ================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Update cumulative consciousness theory")
    parser.add_argument(
        '--model',
        choices=['gpt-5', 'gpt-5-mini', 'gpt-5-nano'],
        default='gpt-5',
        help='GPT-5 model variant to use'
    )
    parser.add_argument(
        '--analysis',
        type=str,
        help='Specific analysis file to process (optional)'
    )
    parser.add_argument(
        '--summary',
        action='store_true',
        help='Print theory summary after update'
    )
    parser.add_argument(
        '--show-current',
        action='store_true',
        help='Just show current theory without updating'
    )

    args = parser.parse_args()

    if args.show_current:
        current = load_current_theory()
        if current:
            print_theory_summary(current)
        else:
            print("No current theory found.")
    else:
        print(f"Updating theory using {args.model}...")
        result = update_cumulative_theory(model=args.model, specific_analysis=args.analysis)

        if result:
            print("Theory update completed successfully!")
            if args.summary:
                print_theory_summary(result)
        else:
            print("Theory update failed. Check the logs for details.")
            sys.exit(1)