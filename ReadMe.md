# 🧠 Consciousness Theory Analysis Tool

A sophisticated Python framework for analyzing scientific papers against **50 core consciousness-related claims** using GPT-5. This tool automates evidence extraction, evaluates theoretical support, and provides an interactive web interface for exploring results.

## 🚀 Quick Start

```bash
# 1. Setup
git clone <repository-url>
cd Consciousness_analysis
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
echo "OPENAI_API_KEY=your-key-here" > config/.env

# 2. Analyze a paper
# Add paper content to prompts/article.txt and URL to prompts/link.txt
python scripts/analyze_theories.py

# 3. View results
python scripts/analysis_viewer.py
# Open http://localhost:5009
```

## ✨ Key Features

### 🔬 Automated Analysis
- **GPT-5 Integration** — Evaluates papers against 50 predefined consciousness claims
- **Evidence Extraction** — Identifies direct quotes supporting or contradicting claims
- **Strength Assessment** — Rates evidence as strong, moderate, or weak
- **Theory Synthesis** — Generates consciousness theories based on supported claims
- **Multiple Models** — Support for `gpt-5`, `gpt-5-mini`, and `gpt-5-nano`

### 🖥️ Interactive Web Viewer
- **Claims Index** — Dropdown showing all 50 claims with paper count indicators
- **Advanced Filtering**:
  - Evidence strength (Strong/Moderate/Weak/None)
  - Claim count ranges
  - Model used for analysis
  - Papers with/without insights
- **Smart Search**:
  - Full-text search across all content
  - Claim number search (e.g., type "12" to find all papers supporting claim 12)
- **Dynamic Sorting** — By date, claim count, insights, or title
- **Detailed Views** — Expandable sections for evidence, quotes, and full JSON data

## 📦 Installation

### Prerequisites
- Python 3.9 or higher
- OpenAI API key with GPT-5 access
- 2GB+ free disk space for virtual environment

### Detailed Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Consciousness_analysis
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   
   # Activate on macOS/Linux:
   source .venv/bin/activate
   
   # Activate on Windows:
   .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API key**
   ```bash
   mkdir -p config
   echo "OPENAI_API_KEY=sk-your-api-key-here" > config/.env
   ```
   > ⚠️ **Security Note**: The `.env` file is gitignored and should never be committed

## 📂 Project Structure

```
Consciousness_analysis/
├── config/
│   └── .env                    # OpenAI API key (gitignored)
├── prompts/
│   ├── theory_analysis.txt     # GPT-5 analysis instructions
│   ├── article.txt            # Paper content to analyze
│   └── link.txt              # Paper URL/DOI
├── output/
│   └── analysis_results/      # JSON analysis results
│       ├── analysis_20250822_234642_.json
│       └── analysis_20250823_115611_*.json
├── scripts/
│   ├── analyze_theories.py    # Main analysis script
│   └── analysis_viewer.py     # Flask web interface
├── requirements.txt          # Python dependencies
├── README.md                # This file
└── theory_analysis.log      # Analysis logs
```

## 🔧 Usage Guide

### Analyzing Papers

1. **Prepare input files**
   ```bash
   # Add paper content
   nano prompts/article.txt
   
   # Add paper URL or DOI
   echo "https://example.com/paper.pdf" > prompts/link.txt
   ```

2. **Run analysis**
   ```bash
   # Default (GPT-5)
   python scripts/analyze_theories.py
   
   # With specific model
   python scripts/analyze_theories.py --model gpt-5-mini
   
   # With console summary
   python scripts/analyze_theories.py --summary
   ```

3. **Monitor progress**
   ```bash
   # Watch logs in real-time
   tail -f theory_analysis.log
   ```

### Viewing Results

1. **Start the viewer**
   ```bash
   python scripts/analysis_viewer.py
   ```

2. **Access interface**
   - Local: http://localhost:5009
   - Network: http://[your-ip]:5009

3. **Use the interface**
   - **Claims Index**: Select any claim from the dropdown to filter papers
   - **Search**: Type claim numbers (e.g., "23") or keywords
   - **Filters**: Combine multiple filters for precise results
   - **Export**: Access raw JSON via "View Complete JSON Data"

## 📊 Output Format

Each analysis generates a structured JSON file:

```json
{
  "paper_metadata": {
    "title": "The efference cascade, consciousness, and its self",
    "link": "https://pmc.ncbi.nlm.nih.gov/articles/PMC3738861/"
  },
  "theory_synthesis": {
    "description": "Conscious sensory phenomenology is implemented in dorsal pulvinar...",
    "type": "Subcortical orienting-based model"
  },
  "supported_claims": [3, 4, 8, 11, 12, 13, 16, 39, 41],
  "evidence_details": {
    "3": {
      "claim_text": "Fast-spiking PV interneurons are necessary for sustaining gamma-band synchrony",
      "direct_quotes": [
        {
          "quote": "Interneurons tend to have resonant frequencies in the gamma range...",
          "page_or_section": "Section 2, pp. 403–404"
        }
      ],
      "interpretation": "The review synthesizes evidence that fast-spiking interneurons...",
      "strength": "moderate",
      "limitations": "The paper emphasizes interneurons broadly..."
    }
  },
  "additional_or_contradictory_insights": [
    {
      "finding": "Dorsal pulvinar implements global best estimate",
      "quotes": ["I have previously proposed..."],
      "relevance": "Articulates mechanism for unified phenomenal content"
    }
  ]
}
```

## 🎯 The 50 Consciousness Claims

### Ion Channels (1-5)
- Nav channel density, spike initiation, GABA receptors

### Cytoskeleton (6-12)  
- Microtubule stability, synaptic scaffolds, metabolic coupling

### EM Fields (13-22)
- Spatial organization, field patterns, integration windows

### Microtubules (23-32)
- MAP regulation, anesthetic binding, receptor trafficking

### Signaling Pathways (33-38)
- Phosphorylation cascades, post-translational modifications

### Perturbation Experiments (39-50)
- Stimulation protocols, anesthesia effects, cross-species validation

> View all claims in the web interface dropdown or in `scripts/analyze_theories.py`

## 🛠️ Advanced Features

### API Endpoints
- `GET /` — Main web interface
- `GET /api/papers` — All papers as JSON
- `GET /api/statistics` — Analysis statistics  
- `GET /api/claims` — Claim distribution across papers

### Filtering Logic
- **Individual evidence filtering** — Hide/show specific evidence items by strength
- **Compound filters** — Combine search, strength, model, and count filters
- **Real-time updates** — Filter results update instantly
- **Persistent state** — Filters remain active during session

### Performance Optimization
- **Retry logic** — Automatic retry with exponential backoff for API limits
- **Efficient rendering** — Collapsible sections prevent UI overload
- **Lazy loading** — JSON details load on demand

## ⚡ Troubleshooting

| Issue | Solution |
|-------|----------|
| **"OPENAI_API_KEY not found"** | Create `config/.env` with your API key |
| **"File not found: article.txt"** | Ensure files exist in `prompts/` directory |
| **Rate limit errors** | Script auto-retries; wait or use `--model gpt-5-mini` |
| **No papers showing in viewer** | Check `output/analysis_results/` for JSON files |
| **Port 5009 in use** | Change port in `analysis_viewer.py` last line |
| **JSON decode error** | Check `theory_analysis.log` for malformed responses |

## 🔒 Security Best Practices

- **API Keys**: Never commit `.env` files; they're gitignored
- **Sensitive Data**: Avoid analyzing papers with PII
- **Network Access**: Viewer binds to `0.0.0.0` by default; restrict for production
- **File Permissions**: Ensure `config/` is readable only by your user

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-analysis`)
3. Make changes and test thoroughly
4. Submit a pull request with clear description

### Development Setup
```bash
# Install dev dependencies
pip install pytest black flake8

# Run tests
pytest tests/

# Format code
black scripts/

# Lint
flake8 scripts/
```

## 📄 License

This project is for research purposes. Ensure compliance with:
- [OpenAI Usage Policies](https://openai.com/policies/usage-policies)
- Your institution's research guidelines
- Journal publication requirements when using results

## 🔗 Resources

- [OpenAI GPT-5 Documentation](https://platform.openai.com/docs)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Consciousness Studies Resources](https://plato.stanford.edu/entries/consciousness/)

## 📧 Support

- **Issues**: Open a GitHub issue with logs and error messages
- **Questions**: Include your Python version and OS
- **Feature Requests**: Describe use case and expected behavior

---

*Built with 🧠 for consciousness research*