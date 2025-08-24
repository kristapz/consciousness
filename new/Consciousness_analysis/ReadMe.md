# Consciousness Theory Analysis Tool

A Python-based tool for analyzing scientific papers against consciousness-related claims using GPT-5. This tool extracts evidence from papers and evaluates how they support or relate to 50 core claims about consciousness, covering topics from ion channels and cytoskeleton to electromagnetic fields and microtubules.

## 🧠 Overview

This project provides:
- Automated analysis of scientific papers using GPT-5
- Evaluation against 50 predefined consciousness-related claims
- Interactive web-based viewer for browsing analysis results
- Support for different GPT-5 model variants (standard, mini, nano)

## 📋 Prerequisites

- Python 3.9 or higher
- OpenAI API key with GPT-5 access
- Virtual environment (recommended)

## 🚀 Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd Consciousness_analysis
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv .venv
   
   # On macOS/Linux:
   source .venv/bin/activate
   
   # On Windows:
   .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   Create a `.env` file in the `config` directory:
   ```bash
   mkdir -p config
   echo "OPENAI_API_KEY=your-api-key-here" > config/.env
   ```

## 📁 Project Structure

```
Consciousness_analysis/
├── config/
│   └── .env                    # Environment variables (API keys)
├── prompts/
│   ├── theory_analysis.txt     # Analysis prompt template
│   ├── article.txt            # Paper content to analyze
│   └── link.txt              # Paper URL/link
├── output/
│   └── analysis_results/      # JSON analysis results
├── scripts/
│   ├── analyze_theories.py    # Main analysis script
│   └── analysis_viewer.py     # Flask web viewer
└── requirements.txt          # Python dependencies
```

## 🔧 Usage

### Running the Analysis

1. **Prepare your paper for analysis:**
   - Place the paper content in `prompts/article.txt`
   - Add the paper URL to `prompts/link.txt`
   - The analysis prompt is already configured in `prompts/theory_analysis.txt`

2. **Run the analysis script:**
   ```bash
   python scripts/analyze_theories.py
   ```

   **Optional arguments:**
   ```bash
   # Use a specific model variant
   python scripts/analyze_theories.py --model gpt-5-mini
   
   # Show summary after analysis
   python scripts/analyze_theories.py --summary
   ```

3. **Results are saved to:**
   `output/analysis_results/analysis_TIMESTAMP_PAPERID.json`

### Viewing Results

1. **Start the Flask viewer:**
   ```bash
   python scripts/analysis_viewer.py
   ```

2. **Open in browser:**
   Navigate to `http://localhost:5009`

3. **Features:**
   - Browse all analyzed papers
   - Filter by evidence strength (strong/moderate/weak)
   - Filter by claim count, model used, insights
   - Search across all content
   - Sort by date, claims, or insights
   - View detailed evidence with quotes and interpretations

## 📊 Analysis Output Format

Each analysis produces a JSON file containing:

```json
{
  "paper_metadata": {
    "title": "Paper Title",
    "link": "https://..."
  },
  "theory_synthesis": {
    "description": "Theory developed from supported claims",
    "type": "Theory type/category"
  },
  "supported_claims": [1, 5, 12, ...],
  "evidence_details": {
    "claim_number": {
      "claim_text": "Original claim",
      "direct_quotes": [...],
      "interpretation": "How evidence supports claim",
      "strength": "strong/moderate/weak",
      "limitations": "Any caveats"
    }
  },
  "additional_or_contradictory_insights": [...]
}
```

## 🎯 Core Claims Categories

The tool analyzes papers against 50 claims organized into categories:

1. **Ion Channels (1-5):** Nav/Kv channel dynamics, GABA receptors
2. **Cytoskeleton (6-12):** Microtubule stability, synaptic organization
3. **EM Fields (13-22):** Electromagnetic field patterns and consciousness
4. **Microtubules (23-32):** Stability effects on spike timing and synchrony
5. **Signaling Pathways (33-38):** Phosphorylation, post-translational modifications
6. **Perturbation Experiments (39-50):** Stimulation protocols, cross-species validation

## 🛠️ API Endpoints

The Flask viewer provides several API endpoints:

- `GET /` - Main web interface
- `GET /api/papers` - All papers as JSON
- `GET /api/statistics` - Analysis statistics
- `GET /api/claims` - Claim distribution data

## ⚙️ Configuration

### Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key (required)

### Model Selection
Available models:
- `gpt-5` (default): Full GPT-5 model
- `gpt-5-mini`: Smaller, faster variant
- `gpt-5-nano`: Smallest variant

### Rate Limiting
The script includes retry logic with exponential backoff for API rate limits.

## 🐛 Troubleshooting

**Common Issues:**

1. **API Key Error:**
   - Ensure `.env` file exists in `config/` directory
   - Verify API key has GPT-5 access

2. **File Not Found:**
   - Check that `article.txt` and `link.txt` exist in `prompts/`
   - Ensure proper file permissions

3. **JSON Parse Error:**
   - Check logs in `theory_analysis.log`
   - Verify GPT-5 response format

4. **Flask Viewer Issues:**
   - Ensure port 5009 is available
   - Check that JSON files exist in `output/analysis_results/`

## 📝 Logging

Logs are written to:
- Console output
- `theory_analysis.log` file

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is for research purposes. Please ensure compliance with OpenAI's usage policies.

## 🔗 Links

- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Flask Documentation](https://flask.palletsprojects.com/)

## 📧 Support

For issues or questions, please open an issue on the repository.