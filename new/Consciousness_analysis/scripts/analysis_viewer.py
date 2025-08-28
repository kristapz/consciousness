#!/usr/bin/env python3
"""
Flask Analysis Viewer - Consciousness Theory Analysis
Styled to match Fourth Offset aesthetic with advanced filtering
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

# Cumulative theory location
THEORY_DIR = PROJECT_ROOT / "output" / "cumulative_theory"
THEORY_FILE = THEORY_DIR / "current_theory.json"

def load_cumulative_theory():
    """Load the latest cumulative theory JSON (if present)."""
    try:
        if THEORY_FILE.exists():
            with open(THEORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Error loading cumulative theory: {e}")
    return None


# Define the 50 consciousness claims
CONSCIOUSNESS_CLAIMS = {
    # Ion Channels (1-5)
    "1": "Nav channel density and kinetics influence spike initiation precision and phase-locking across oscillatory bands.",
    "2": "Kv, KCNQ, and HCN channel dynamics regulate oscillation frequency and spike-time variability.",
    "3": "Fast-spiking PV interneurons are necessary for sustaining gamma-band synchrony.",
    "4": "GABA_A and GABA_B receptor kinetics set inhibitory timing windows critical for oscillation stability.",
    "5": "Presynaptic vesicle cycling, including dynamin-dependent endocytosis, constrains sustained high-frequency synchrony",

    # Cytoskeleton (6-12)
    "6": "Microtubule and MAP stability maintain synaptic organization and influence spike-time precision.",
    "7": "Actin dynamics and synaptic scaffolds (PSD-95, Shank, Homer) regulate excitatory input timing alignment.",
    "8": "AIS and node organization (ankyrin-G, βIV-spectrin) control spike initiation timing and conduction delays.",
    "9": "Myelination and conduction tuning synchronize long-range circuits at oscillation-relevant bands.",
    "10": "Mitochondrial density and ATP availability set energetic limits on high-frequency oscillations.",
    "11": "Astrocyte-neuron metabolic coupling (e.g., lactate shuttling, glutamate clearance) supports network-wide synchrony.",
    "12": "Neuromodulators (ACh, NE, DA, 5-HT) regulate oscillatory gain and preferred frequency bands.",

    # EM Fields (13-22)
    "13": "Spatially organized extracellular EM fields emerge from coordinated neuronal activity.",
    "14": "Stable EM field patterns correlate with unified conscious content over integration windows (~50–300 ms).",
    "15": "Coherent EM gradients across cortical and subcortical regions facilitate large-scale signal integration.",
    "16": "Cross-frequency nesting within EM fields couples slow oscillations to faster local synchrony.",
    "17": "Disruption of EM field stability selectively alters conscious access without abolishing spiking activity.",
    "18": "Forward modeling of iEEG, LFP, or MEG reconstructs structured EM field configurations.",
    "19": "Mesoscopic EM 'pockets' show higher spatial coherence during conscious perception than during unconscious states.",
    "20": "EM field boundaries separate unrelated contents into distinct integration domains.",
    "21": "Computational models predict that local dipole alignment produces bounded EM regions supporting unified percepts.",
    "22": "Structured EM fields facilitate long-range timing alignment beyond direct synaptic connectivity.",

    # Microtubules (23-32)
    "23": "Microtubule stability influences neuronal spike-time precision and phase-locking.",
    "24": "Tau and other MAPs (MAP2, MAP1B, CRMP2) regulate lattice stability needed for conduction timing.",
    "25": "Microtubule destabilization (e.g., nocodazole, colchicine) increases spike-time variability without abolishing spiking.",
    "26": "Stabilization agents (epothilones, paclitaxel) enhance spike-field coherence and phase alignment.",
    "27": "Anesthetics that bind tubulin (e.g., isoflurane) modulate microtubule stability and oscillatory synchrony.",
    "28": "Microtubule dynamics regulate receptor trafficking (AMPA, NMDA, GABA) impacting excitatory/inhibitory balance.",
    "29": "MAP-dependent microtubule stability influences dendritic spine structure and excitatory input timing.",
    "30": "Microtubule disruption impairs late-phase LTP while sparing early synaptic responses.",
    "31": "Pharmacological or genetic stabilization enhances learning-related oscillatory coherence.",
    "32": "Neurotrophic signaling pathways (e.g., Trk family) regulate MAP expression and microtubule stability gating circuit alignment.",

    # Signaling Pathways (33-38)
    "33": "PI3K/Akt/mTOR activity modulates tau phosphorylation and MAP synthesis affecting lattice stability.",
    "34": "GSK3β and CDK5 phosphorylation dynamics influence microtubule stability and spike-time precision.",
    "35": "Protein phosphatases (PP2A, calcineurin) can reverse tau/MAP phosphorylation and restore synchrony capacity.",
    "36": "Microtubule post-translational modifications (acetylation, detyrosination, polyglutamylation) tune lattice longevity and timing precision.",
    "37": "Actin–microtubule cross-talk (RhoA/ROCK, LIMK/cofilin, Arp2/3) shapes spine architecture critical for timing alignment.",
    "38": "Oligodendrocyte/myelination signaling (e.g., NRG1/ErbB) tunes conduction properties for phase alignment.",

    # Perturbation Experiments (39-50)
    "39": "Closed-loop phase-locked stimulation (tACS/tFUS/TMS) delivered in-phase with endogenous rhythms enhances local synchrony and conscious access.",
    "40": "Out-of-phase stimulation disrupts synchrony and excludes the stimulated region from contributing to access.",
    "41": "Frequency-specific stimulation biases content: gamma entrainment enhances binding, beta/alpha biases gating.",
    "42": "Focused tFUS targeting deep integration hubs modulates global oscillatory coherence and conscious reportability.",
    "43": "Anesthesia-induced unconsciousness correlates with disrupted EM field pocket stability, even with preserved spiking.",
    "44": "Repetitive stimulation protocols induce plastic aftereffects, shifting baseline synchrony beyond stimulation windows.",
    "45": "Well-powered sham-controlled studies can yield null results, directly testing the necessity of local synchrony for conscious access.",
    "46": "High-density ECoG/MEG/iEEG reveals bounded EM pockets during conscious perception that collapse during unconscious states.",
    "47": "Binocular rivalry and ambiguous figure paradigms show EM pocket topology tracks dominant percepts at constant sensory input.",
    "48": "Backward masking paradigms demonstrate preserved early responses but reduced late coherence when access fails.",
    "49": "Information-theoretic analyses (Granger, transfer entropy) can identify directionality of conscious content flow distinct from raw coherence.",
    "50": "Cross-species replication (mouse laminar → macaque ECoG → human MEG) tests generalizability of EM pocket formation and their role in conscious access."
}

# HTML Template with Fourth Offset aesthetic and advanced filtering
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Consciousness Theory Analysis</title>
    <link href="https://fonts.googleapis.com/css2?family=EB+Garamond:wght@400;500&display=swap" rel="stylesheet">
    <style>
        /* Reset */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        html, body {
            height: 100%;
        }

        body {
            font-family: 'EB Garamond', Georgia, serif;
            font-size: 20px;
            font-weight: 400;
            line-height: 1.7;
            color: #000;
            background: #fff;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }

        /* Title Page */
        .title-page {
            position: relative;
            width: 100%;
            height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
        }

        .title-content {
            text-align: center;
            max-width: 800px;
            padding: 80px 60px;
            z-index: 2;
        }

        .title-main {
            font-family: Georgia, serif;
            font-size: 60px;
            font-weight: 900;
            letter-spacing: -0.02em;
            line-height: 1.1;
            color: #fdfde7;
            margin-bottom: 30px;
            text-transform: uppercase;
        }

        .title-subtitle {
            font-family: 'EB Garamond', Georgia, serif;
            font-size: 22px;
            font-weight: 400;
            color: #fdfde7;
            opacity: 0.9;
        }

        .scroll-indicator {
            position: absolute;
            bottom: 40px;
            left: 50%;
            transform: translateX(-50%);
            cursor: pointer;
            z-index: 2;
        }

        .scroll-arrow {
            width: 20px;
            height: 20px;
            border-right: 2px solid #fdfde7;
            border-bottom: 2px solid #fdfde7;
            transform: rotate(45deg);
            animation: scrollBounce 2s infinite;
        }

        @keyframes scrollBounce {
            0%, 100% { transform: rotate(45deg) translateY(0); }
            50% { transform: rotate(45deg) translateY(-10px); }
        }

        /* Layout Container */
        .content-container {
            display: flex;
            width: 100%;
            min-height: 100vh;
            position: relative;
        }

        /* Left Sidebar */
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
            background: transparent;
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

        .nav-dots {
            position: relative;
            height: 90%;
            width: 100%;
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
            align-items: center;
            padding: 10px 0;
        }

        .nav-dot {
            position: absolute;
            width: 30px;
            height: 30px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            text-decoration: none;
        }

        .nav-dot::before {
            content: '';
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: #ccc;
            transition: all 0.2s ease;
        }

        .nav-dot:hover::before,
        .nav-dot.active::before {
            width: 8px;
            height: 8px;
            background: #000;
        }

        .tooltip {
            position: absolute;
            left: 100%;
            margin-left: 5px;
            font-size: 13px;
            font-weight: 400;
            color: #666;
            padding: 2px 8px;
            white-space: nowrap;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.2s ease;
            font-family: 'EB Garamond', Georgia, serif;
            max-width: 200px;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .sidebar:hover .tooltip {
            opacity: 1;
        }

        /* Main Content */
        .main-content {
            margin-left: 17%;
            width: 54%;
            max-width: 900px;
            padding: 90px 0;
        }

        /* Right Citations Column */
        .citations-container {
            position: absolute;
            left: 64%;
            width: 29%;
            top: 60px;
            padding-right: 40px;
        }

        /* Typography */
        h1 {
            font-family: 'EB Garamond', Georgia, serif;
            font-size: 48px;
            font-weight: 400;
            line-height: 1.1;
            margin-bottom: 40px;
            letter-spacing: -0.02em;
            color: #000;
            opacity: 0.85;
        }

        h2 {
            font-family: 'EB Garamond', Georgia, serif;
            font-size: 32px;
            font-weight: 400;
            margin-top: 60px;
            margin-bottom: 20px;
            letter-spacing: -0.01em;
            color: #000;
            opacity: 0.85;
        }

        h3 {
            font-family: 'EB Garamond', Georgia, serif;
            font-size: 26px;
            font-weight: 400;
            margin-top: 30px;
            margin-bottom: 16px;
            color: #000;
            opacity: 0.85;
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
            line-height: 1;
            margin-bottom: 10px;
        }

        .stat-label {
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: #666;
            font-weight: 400;
        }

        /* Filter Section */
        .filters-section {
            background: #f8f8f8;
            padding: 30px;
            margin-bottom: 40px;
            border-radius: 8px;
        }

        .filter-group {
            margin-bottom: 20px;
        }

        .filter-group:last-child {
            margin-bottom: 0;
        }

        .filter-label {
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: #666;
            margin-bottom: 10px;
            display: block;
        }

        .strength-filters {
            display: flex;
            gap: 15px;
        }

        .strength-option {
            display: flex;
            align-items: center;
            gap: 5px;
            cursor: pointer;
        }

        .strength-option input[type="checkbox"] {
            cursor: pointer;
        }

        .strength-option label {
            cursor: pointer;
            font-size: 16px;
        }

        .filter-controls {
            display: flex;
            gap: 15px;
            align-items: center;
            margin-top: 20px;
        }

        .filter-button {
            padding: 8px 20px;
            background: #000;
            color: #fff;
            border: none;
            border-radius: 4px;
            font-family: 'EB Garamond', Georgia, serif;
            font-size: 16px;
            cursor: pointer;
            transition: background 0.2s ease;
        }

        .filter-button:hover {
            background: #333;
        }

        .filter-button.secondary {
            background: #666;
        }

        .filter-button:disabled {
            background: #e0e0e0;
            color: #999;
            cursor: not-allowed;
        }

        .active-filters {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            margin-top: 15px;
        }

        .filter-tag {
            display: inline-flex;
            align-items: center;
            gap: 5px;
            padding: 4px 10px;
            background: #000;
            color: #fff;
            border-radius: 15px;
            font-size: 14px;
        }

        .filter-tag button {
            background: none;
            border: none;
            color: #fff;
            cursor: pointer;
            font-size: 16px;
            line-height: 1;
            padding: 0 2px;
        }

        /* Claims Index */
        .claims-index {
            margin-bottom: 40px;
            border-top: 1px solid #e0e0e0;
            border-bottom: 1px solid #e0e0e0;
            padding: 30px 0;
        }

        .claims-category {
            margin-bottom: 20px;
        }

        .category-title {
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: #666;
            margin-bottom: 10px;
        }

        .claim-list {
            display: flex;
            flex-direction: column;
            gap: 6px;
        }

        .claim-option {
            display: flex;
            align-items: baseline;
            padding: 6px 10px;
            cursor: pointer;
            transition: all 0.2s ease;
            border-radius: 4px;
            border: 1px solid transparent;
        }

        .claim-option:hover {
            background: #f8f8f8;
            transform: translateX(2px);
        }

        .claim-option.active {
            background: #f0f0f0;
            border: 1px solid #000;
            font-weight: 500;
        }

        .claim-number-badge {
            font-size: 14px;
            font-weight: 500;
            color: #000;
            min-width: 30px;
            margin-right: 8px;
        }

        .claim-text-preview {
            flex: 1;
            font-size: 15px;
            line-height: 1.3;
            color: #333;
        }

        .claim-count {
            font-size: 13px;
            padding: 1px 6px;
            background: #000;
            color: #fff;
            border-radius: 10px;
            margin-left: 8px;
        }

        .claim-count.zero {
            background: #e0e0e0;
            color: #999;
        }

        /* Search */
        .search-group {
            margin-bottom: 20px;
        }

        input[type="text"] {
            width: 100%;
            padding: 10px;
            font-family: 'EB Garamond', Georgia, serif;
            font-size: 18px;
            border: 1px solid #e0e0e0;
            background: white;
            border-radius: 4px;
        }

        /* Papers */
        .paper {
            margin-bottom: 80px;
            position: relative;
        }

        .paper.filtered-result {
            background: #fafafa;
            padding: 20px;
            margin-left: -20px;
            margin-right: -20px;
            border-radius: 8px;
        }

        .paper-title {
            font-family: 'EB Garamond', Georgia, serif;
            font-size: 32px;
            font-weight: 400;
            margin-bottom: 10px;
            letter-spacing: -0.01em;
            color: #000;
            opacity: 0.85;
        }

        .paper-meta {
            font-size: 16px;
            color: #666;
            margin-bottom: 30px;
            font-family: 'EB Garamond', Georgia, serif;
        }

        .paper-link {
            color: #333;
            text-decoration: underline;
            text-underline-offset: 3px;
            text-decoration-thickness: 1px;
        }

        .paper-link:hover {
            color: #666;
        }

        /* Sections */
        .section {
            margin-bottom: 40px;
        }

        .section-title {
            font-family: 'EB Garamond', Georgia, serif;
            font-size: 16px;
            font-weight: 400;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: #333;
            margin-bottom: 20px;
            opacity: 0.8;
        }

        /* Theory Synthesis */
        .theory-synthesis {
            padding: 20px 24px;
            margin: 30px 0;
            background: white;
            border-left: 2px solid #000;
            font-style: italic;
            color: #333;
            font-size: 19px;
            line-height: 1.7;
        }

        /* Evidence */
        .evidence-item {
            padding: 20px 0;
            border-top: 1px solid #626F61;
            font-size: 16px;
            line-height: 1.5;
            color: #333;
        }

        .evidence-item:first-child {
            border-top: none;
        }

        .evidence-item.hidden-by-filter {
            display: none;
        }

        .evidence-strength {
            display: inline-block;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            padding: 2px 8px;
            margin-left: 10px;
            border-radius: 2px;
        }

        .strength-strong {
            background: #d4edda;
            color: #155724;
        }

        .strength-moderate {
            background: #fff3cd;
            color: #856404;
        }

        .strength-weak {
            background: #f8d7da;
            color: #721c24;
        }

        /* Quotes */
        .quote {
            margin: 16px 0;
            padding-left: 20px;
            border-left: 2px solid #e0e0e0;
            font-style: italic;
            color: #555;
        }

        .quote-source {
            font-size: 14px;
            color: #888;
            margin-top: 8px;
            font-style: normal;
        }

        /* Results Summary */
        .results-summary {
            background: #f0f0f0;
            padding: 20px;
            margin-bottom: 40px;
            border-radius: 8px;
            font-size: 18px;
        }

        .no-results {
            text-align: center;
            padding: 60px 20px;
            color: #666;
            font-style: italic;
        }

        /* Mobile */
        @media (max-width: 768px) {
            .title-main {
                font-size: 36px;
            }

            .sidebar {
                display: none;
            }

            .main-content {
                margin-left: 0;
                width: 100%;
                padding: 40px 20px;
            }

            .citations-container {
                display: none;
            }

            .stats {
                grid-template-columns: repeat(2, 1fr);
            }

            .strength-filters {
                flex-direction: column;
            }

            h1 {
                font-size: 32px;
            }

            h2 {
                font-size: 26px;
            }

            body {
                font-size: 18px;
            }
        }
    </style>
</head>
<body>
    <!-- Title Page -->
    <div class="title-page">
        <div class="title-content">
            <h1 class="title-main">Consciousness Theory Analysis</h1>
            <p class="title-subtitle">Scientific Evidence Across 50 Claims</p>
        </div>
        <div class="scroll-indicator" onclick="document.getElementById('overview').scrollIntoView({behavior: 'smooth'})">
            <div class="scroll-arrow"></div>
        </div>
    </div>

    <!-- Content Container -->
    <div class="content-container">
        <!-- Left Sidebar Navigation -->
        <nav class="sidebar">
            <div class="sidebar-track"></div>
            <div class="sidebar-progress"></div>
            <div class="nav-dots">
                <a href="#overview" class="nav-dot active" style="top: 0px;">
                    <span class="tooltip">Overview</span>
                </a>
                {% for paper in papers %}
                <a href="#paper-{{ loop.index0 }}" class="nav-dot" data-index="{{ loop.index0 }}">
                    <span class="tooltip">{{ get_paper_title(paper)[:50] }}...</span>
                </a>
                {% endfor %}
            </div>
        </nav>

        <!-- Main Content -->
        <article class="main-content">
                    <!-- Cumulative Theory (Latest) -->
            {% if theory and theory.theory %}
            <section id="cumulative-theory" style="margin-bottom: 40px;">
                <h1 style="margin-bottom: 20px;">Cumulative Theory (Latest)</h1>

                {% if theory.synthesis %}
                <div class="theory-synthesis">
                    {{ theory.synthesis }}
                </div>
                {% endif %}

                <!-- Core Principles -->
                {% if theory.theory.core_principles %}
                <div class="section">
                    <h3 class="section-title">Core Principles</h3>
                    <ol style="padding-left: 20px;">
                        {% for p in theory.theory.core_principles %}
                        <li style="margin-bottom: 8px;">{{ p }}</li>
                        {% endfor %}
                    </ol>
                </div>
                {% endif %}

                <!-- Mechanisms -->
                {% if theory.theory.mechanisms %}
                <div class="section">
                    <h3 class="section-title">Mechanisms</h3>
                    <div style="display: grid; grid-template-columns: 1fr; gap: 12px;">
                        {% for mech_name, mech_desc in theory.theory.mechanisms.items() %}
                        <div>
                            <strong style="text-transform: capitalize;">{{ mech_name.replace('_',' ') }}</strong>
                            <div style="margin-top: 6px;">{{ mech_desc }}</div>
                        </div>
                        {% endfor %}
                    </div>
                </div>
                {% endif %}

                <!-- Integration Framework -->
                {% if theory.theory.integration_framework %}
                <div class="section">
                    <h3 class="section-title">Integration Framework</h3>
                    <p>{{ theory.theory.integration_framework }}</p>
                </div>
                {% endif %}

                <!-- Key Predictions -->
                {% if theory.theory.key_predictions %}
                <div class="section">
                    <h3 class="section-title">Key Predictions</h3>
                    <ol style="padding-left: 20px;">
                        {% for pred in theory.theory.key_predictions %}
                        <li style="margin-bottom: 8px;">{{ pred }}</li>
                        {% endfor %}
                    </ol>
                </div>
                {% endif %}

                <!-- Confidence Levels -->
                {% if theory.theory.confidence_levels %}
                <div class="section">
                    <h3 class="section-title">Confidence Levels</h3>
                    {% for level, items in theory.theory.confidence_levels.items() %}
                    <div style="margin-bottom: 12px;">
                        <strong style="text-transform: capitalize;">{{ level }}</strong>
                        {% if items %}
                        <ul style="padding-left: 20px; margin-top: 6px;">
                            {% for it in items %}
                            <li style="margin-bottom: 6px;">{{ it }}</li>
                            {% endfor %}
                        </ul>
                        {% else %}
                        <div style="color:#666; font-size: 15px;">No items.</div>
                        {% endif %}
                    </div>
                    {% endfor %}
                </div>
                {% endif %}

                <!-- Change Log (optional) -->
                {% if theory.changes_from_previous %}
                <div class="section">
                    <h3 class="section-title">Recent Changes</h3>
                    <div style="display: grid; grid-template-columns: 1fr; gap: 8px;">
                        {% for key, vals in theory.changes_from_previous.items() %}
                        <div>
                            <strong style="text-transform: capitalize;">{{ key }}</strong>
                            {% if vals %}
                            <ul style="padding-left: 20px; margin-top: 6px;">
                                {% for v in vals %}
                                <li style="margin-bottom: 6px;">{{ v }}</li>
                                {% endfor %}
                            </ul>
                            {% else %}
                            <div style="color:#666; font-size: 15px;">None</div>
                            {% endif %}
                        </div>
                        {% endfor %}
                    </div>
                </div>
                {% endif %}

                <!-- Next Research Priorities -->
                {% if theory.next_research_priorities %}
                <div class="section">
                    <h3 class="section-title">Next Research Priorities</h3>
                    <ol style="padding-left: 20px;">
                        {% for nrp in theory.next_research_priorities %}
                        <li style="margin-bottom: 8px;">{{ nrp }}</li>
                        {% endfor %}
                    </ol>
                </div>
                {% endif %}

                <!-- Metadata -->
                {% if theory._metadata %}
                <div class="section" style="font-size: 14px; color: #666;">
                    <div><strong>Updated:</strong> {{ theory._metadata.update_timestamp or theory._metadata.updated or theory._metadata.timestamp }}</div>
                    <div><strong>Model:</strong> {{ theory._metadata.model_used }}</div>
                    <div><strong>Papers Incorporated:</strong> {{ theory._metadata.papers_incorporated }}</div>
                    {% if theory.incorporated_analyses %}
                    <div style="margin-top: 6px;">
                        <strong>Latest Analysis File:</strong>
                        {{ theory.incorporated_analyses[-1] }}
                    </div>
                    {% endif %}
                </div>
                {% endif %}
            </section>
            {% endif %}

            <section id="overview">
                <h1>Consciousness Theory Analysis</h1>

                <div class="stats">
                    <div class="stat-card">
                        <div class="stat-number">{{ papers|length }}</div>
                        <div class="stat-label">Papers</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{{ total_claims }}</div>
                        <div class="stat-label">Claims</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{{ unique_claims }}</div>
                        <div class="stat-label">Unique</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{{ total_insights }}</div>
                        <div class="stat-label">Insights</div>
                    </div>
                </div>

                <!-- Advanced Filters -->
                <div class="filters-section">
                    <div class="search-group">
                        <label class="filter-label" for="searchInput">Search Papers</label>
                        <input type="text" id="searchInput" placeholder="Search papers, claims, evidence...">
                    </div>

                    <div class="filter-group">
                        <label class="filter-label">Evidence Strength</label>
                        <div class="strength-filters">
                            <div class="strength-option">
                                <input type="checkbox" id="strength-strong" checked>
                                <label for="strength-strong">Strong</label>
                            </div>
                            <div class="strength-option">
                                <input type="checkbox" id="strength-moderate" checked>
                                <label for="strength-moderate">Moderate</label>
                            </div>
                            <div class="strength-option">
                                <input type="checkbox" id="strength-weak" checked>
                                <label for="strength-weak">Weak</label>
                            </div>
                        </div>
                    </div>

                    <div class="filter-controls">
                        <button class="filter-button" onclick="applyFilters()">Apply Filters</button>
                        <button class="filter-button secondary" onclick="clearAllFilters()">Clear All</button>
                    </div>

                    <div class="active-filters" id="activeFilters"></div>
                </div>

                <div class="results-summary" id="resultsSummary" style="display: none;"></div>

                <div class="claims-index">
                    <div class="claims-category">
                        <div class="category-title">Ion Channels (1-5)</div>
                        <div class="claim-list">
                            {% for num in range(1, 6) %}
                            <div class="claim-option" data-claim="{{ num }}" onclick="toggleClaim('{{ num }}')">
                                <span class="claim-number-badge">#{{ num }}</span>
                                <span class="claim-text-preview">{{ get_claim_text(num)[:80] }}...</span>
                                <span class="claim-count {% if claim_counts.get(num|string, 0) == 0 %}zero{% endif %}">
                                    {{ claim_counts.get(num|string, 0) }}
                                </span>
                            </div>
                            {% endfor %}
                        </div>
                    </div>

                    <div class="claims-category">
                        <div class="category-title">Cytoskeleton (6-12)</div>
                        <div class="claim-list">
                            {% for num in range(6, 13) %}
                            <div class="claim-option" data-claim="{{ num }}" onclick="toggleClaim('{{ num }}')">
                                <span class="claim-number-badge">#{{ num }}</span>
                                <span class="claim-text-preview">{{ get_claim_text(num)[:80] }}...</span>
                                <span class="claim-count {% if claim_counts.get(num|string, 0) == 0 %}zero{% endif %}">
                                    {{ claim_counts.get(num|string, 0) }}
                                </span>
                            </div>
                            {% endfor %}
                        </div>
                    </div>

                    <div class="claims-category">
                        <div class="category-title">EM Fields (13-22)</div>
                        <div class="claim-list">
                            {% for num in range(13, 23) %}
                            <div class="claim-option" data-claim="{{ num }}" onclick="toggleClaim('{{ num }}')">
                                <span class="claim-number-badge">#{{ num }}</span>
                                <span class="claim-text-preview">{{ get_claim_text(num)[:80] }}...</span>
                                <span class="claim-count {% if claim_counts.get(num|string, 0) == 0 %}zero{% endif %}">
                                    {{ claim_counts.get(num|string, 0) }}
                                </span>
                            </div>
                            {% endfor %}
                        </div>
                    </div>

                    <div class="claims-category">
                        <div class="category-title">Microtubules (23-32)</div>
                        <div class="claim-list">
                            {% for num in range(23, 33) %}
                            <div class="claim-option" data-claim="{{ num }}" onclick="toggleClaim('{{ num }}')">
                            
                            
                               <span class="claim-number-badge">#{{ num }}</span>
                               <span class="claim-text-preview">{{ get_claim_text(num)[:80] }}...</span>
                               <span class="claim-count {% if claim_counts.get(num|string, 0) == 0 %}zero{% endif %}">
                                   {{ claim_counts.get(num|string, 0) }}
                               </span>
                           </div>
                           {% endfor %}
                       </div>
                   </div>

                   <div class="claims-category">
                       <div class="category-title">Signaling Pathways (33-38)</div>
                       <div class="claim-list">
                           {% for num in range(33, 39) %}
                           <div class="claim-option" data-claim="{{ num }}" onclick="toggleClaim('{{ num }}')">
                               <span class="claim-number-badge">#{{ num }}</span>
                               <span class="claim-text-preview">{{ get_claim_text(num)[:80] }}...</span>
                               <span class="claim-count {% if claim_counts.get(num|string, 0) == 0 %}zero{% endif %}">
                                   {{ claim_counts.get(num|string, 0) }}
                               </span>
                           </div>
                           {% endfor %}
                       </div>
                   </div>

                   <div class="claims-category">
                       <div class="category-title">Perturbation Experiments (39-50)</div>
                       <div class="claim-list">
                           {% for num in range(39, 51) %}
                           <div class="claim-option" data-claim="{{ num }}" onclick="toggleClaim('{{ num }}')">
                               <span class="claim-number-badge">#{{ num }}</span>
                               <span class="claim-text-preview">{{ get_claim_text(num)[:80] }}...</span>
                               <span class="claim-count {% if claim_counts.get(num|string, 0) == 0 %}zero{% endif %}">
                                   {{ claim_counts.get(num|string, 0) }}
                               </span>
                           </div>
                           {% endfor %}
                       </div>
                   </div>
               </div>
           </section>

           <!-- Papers -->
           <div id="papersContainer">
               <div id="noResults" class="no-results" style="display: none;">
                   No evidence found matching your filters. Try adjusting your selection.
               </div>
               
               {% for paper in papers %}
               <div class="paper" id="paper-{{ loop.index0 }}" data-paper-index="{{ loop.index0 }}">
                   <h2 class="paper-title">{{ get_paper_title(paper) }}</h2>
                   {% if paper.paper_metadata and paper.paper_metadata.link %}
                   <div class="paper-meta">
                       <a href="{{ paper.paper_metadata.link }}" target="_blank" class="paper-link">
                           View paper →
                       </a>
                   </div>
                   {% endif %}

                   {% if paper.theory_synthesis %}
                   <div class="section theory-synthesis-section">
                       <h3 class="section-title">Theory Synthesis</h3>
                       <div class="theory-synthesis">
                           {{ extract_theory_synthesis(paper.theory_synthesis) }}
                       </div>
                   </div>
                   {% endif %}

                   {% if paper.evidence_details %}
                   <div class="section evidence-section">
                       <h3 class="section-title">Evidence</h3>
                       {% for claim_num, evidence in paper.evidence_details.items() %}
                       {% if evidence is mapping %}
                       <div class="evidence-item" 
                            data-claim-number="{{ claim_num }}"
                            data-strength="{{ evidence.strength|lower if evidence.strength else 'unknown' }}">
                           <strong>Claim {{ claim_num }}: {{ get_claim_text(claim_num) }}</strong>
                           {% if evidence.strength %}
                           <span class="evidence-strength strength-{{ evidence.strength|lower }}">
                               {{ evidence.strength }}
                           </span>
                           {% endif %}
                           
                           {% if evidence.interpretation %}
                           <p>{{ evidence.interpretation }}</p>
                           {% endif %}

                           {% if evidence.direct_quotes %}
                               {% for quote_obj in evidence.direct_quotes %}
                               <div class="quote">
                                   "{{ quote_obj.quote }}"
                                   {% if quote_obj.page_or_section %}
                                   <div class="quote-source">— {{ quote_obj.page_or_section }}</div>
                                   {% endif %}
                               </div>
                               {% endfor %}
                           {% endif %}

                           {% if evidence.limitations %}
                           <p style="font-size: 14px; color: #666; margin-top: 10px;">
                               <strong>Limitations:</strong> {{ evidence.limitations }}
                           </p>
                           {% endif %}
                       </div>
                       {% endif %}
                       {% endfor %}
                   </div>
                   {% endif %}

                   {% if paper.additional_or_contradictory_insights %}
                   <div class="section insights-section">
                       <h3 class="section-title">Additional Insights</h3>
                       {% for insight in paper.additional_or_contradictory_insights %}
                       <div class="insight-item">
                           <strong>{{ insight.finding }}</strong>
                           {% if insight.relevance %}
                           <p style="margin-top: 10px;">{{ insight.relevance }}</p>
                           {% endif %}
                       </div>
                       {% endfor %}
                   </div>
                   {% endif %}
               </div>
               {% endfor %}
           </div>
       </article>

       <!-- Right Citations Column -->
       <div class="citations-container" id="citationsContainer">
           <!-- Dynamic citations will appear here -->
       </div>
   </div>

   <script>
       // State management
       let selectedClaims = new Set();
       let selectedStrengths = new Set(['strong', 'moderate', 'weak']);
       let searchTerm = '';
       let isFiltering = false;

       // Initialize strength checkboxes
       document.addEventListener('DOMContentLoaded', function() {
           document.getElementById('strength-strong').checked = true;
           document.getElementById('strength-moderate').checked = true;
           document.getElementById('strength-weak').checked = true;
           positionNavDots();
           updateActiveNav();
       });

       // Calculate and position nav dots
       function positionNavDots() {
           const dots = document.querySelectorAll('.nav-dot[data-index]');
           const totalDots = dots.length;
           const availableHeight = window.innerHeight * 0.9 - 100;
           const spacing = Math.min(availableHeight / (totalDots + 1), 50);

           dots.forEach((dot, index) => {
               dot.style.top = (50 + (index + 1) * spacing) + 'px';
           });
       }

       // Toggle claim selection
       function toggleClaim(claimNum) {
           const claimElement = document.querySelector(`.claim-option[data-claim="${claimNum}"]`);

           if (selectedClaims.has(claimNum)) {
               selectedClaims.delete(claimNum);
               claimElement.classList.remove('active');
           } else {
               selectedClaims.add(claimNum);
               claimElement.classList.add('active');
           }

           updateActiveFilters();
       }

       // Apply filters
       function applyFilters() {
           isFiltering = true;
           
           // Update selected strengths
           selectedStrengths.clear();
           if (document.getElementById('strength-strong').checked) selectedStrengths.add('strong');
           if (document.getElementById('strength-moderate').checked) selectedStrengths.add('moderate');
           if (document.getElementById('strength-weak').checked) selectedStrengths.add('weak');
           
           // Get search term
           searchTerm = document.getElementById('searchInput').value.toLowerCase();
           
           // Apply filtering
           filterContent();
           updateActiveFilters();
           updateResultsSummary();
       }

       // Filter content based on all active filters
       function filterContent() {
           const papers = document.querySelectorAll('.paper');
           let visiblePapers = 0;
           let matchingEvidence = 0;

           papers.forEach(paper => {
               let paperHasMatch = false;
               
               // Hide all sections initially if filtering
               if (selectedClaims.size > 0 || !selectedStrengths.has('strong') || 
                   !selectedStrengths.has('moderate') || !selectedStrengths.has('weak')) {
                   paper.querySelectorAll('.theory-synthesis-section, .insights-section').forEach(section => {
                       section.style.display = 'none';
                   });
               }
               
               // Check evidence items
               const evidenceItems = paper.querySelectorAll('.evidence-item');
               evidenceItems.forEach(item => {
                   const claimNumber = item.getAttribute('data-claim-number');
                   const strength = item.getAttribute('data-strength');
                   const text = item.textContent.toLowerCase();
                   
                   // Check if matches filters
                   let matchesClaim = selectedClaims.size === 0 || selectedClaims.has(claimNumber);
                   let matchesStrength = selectedStrengths.has(strength);
                   let matchesSearch = !searchTerm || text.includes(searchTerm);
                   
                   if (matchesClaim && matchesStrength && matchesSearch) {
                       item.classList.remove('hidden-by-filter');
                       paperHasMatch = true;
                       matchingEvidence++;
                   } else {
                       item.classList.add('hidden-by-filter');
                   }
               });
               
               // Show/hide paper based on matches
               if (paperHasMatch) {
                   paper.style.display = 'block';
                   paper.classList.add('filtered-result');
                   visiblePapers++;
                   
                   // Check if all evidence is hidden
                   const visibleEvidence = paper.querySelectorAll('.evidence-item:not(.hidden-by-filter)');
                   if (visibleEvidence.length === 0) {
                       paper.querySelector('.evidence-section').style.display = 'none';
                   }
               } else if (selectedClaims.size > 0 || searchTerm) {
                   paper.style.display = 'none';
               } else {
                   paper.style.display = 'block';
                   paper.classList.remove('filtered-result');
                   // Restore sections
                   paper.querySelectorAll('.theory-synthesis-section, .insights-section').forEach(section => {
                       section.style.display = 'block';
                   });
               }
           });

           // Show no results message if needed
           document.getElementById('noResults').style.display = 
               (visiblePapers === 0 && isFiltering) ? 'block' : 'none';
       }

       // Update active filters display
       function updateActiveFilters() {
           const container = document.getElementById('activeFilters');
           container.innerHTML = '';
           
           // Add claim filters
           selectedClaims.forEach(claim => {
               const tag = createFilterTag(`Claim #${claim}`, () => {
                   toggleClaim(claim);
                   applyFilters();
               });
               container.appendChild(tag);
           });
           
           // Add strength filters if not all selected
           const allStrengths = ['strong', 'moderate', 'weak'];
           if (selectedStrengths.size < 3) {
               allStrengths.forEach(strength => {
                   if (!selectedStrengths.has(strength)) {
                       const tag = createFilterTag(`No ${strength}`, () => {
                           document.getElementById(`strength-${strength}`).checked = true;
                           applyFilters();
                       });
                       container.appendChild(tag);
                   }
               });
           }
           
           // Add search filter
           if (searchTerm) {
               const tag = createFilterTag(`Search: "${searchTerm}"`, () => {
                   document.getElementById('searchInput').value = '';
                   searchTerm = '';
                   applyFilters();
               });
               container.appendChild(tag);
           }
       }

       // Create filter tag element
       function createFilterTag(text, onRemove) {
           const tag = document.createElement('div');
           tag.className = 'filter-tag';
           tag.innerHTML = `
               ${text}
               <button onclick="(${onRemove.toString()})()">×</button>
           `;
           return tag;
       }

       // Update results summary
       function updateResultsSummary() {
           const summary = document.getElementById('resultsSummary');
           if (!isFiltering || (selectedClaims.size === 0 && selectedStrengths.size === 3 && !searchTerm)) {
               summary.style.display = 'none';
               return;
           }
           
           const visiblePapers = document.querySelectorAll('.paper:not([style*="display: none"])').length;
           const visibleEvidence = document.querySelectorAll('.evidence-item:not(.hidden-by-filter)').length;
           
           let summaryText = `Showing ${visibleEvidence} evidence item${visibleEvidence !== 1 ? 's' : ''} 
                            from ${visiblePapers} paper${visiblePapers !== 1 ? 's' : ''}`;
           
           summary.textContent = summaryText;
           summary.style.display = 'block';
       }

       // Clear all filters
       function clearAllFilters() {
           selectedClaims.clear();
           document.querySelectorAll('.claim-option').forEach(opt => {
               opt.classList.remove('active');
           });
           
           // Reset strength checkboxes
           document.getElementById('strength-strong').checked = true;
           document.getElementById('strength-moderate').checked = true;
           document.getElementById('strength-weak').checked = true;
           
           // Clear search
           document.getElementById('searchInput').value = '';
           searchTerm = '';
           
           // Reset filtering
           isFiltering = false;
           document.querySelectorAll('.paper').forEach(paper => {
               paper.style.display = 'block';
               paper.classList.remove('filtered-result');
               paper.querySelectorAll('.evidence-item').forEach(item => {
                   item.classList.remove('hidden-by-filter');
               });
               paper.querySelectorAll('.theory-synthesis-section, .insights-section, .evidence-section').forEach(section => {
                   section.style.display = 'block';
               });
           });
           
           updateActiveFilters();
           updateResultsSummary();
           document.getElementById('noResults').style.display = 'none';
       }

       // Search on enter key
       document.getElementById('searchInput').addEventListener('keypress', function(e) {
           if (e.key === 'Enter') {
               applyFilters();
           }
       });

       // Progress bar
       window.addEventListener('scroll', function() {
           const scrollTop = window.scrollY;
           const docHeight = document.documentElement.scrollHeight - window.innerHeight;
           const scrollPercent = (scrollTop / docHeight) * 90;
           document.querySelector('.sidebar-progress').style.height = scrollPercent + '%';
       });

       // Active nav dot based on scroll
       const papers = document.querySelectorAll('.paper[id], #overview');
       const navDots = document.querySelectorAll('.nav-dot');

       function updateActiveNav() {
           let current = 'overview';

           papers.forEach(paper => {
               const rect = paper.getBoundingClientRect();
               if (rect.top <= 100 && rect.bottom > 100) {
                   current = paper.id;
               }
           });

           navDots.forEach(dot => {
               dot.classList.remove('active');
               const href = dot.getAttribute('href');
               if (href === '#' + current) {
                   dot.classList.add('active');
               }
           });
       }

       // Initialize
       window.addEventListener('resize', positionNavDots);
       window.addEventListener('scroll', updateActiveNav);

       // Smooth scroll for nav dots
       navDots.forEach(dot => {
           dot.addEventListener('click', (e) => {
               e.preventDefault();
               const target = document.querySelector(dot.getAttribute('href'));
               if (target) {
                   target.scrollIntoView({ behavior: 'smooth' });
               }
           });
       });
   </script>
</body>
</html>
'''

# Continue with the rest of the Python functions that were already defined...






def get_claim_text(claim_number):
    """Get the full text of a claim by its number"""
    return CONSCIOUSNESS_CLAIMS.get(str(claim_number), f"Claim {claim_number}")


def get_paper_title(paper):
    """Extract paper title handling various formats"""
    if paper.get('paper_metadata'):
        return paper['paper_metadata'].get('title', 'Untitled Paper')
    return 'Analysis Result'


def extract_theory_synthesis(synthesis):
    """Extract theory synthesis handling nested structures"""
    if isinstance(synthesis, dict):
        return synthesis.get('description', str(synthesis))
    return str(synthesis)


def extract_claims_list(claims):
    """Extract claims list from various formats"""
    if not claims:
        return []

    if isinstance(claims, dict):
        # Handle nested structure with 'items' key
        if 'items' in claims:
            items = claims['items']
            if isinstance(items, list):
                return items
            elif isinstance(items, (int, str)):
                return [items]
        # Handle other dict formats
        elif 'type' in claims and claims.get('type') == 'array':
            return claims.get('items', [])
        return []
    elif isinstance(claims, list):
        return claims
    return []


def load_analysis_results():
    """Load all JSON files from the output directory"""
    papers = []

    if not OUTPUT_DIR.exists():
        logger.error(f"Output directory does not exist: {OUTPUT_DIR}")
        return papers, f"Output directory not found: {OUTPUT_DIR}"

    json_files = list(OUTPUT_DIR.glob("*.json"))

    for json_file in json_files:
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
    total_claims = 0
    unique_claims = set()
    total_insights = 0
    claim_counts = {}

    for paper in papers:
        claims = extract_claims_list(paper.get('supported_claims', []))
        total_claims += len(claims)
        unique_claims.update(claims)

        for claim in claims:
            claim_str = str(claim)
            claim_counts[claim_str] = claim_counts.get(claim_str, 0) + 1

        insights = paper.get('additional_or_contradictory_insights', [])
        total_insights += len(insights)

    return {
        'total_claims': total_claims,
        'unique_claims': len(unique_claims),
        'total_insights': total_insights,
        'claim_counts': claim_counts
    }


@app.route('/')
def index():
    """Main page displaying all analysis results"""
    papers, error = load_analysis_results()
    stats = calculate_statistics(papers)
    theory = load_cumulative_theory()  # NEW

    return render_template_string(
        HTML_TEMPLATE,
        papers=papers,
        error=error,
        theory=theory,  # NEW
        get_paper_title=get_paper_title,
        extract_theory_synthesis=extract_theory_synthesis,
        extract_claims_list=extract_claims_list,
        get_claim_text=get_claim_text,
        **stats
    )



if __name__ == '__main__':
    print(f"\nConsciousness Theory Analysis Viewer")
    print(f"Output Directory: {OUTPUT_DIR}")
    print(f"Starting server on http://localhost:5009")

    app.run(debug=True, port=5009, host='0.0.0.0')
