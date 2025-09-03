#!/usr/bin/env python3
"""
Flask Analysis Viewer - Consciousness Phenomena Analysis
Updated to handle the new 9 phenomena framework
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template_string, jsonify, request

# Setup
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get project root and output directory
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
OUTPUT_DIR = PROJECT_ROOT / "output" / "analysis_results"

# Define the 9 consciousness phenomena
CONSCIOUSNESS_PHENOMENA = {
    "information_integration": {
        "name": "Information Integration",
        "description": "Distributed elements combine into unified representations or system-wide access.",
        "biological_markers": ["global workspace-like activation", "frontoparietal hub engagement",
                               "long-range coherence", "binding by synchrony"],
        "ai_markers": ["attention convergence", "low-rank/residual integration", "feature superposition",
                       "aggregator/CLS tokens"]
    },
    "state_transitions": {
        "name": "State Transitions",
        "description": "Abrupt or metastable switches between processing regimes.",
        "biological_markers": ["ignition events (e.g., P3b)", "metastable switching", "up/down states"],
        "ai_markers": ["abrupt capability onsets", "mode switches in activation space", "grokking-like phase change"]
    },
    "temporal_coordination": {
        "name": "Temporal Coordination",
        "description": "Timing mechanisms that bind or segment content.",
        "biological_markers": ["oscillations", "phase-locking", "cross-frequency coupling", "thalamic pacing"],
        "ai_markers": ["attention synchronization", "routing schedules", "positional/temporal encoding dynamics"]
    },
    "selective_routing": {
        "name": "Selective Routing",
        "description": "Gating and control of information flow.",
        "biological_markers": ["pulvinar/intralaminar gating", "TRN inhibition", "PV/SST/VIP gain control",
                               "neuromodulation"],
        "ai_markers": ["attention weights", "masking/gating modules", "mixture-of-experts routing"]
    },
    "representational_structure": {
        "name": "Representational Structure",
        "description": "How information is encoded, organized, and accessed.",
        "biological_markers": ["population codes", "cell assemblies", "cognitive maps"],
        "ai_markers": ["embeddings", "SAE latents", "representational subspaces/geometry", "polysemanticity"]
    },
    "causal_control": {
        "name": "Causal Control",
        "description": "Interventions that change computation, access, or behavior.",
        "biological_markers": ["TMS/tACS/tFUS/DBS effects", "lesion/optogenetic manipulation"],
        "ai_markers": ["ablation", "activation patching", "routing/objective edits"]
    },
    "emergent_dynamics": {
        "name": "Emergent Dynamics",
        "description": "Higher-order phenomena arising from interactions.",
        "biological_markers": ["criticality", "complexity indices (PCI/LZC)", "global state signatures"],
        "ai_markers": ["in-context learning", "emergent strategies", "self-organization"]
    },
    "valence_welfare": {
        "name": "Valence & Welfare",
        "description": "Affective value, aversion, and persistence relevant to suffering.",
        "biological_markers": ["PAG, amygdala, insula, ACC coupling", "spinothalamic input", "neuromodulatory shifts"],
        "ai_markers": ["negative reward channels", "value heads/critics", "aversive-cost signals",
                       "persistence of negative states"]
    },
    "self_model_report": {
        "name": "Self-Model & Reportability",
        "description": "Higher-order access, confidence, and report links.",
        "biological_markers": ["PFC/ACC metacognition", "report-linked signatures"],
        "ai_markers": ["introspection/verifier modules", "confidence estimators", "report pathways"]
    }
}

# HTML Template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Consciousness Phenomena Analysis</title>
    <link href="https://fonts.googleapis.com/css2?family=EB+Garamond:wght@400;500&display=swap" rel="stylesheet">
    <style>
        /* Reset and Base Styles */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'EB Garamond', Georgia, serif;
            font-size: 20px;
            line-height: 1.7;
            color: #000;
            background: #fff;
            -webkit-font-smoothing: antialiased;
        }

        /* Title Page */
        .title-page {
            width: 100%;
            height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
        }

        .title-content {
            text-align: center;
            padding: 80px 60px;
        }

        .title-main {
            font-size: 60px;
            font-weight: 900;
            letter-spacing: -0.02em;
            line-height: 1.1;
            color: #fdfde7;
            margin-bottom: 30px;
            text-transform: uppercase;
        }

        .title-subtitle {
            font-size: 22px;
            color: #fdfde7;
            opacity: 0.9;
        }

        /* Layout */
        .content-container {
            display: flex;
            width: 100%;
            min-height: 100vh;
        }

        /* Sidebar */
        .sidebar {
            position: fixed;
            left: 0;
            top: 0;
            bottom: 0;
            width: 40px;
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 100;
        }

        .sidebar-track {
            position: absolute;
            width: 1px;
            height: 90%;
            background: #e0e0e0;
        }

        .sidebar-progress {
            position: absolute;
            top: 5%;
            width: 1px;
            background: #000;
            height: 0%;
            transition: none;
        }

        /* Main Content */
        .main-content {
            margin-left: 10%;
            width: 80%;
            max-width: 1200px;
            padding: 90px 0;
        }

        /* Typography */
        h1 {
            font-size: 48px;
            font-weight: 400;
            margin-bottom: 40px;
            letter-spacing: -0.02em;
            color: #000;
        }

        h2 {
            font-size: 36px;
            font-weight: 400;
            margin-top: 60px;
            margin-bottom: 20px;
            color: #000;
        }

        h3 {
            font-size: 24px;
            font-weight: 400;
            margin-top: 30px;
            margin-bottom: 16px;
            color: #000;
        }

        /* Stats Grid */
        .stats {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 0;
            margin-bottom: 60px;
        }

        .stat-card {
            text-align: center;
            padding: 30px 20px;
            border-right: 1px solid #e0e0e0;
        }

        .stat-card:last-child {
            border-right: none;
        }

        .stat-number {
            font-size: 48px;
            font-weight: 400;
            color: #000;
            margin-bottom: 10px;
        }

        .stat-label {
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: #666;
        }

        /* Phenomena Grid */
        .phenomena-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            margin: 40px 0;
        }

        .phenomenon-card {
            padding: 20px;
            background: #f8f8f8;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s ease;
            border: 2px solid transparent;
        }

        .phenomenon-card:hover {
            background: #f0f0f0;
            transform: translateY(-2px);
        }

        .phenomenon-card.active {
            background: #fff;
            border: 2px solid #000;
        }

        .phenomenon-name {
            font-size: 18px;
            font-weight: 500;
            margin-bottom: 8px;
        }

        .phenomenon-description {
            font-size: 14px;
            color: #666;
            line-height: 1.4;
        }

        .phenomenon-count {
            display: inline-block;
            margin-top: 10px;
            padding: 2px 8px;
            background: #000;
            color: #fff;
            border-radius: 12px;
            font-size: 12px;
        }

        .phenomenon-count.zero {
            background: #e0e0e0;
            color: #999;
        }

        /* Filters */
        .filters-section {
            background: #f8f8f8;
            padding: 30px;
            margin-bottom: 40px;
            border-radius: 8px;
        }

        .filter-group {
            margin-bottom: 20px;
        }

        .filter-label {
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: #666;
            margin-bottom: 10px;
            display: block;
        }

        .system-filters {
            display: flex;
            gap: 15px;
        }

        .filter-option {
            display: flex;
            align-items: center;
            gap: 5px;
            cursor: pointer;
        }

        .filter-option input {
            cursor: pointer;
        }

        .filter-option label {
            cursor: pointer;
            font-size: 16px;
        }

        .filter-button {
            padding: 8px 20px;
            background: #000;
            color: #fff;
            border: none;
            border-radius: 4px;
            font-size: 16px;
            cursor: pointer;
            transition: background 0.2s ease;
        }

        .filter-button:hover {
            background: #333;
        }

        input[type="text"] {
            width: 100%;
            padding: 10px;
            font-family: 'EB Garamond', Georgia, serif;
            font-size: 18px;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
        }

        /* Papers */
        .paper {
            margin-bottom: 80px;
            padding: 40px;
            background: #fff;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
        }

        .paper-title {
            font-size: 32px;
            font-weight: 400;
            margin-bottom: 10px;
            color: #000;
        }

        .paper-meta {
            font-size: 16px;
            color: #666;
            margin-bottom: 20px;
        }

        .paper-domain {
            display: inline-block;
            padding: 4px 12px;
            background: #f0f0f0;
            border-radius: 4px;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-left: 10px;
        }

        /* Evidence Items */
        .evidence-item {
            padding: 30px;
            margin: 20px 0;
            background: #fafafa;
            border-left: 3px solid #000;
            border-radius: 4px;
        }

        .evidence-header {
            margin-bottom: 15px;
        }

        .phenomenon-badge {
            display: inline-block;
            padding: 4px 12px;
            background: #000;
            color: #fff;
            border-radius: 4px;
            font-size: 14px;
            margin-right: 10px;
        }

        .system-type {
            display: inline-block;
            padding: 4px 10px;
            border: 1px solid #666;
            border-radius: 4px;
            font-size: 14px;
            margin-right: 10px;
        }

        .species-model {
            font-size: 14px;
            color: #666;
        }

        .mechanism {
            font-size: 18px;
            margin: 15px 0;
            line-height: 1.5;
        }

        /* Quotes */
        .quote-item {
            margin: 20px 0;
            padding-left: 20px;
            border-left: 2px solid #e0e0e0;
        }

        .quote-text {
            font-style: italic;
            color: #333;
            margin-bottom: 8px;
        }

        .quote-meta {
            font-size: 14px;
            color: #666;
        }

        .quote-interpretation {
            margin-top: 10px;
            font-size: 16px;
            color: #555;
        }

        /* Figures and Tables */
        .references {
            margin-top: 20px;
            padding: 15px;
            background: #f8f8f8;
            border-radius: 4px;
        }

        .ref-label {
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #666;
            margin-bottom: 8px;
        }

        .ref-item {
            margin: 8px 0;
            font-size: 16px;
        }

        /* No results */
        .no-results {
            text-align: center;
            padding: 60px 20px;
            color: #666;
            font-style: italic;
        }

        /* Mobile */
        @media (max-width: 768px) {
            .phenomena-grid {
                grid-template-columns: 1fr;
            }

            .stats {
                grid-template-columns: repeat(2, 1fr);
            }

            .main-content {
                margin-left: 5%;
                width: 90%;
            }
        }
    </style>
</head>
<body>
    <!-- Title Page -->
    <div class="title-page">
        <div class="title-content">
            <h1 class="title-main">Consciousness Phenomena Analysis</h1>
            <p class="title-subtitle">Evidence Across 9 Core Phenomena in Brain & AI Systems</p>
        </div>
    </div>

    <!-- Content Container -->
    <div class="content-container">
        <!-- Sidebar -->
        <nav class="sidebar">
            <div class="sidebar-track"></div>
            <div class="sidebar-progress"></div>
        </nav>

        <!-- Main Content -->
        <article class="main-content">
            <section id="overview">
                <h1>Analysis Overview</h1>

                <!-- Statistics -->
                <div class="stats">
                    <div class="stat-card">
                        <div class="stat-number">{{ papers|length }}</div>
                        <div class="stat-label">Papers</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{{ total_evidence }}</div>
                        <div class="stat-label">Evidence Items</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{{ phenomena_count }}</div>
                        <div class="stat-label">Phenomena</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{{ unique_systems }}</div>
                        <div class="stat-label">Systems</div>
                    </div>
                </div>

                <!-- Phenomena Overview -->
                <h2>Core Phenomena</h2>
                <div class="phenomena-grid">
                    {% for pid, pdata in phenomena.items() %}
                    <div class="phenomenon-card" data-phenomenon="{{ pid }}" onclick="togglePhenomenon('{{ pid }}')">
                        <div class="phenomenon-name">{{ pdata.name }}</div>
                        <div class="phenomenon-description">{{ pdata.description }}</div>
                        <span class="phenomenon-count {% if phenomenon_counts.get(pid, 0) == 0 %}zero{% endif %}">
                            {{ phenomenon_counts.get(pid, 0) }} evidence
                        </span>
                    </div>
                    {% endfor %}
                </div>

                <!-- Filters -->
                <div class="filters-section">
                    <div class="filter-group">
                        <label class="filter-label">Search</label>
                        <input type="text" id="searchInput" placeholder="Search papers, evidence, quotes...">
                    </div>

                    <div class="filter-group">
                        <label class="filter-label">System Type</label>
                        <div class="system-filters">
                            <div class="filter-option">
                                <input type="checkbox" id="system-bio" checked>
                                <label for="system-bio">Biological</label>
                            </div>
                            <div class="filter-option">
                                <input type="checkbox" id="system-ai" checked>
                                <label for="system-ai">AI</label>
                            </div>
                            <div class="filter-option">
                                <input type="checkbox" id="system-other" checked>
                                <label for="system-other">Other</label>
                            </div>
                        </div>
                    </div>

                    <button class="filter-button" onclick="applyFilters()">Apply Filters</button>
                    <button class="filter-button" onclick="clearFilters()" style="background: #666; margin-left: 10px;">Clear</button>
                </div>
            </section>

            <!-- Papers -->
            <section id="papers">
                <h2>Paper Analyses</h2>

                <div id="noResults" class="no-results" style="display: none;">
                    No evidence found matching your filters.
                </div>

                {% for paper in papers %}
                <div class="paper" data-paper-index="{{ loop.index0 }}">
                    <!-- Paper Header -->
                    <h3 class="paper-title">
                        {{ paper.paper_metadata.title if paper.paper_metadata else 'Untitled' }}
                    </h3>
                    <div class="paper-meta">
                        {% if paper.paper_metadata %}
                            {% if paper.paper_metadata.authors %}
                                {{ paper.paper_metadata.authors|join(', ') }}
                            {% endif %}
                            {% if paper.paper_metadata.year %}
                                ({{ paper.paper_metadata.year }})
                            {% endif %}
                            {% if paper.paper_metadata.domain %}
                                <span class="paper-domain">{{ paper.paper_metadata.domain }}</span>
                            {% endif %}
                            {% if paper.paper_metadata.doi_or_arxiv %}
                                <br><a href="https://doi.org/{{ paper.paper_metadata.doi_or_arxiv }}" target="_blank">
                                    {{ paper.paper_metadata.doi_or_arxiv }}
                                </a>
                            {% endif %}
                        {% endif %}
                    </div>

                    <!-- Evidence Items -->
                    {% if paper.evidence %}
                    <div class="evidence-section">
                        {% for item in paper.evidence %}
                        <div class="evidence-item" 
                             data-phenomenon="{{ item.phenomenon_id }}"
                             data-system="{{ item.system_type }}">

                            <div class="evidence-header">
                                <span class="phenomenon-badge">
                                    {{ phenomena[item.phenomenon_id].name }}
                                </span>
                                <span class="system-type">{{ item.system_type|upper }}</span>
                                <span class="species-model">{{ item.species_or_model }}</span>
                            </div>

                            <div class="mechanism">
                                <strong>{{ item.brief_mechanism }}</strong>
                            </div>

                            <!-- Method and State -->
                            <div style="font-size: 14px; color: #666; margin: 10px 0;">
                                Method: {{ item.method }} | State: {{ item.state }}
                                {% if item.time %}
                                    {% if item.time.bio_ms %}
                                        | Time: {{ item.time.bio_ms }}ms
                                    {% endif %}
                                    {% if item.time.ai_units %}
                                        {% if item.time.ai_units.layers %}
                                            | Layers: {{ item.time.ai_units.layers }}
                                        {% endif %}
                                        {% if item.time.ai_units.tokens %}
                                            | Tokens: {{ item.time.ai_units.tokens }}
                                        {% endif %}
                                    {% endif %}
                                {% endif %}
                            </div>

                            <!-- Text References -->
                            {% if item.text_refs %}
                            <div class="quotes-section">
                                {% for ref in item.text_refs %}
                                <div class="quote-item">
                                    <div class="quote-text">
                                        "{{ ref.quote }}"
                                    </div>
                                    <div class="quote-meta">
                                        — {{ ref.section_title }} ({{ ref.section_type }})
                                        {% if ref.page %}, p.{{ ref.page }}{% endif %}
                                    </div>
                                    {% if ref.interpretation %}
                                    <div class="quote-interpretation">
                                        → {{ ref.interpretation }}
                                    </div>
                                    {% endif %}
                                </div>
                                {% endfor %}
                            </div>
                            {% endif %}

                            <!-- Figures and Tables -->
                            {% if item.figure_refs or item.table_refs %}
                            <div class="references">
                                {% if item.figure_refs %}
                                <div class="ref-label">Figures:</div>
                                {% for fig in item.figure_refs %}
                                <div class="ref-item">
                                    <strong>{{ fig.figure_label }}</strong> (p.{{ fig.page }}): 
                                    {{ fig.interpretation_short }}
                                </div>
                                {% endfor %}
                                {% endif %}

                                {% if item.table_refs %}
                                <div class="ref-label">Tables:</div>
                                {% for table in item.table_refs %}
                                <div class="ref-item">
                                    <strong>{{ table.table_label }}</strong> (p.{{ table.page }})
                                </div>
                                {% endfor %}
                                {% endif %}
                            </div>
                            {% endif %}

                            <!-- Limitations -->
                            {% if item.limitations %}
                            <div style="margin-top: 15px; font-size: 14px; color: #666;">
                                <strong>Limitations:</strong> {{ item.limitations }}
                            </div>
                            {% endif %}
                        </div>
                        {% endfor %}
                    </div>
                    {% endif %}
                </div>
                {% endfor %}
            </section>
        </article>
    </div>

    <script>
        // State management
        let selectedPhenomena = new Set();
        let selectedSystems = new Set(['bio', 'ai', 'other']);
        let searchTerm = '';

        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            updateProgress();
        });

        // Toggle phenomenon selection
        function togglePhenomenon(pid) {
            const card = document.querySelector(`.phenomenon-card[data-phenomenon="${pid}"]`);

            if (selectedPhenomena.has(pid)) {
                selectedPhenomena.delete(pid);
                card.classList.remove('active');
            } else {
                selectedPhenomena.add(pid);
                card.classList.add('active');
            }

            applyFilters();
        }

        // Apply filters
        function applyFilters() {
            // Update selected systems
            selectedSystems.clear();
            if (document.getElementById('system-bio').checked) selectedSystems.add('bio');
            if (document.getElementById('system-ai').checked) selectedSystems.add('ai');
            if (document.getElementById('system-other').checked) selectedSystems.add('other');

            // Get search term
            searchTerm = document.getElementById('searchInput').value.toLowerCase();

            // Filter evidence
            const papers = document.querySelectorAll('.paper');
            let visiblePapers = 0;
            let visibleEvidence = 0;

            papers.forEach(paper => {
                let paperHasMatch = false;
                const evidenceItems = paper.querySelectorAll('.evidence-item');

                evidenceItems.forEach(item => {
                    const phenomenon = item.getAttribute('data-phenomenon');
                    const system = item.getAttribute('data-system');
                    const text = item.textContent.toLowerCase();

                    let matchesPhenomenon = selectedPhenomena.size === 0 || selectedPhenomena.has(phenomenon);
                    let matchesSystem = selectedSystems.has(system);
                    let matchesSearch = !searchTerm || text.includes(searchTerm);

                    if (matchesPhenomenon && matchesSystem && matchesSearch) {
                        item.style.display = 'block';
                        paperHasMatch = true;
                        visibleEvidence++;
                    } else {
                        item.style.display = 'none';
                    }
                });

                if (paperHasMatch) {
                    paper.style.display = 'block';
                    visiblePapers++;
                } else {
                    paper.style.display = 'none';
                }
            });

            // Show no results message
            document.getElementById('noResults').style.display = 
                (visiblePapers === 0) ? 'block' : 'none';
        }

        // Clear filters
        function clearFilters() {
            selectedPhenomena.clear();
            document.querySelectorAll('.phenomenon-card').forEach(card => {
                card.classList.remove('active');
            });

            document.getElementById('system-bio').checked = true;
            document.getElementById('system-ai').checked = true;
            document.getElementById('system-other').checked = true;
            document.getElementById('searchInput').value = '';

            document.querySelectorAll('.paper').forEach(paper => {
                paper.style.display = 'block';
            });

            document.querySelectorAll('.evidence-item').forEach(item => {
                item.style.display = 'block';
            });

            document.getElementById('noResults').style.display = 'none';
        }

        // Search on enter
        document.getElementById('searchInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                applyFilters();
            }
        });

        // Progress bar
        function updateProgress() {
            window.addEventListener('scroll', function() {
                const scrollTop = window.scrollY;
                const docHeight = document.documentElement.scrollHeight - window.innerHeight;
                const scrollPercent = (scrollTop / docHeight) * 90;
                document.querySelector('.sidebar-progress').style.height = scrollPercent + '%';
            });
        }
    </script>
</body>
</html>
'''


def load_analysis_results():
    """Load all JSON files from the output directory"""
    papers = []

    if not OUTPUT_DIR.exists():
        logger.error(f"Output directory does not exist: {OUTPUT_DIR}")
        return papers, "Output directory not found"

    # Load all JSON files
    json_files = list(OUTPUT_DIR.glob("*.json"))

    # Skip processing log files
    for json_file in json_files:
        if json_file.name == "processed_papers.json":
            continue

        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                papers.append(data)
        except Exception as e:
            logger.error(f"Error loading {json_file.name}: {str(e)}")

    # Sort by timestamp if available
    papers.sort(key=lambda p: p.get('_metadata', {}).get('analysis_timestamp', ''), reverse=True)

    return papers, None


def calculate_statistics(papers):
    """Calculate statistics from the loaded papers"""
    total_evidence = 0
    phenomenon_counts = {}
    unique_systems = set()

    for paper in papers:
        evidence_items = paper.get('evidence', [])
        total_evidence += len(evidence_items)

        for item in evidence_items:
            # Count phenomena
            phenomenon_id = item.get('phenomenon_id')
            if phenomenon_id:
                phenomenon_counts[phenomenon_id] = phenomenon_counts.get(phenomenon_id, 0) + 1

            # Track systems
            system_type = item.get('system_type')
            if system_type:
                unique_systems.add(system_type)

    return {
        'total_evidence': total_evidence,
        'phenomenon_counts': phenomenon_counts,
        'phenomena_count': len([p for p in phenomenon_counts if phenomenon_counts[p] > 0]),
        'unique_systems': len(unique_systems)
    }


@app.route('/')
def index():
    """Main page displaying all analysis results"""
    papers, error = load_analysis_results()
    stats = calculate_statistics(papers)

    return render_template_string(
        HTML_TEMPLATE,
        papers=papers,
        error=error,
        phenomena=CONSCIOUSNESS_PHENOMENA,
        phenomenon_counts=stats['phenomenon_counts'],
        total_evidence=stats['total_evidence'],
        phenomena_count=stats['phenomena_count'],
        unique_systems=stats['unique_systems']
    )


@app.route('/api/papers')
def api_papers():
    """API endpoint to get all papers data"""
    papers, error = load_analysis_results()
    if error:
        return jsonify({'error': error}), 404
    return jsonify(papers)


@app.route('/api/phenomena')
def api_phenomena():
    """API endpoint to get phenomena definitions"""
    return jsonify(CONSCIOUSNESS_PHENOMENA)


@app.route('/api/stats')
def api_stats():
    """API endpoint to get statistics"""
    papers, error = load_analysis_results()
    if error:
        return jsonify({'error': error}), 404
    stats = calculate_statistics(papers)
    return jsonify(stats)


if __name__ == '__main__':
    print(f"\nConsciousness Phenomena Analysis Viewer")
    print(f"Output Directory: {OUTPUT_DIR}")
    print(f"Starting server on http://localhost:5009")

    app.run(debug=True, port=5009, host='0.0.0.0')