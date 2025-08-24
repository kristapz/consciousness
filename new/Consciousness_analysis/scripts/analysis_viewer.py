#!/usr/bin/env python3
"""
Flask Analysis Viewer - Enhanced JSON Display for Consciousness Theory Analysis
Complete version with all data shown, advanced filtering, and compact design
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

# Enhanced HTML Template with compact design and advanced filtering
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Consciousness Theory Analysis Viewer</title>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.4;
            color: #333;
            background-color: #f5f7fa;
            font-size: 13px;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 15px;
        }

        header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1.25rem;
            border-radius: 8px;
            margin-bottom: 1.25rem;
            box-shadow: 0 3px 5px rgba(0,0,0,0.1);
        }

        h1 {
            font-size: 1.75rem;
            margin-bottom: 0.25rem;
        }

        .subtitle {
            font-size: 0.9rem;
            opacity: 0.9;
        }

        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 0.75rem;
            margin-bottom: 1.25rem;
        }

        .stat-card {
            background: white;
            padding: 1rem;
            border-radius: 6px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.08);
            text-align: center;
        }

        .stat-number {
            font-size: 1.5rem;
            font-weight: bold;
            color: #667eea;
        }

        .stat-label {
            color: #666;
            font-size: 0.75rem;
            margin-top: 0.25rem;
        }

        .claims-index {
            background: white;
            padding: 1rem;
            border-radius: 6px;
            margin-bottom: 1.25rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.08);
        }

        .filters {
            background: white;
            padding: 1rem;
            border-radius: 6px;
            margin-bottom: 1.25rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.08);
        }

        .filter-row {
            display: flex;
            gap: 0.75rem;
            align-items: center;
            flex-wrap: wrap;
            margin-bottom: 0.75rem;
        }

        .filter-row:last-child {
            margin-bottom: 0;
        }

        .filter-label {
            font-weight: 600;
            color: #555;
            min-width: 60px;
            font-size: 0.85rem;
        }

        input[type="text"], select {
            padding: 0.4rem;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 0.85rem;
        }

        input[type="number"] {
            width: 80px;
            padding: 0.4rem;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 0.85rem;
        }

        .checkbox-group {
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
        }

        .checkbox-item {
            display: flex;
            align-items: center;
            gap: 0.25rem;
            font-size: 0.85rem;
        }

        .checkbox-item input[type="checkbox"] {
            cursor: pointer;
        }

        .paper {
            background: white;
            border-radius: 6px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.08);
            margin-bottom: 1rem;
            overflow: hidden;
            transition: transform 0.2s, box-shadow 0.2s;
        }

        .paper:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 10px rgba(0,0,0,0.12);
        }

        .paper-header {
            background: #f8f9fa;
            padding: 1rem;
            border-bottom: 1px solid #e9ecef;
        }

        .paper-title {
            font-size: 1.1rem;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 0.25rem;
        }

        .paper-link {
            color: #667eea;
            text-decoration: none;
            font-size: 0.75rem;
            word-break: break-all;
        }

        .paper-link:hover {
            text-decoration: underline;
        }

        .paper-meta {
            display: flex;
            gap: 1rem;
            margin-top: 0.5rem;
            font-size: 0.75rem;
            color: #666;
        }

        .paper-body {
            padding: 1rem;
        }

        .section {
            margin-bottom: 1rem;
        }

        .section-title {
            font-weight: 600;
            color: #495057;
            margin-bottom: 0.5rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.95rem;
        }

        .section-icon {
            width: 18px;
            height: 18px;
            background: #667eea;
            border-radius: 50%;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 0.7rem;
            flex-shrink: 0;
        }

        .theory-synthesis {
            background: #f1f3f5;
            padding: 0.75rem;
            border-radius: 5px;
            font-style: italic;
            color: #495057;
            font-size: 0.85rem;
        }

        .theory-type {
            font-size: 0.75rem;
            color: #888;
            margin-top: 0.25rem;
            font-style: normal;
        }

        .claims-container {
            display: flex;
            flex-wrap: wrap;
            gap: 0.4rem;
            margin-top: 0.4rem;
        }

        .claim-tag-full {
            background: #e3f2fd;
            color: #1976d2;
            padding: 0.4rem 0.8rem;
            border-radius: 6px;
            font-size: 0.75rem;
            margin: 0.3rem 0;
            display: block;
            border: 1px solid #bbdefb;
        }

        .claim-number {
            font-weight: 700;
            margin-right: 0.4rem;
        }

        .claim-text {
            color: #1565c0;
        }

        .claim-tag {
            background: #e3f2fd;
            color: #1976d2;
            padding: 0.2rem 0.6rem;
            border-radius: 15px;
            font-size: 0.75rem;
            font-weight: 500;
        }

        .evidence-item {
            background: #f8f9fa;
            border-left: 3px solid #667eea;
            padding: 0.75rem;
            margin: 0.5rem 0;
            border-radius: 0 4px 4px 0;
        }

        .evidence-claim {
            font-weight: 600;
            color: #495057;
            margin-bottom: 0.4rem;
            font-size: 0.85rem;
        }

        .quote {
            background: white;
            padding: 0.5rem;
            margin: 0.4rem 0;
            border-radius: 4px;
            font-size: 0.8rem;
            color: #555;
            border: 1px solid #e9ecef;
        }

        .quote-text {
            font-style: italic;
        }

        .quote-source {
            font-size: 0.7rem;
            color: #888;
            margin-top: 0.2rem;
        }

        .strength-badge {
            display: inline-block;
            padding: 0.15rem 0.4rem;
            border-radius: 3px;
            font-size: 0.7rem;
            font-weight: 500;
            margin-left: 0.5rem;
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

        .insights {
            background: #f8f9fa;
            padding: 0.75rem;
            border-radius: 5px;
        }

        .insight-item {
            margin-bottom: 0.75rem;
            padding-bottom: 0.75rem;
            border-bottom: 1px solid #dee2e6;
        }

        .insight-item:last-child {
            margin-bottom: 0;
            padding-bottom: 0;
            border-bottom: none;
        }

        .insight-item strong {
            font-size: 0.85rem;
        }

        .insight-item p {
            font-size: 0.8rem;
        }

        details {
            margin-top: 0.5rem;
        }

        details.json-details {
            margin-top: 1rem;
            border-top: 1px solid #e9ecef;
            padding-top: 0.75rem;
        }

        summary {
            cursor: pointer;
            color: #667eea;
            font-weight: 500;
            outline: none;
            user-select: none;
            font-size: 0.85rem;
        }

        summary:hover {
            text-decoration: underline;
        }

        summary::-webkit-details-marker {
            color: #667eea;
        }

        details[open] summary {
            margin-bottom: 0.5rem;
        }

        pre {
            background: #f8f9fa;
            padding: 0.75rem;
            border-radius: 4px;
            overflow-x: auto;
            font-size: 0.75rem;
            margin-top: 0.5rem;
        }

        .no-results {
            text-align: center;
            padding: 2rem;
            color: #666;
        }

        .error {
            background: #f8d7da;
            color: #721c24;
            padding: 0.75rem;
            border-radius: 4px;
            margin-bottom: 0.75rem;
            font-size: 0.85rem;
        }

        .empty-state {
            color: #999;
            font-style: italic;
            font-size: 0.8rem;
        }

        .filter-stats {
            text-align: right;
            color: #666;
            font-size: 0.75rem;
            margin-top: 0.5rem;
        }

        /* Style options with different counts */
        #claimSelect option[data-count="0"] {
            color: #999;
        }

        #claimSelect option[data-count]:not([data-count="0"]) {
            font-weight: 500;
        }

        .hidden {
            display: none !important;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Consciousness Theory Analysis Viewer</h1>
            <p class="subtitle">Exploring scientific papers through the lens of consciousness-related claims</p>
        </header>

        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{{ papers|length }}</div>
                <div class="stat-label">Papers Analyzed</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ total_claims }}</div>
                <div class="stat-label">Total Claims Supported</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ unique_claims }}</div>
                <div class="stat-label">Unique Claims</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ total_insights }}</div>
                <div class="stat-label">Additional Insights</div>
            </div>
        </div>

        <div class="claims-index">
            <h3 style="font-size: 1rem; margin-bottom: 0.75rem; color: #495057;">
                <span class="section-icon" style="vertical-align: middle;">C</span>
                Claims Index
            </h3>
            <select id="claimSelect" style="width: 100%; padding: 0.5rem; font-size: 0.85rem;">
                <option value="">Select a claim to filter papers...</option>
                <optgroup label="Ion Channels (1-5)">
                    {% for num in range(1, 6) %}
                    <option value="{{ num }}" data-count="{{ claim_counts.get(num|string, 0) }}">
                        #{{ num }} ({{ claim_counts.get(num|string, 0) }} papers): {{ get_claim_text(num)[:80] }}...
                    </option>
                    {% endfor %}
                </optgroup>
                <optgroup label="Cytoskeleton (6-12)">
                    {% for num in range(6, 13) %}
                    <option value="{{ num }}" data-count="{{ claim_counts.get(num|string, 0) }}">
                        #{{ num }} ({{ claim_counts.get(num|string, 0) }} papers): {{ get_claim_text(num)[:80] }}...
                    </option>
                    {% endfor %}
                </optgroup>
                <optgroup label="EM Fields (13-22)">
                    {% for num in range(13, 23) %}
                    <option value="{{ num }}" data-count="{{ claim_counts.get(num|string, 0) }}">
                        #{{ num }} ({{ claim_counts.get(num|string, 0) }} papers): {{ get_claim_text(num)[:80] }}...
                    </option>
                    {% endfor %}
                </optgroup>
                <optgroup label="Microtubules (23-32)">
                    {% for num in range(23, 33) %}
                    <option value="{{ num }}" data-count="{{ claim_counts.get(num|string, 0) }}">
                        #{{ num }} ({{ claim_counts.get(num|string, 0) }} papers): {{ get_claim_text(num)[:80] }}...
                    </option>
                    {% endfor %}
                </optgroup>
                <optgroup label="Signaling Pathways (33-38)">
                    {% for num in range(33, 39) %}
                    <option value="{{ num }}" data-count="{{ claim_counts.get(num|string, 0) }}">
                        #{{ num }} ({{ claim_counts.get(num|string, 0) }} papers): {{ get_claim_text(num)[:80] }}...
                    </option>
                    {% endfor %}
                </optgroup>
                <optgroup label="Perturbation Experiments (39-50)">
                    {% for num in range(39, 51) %}
                    <option value="{{ num }}" data-count="{{ claim_counts.get(num|string, 0) }}">
                        #{{ num }} ({{ claim_counts.get(num|string, 0) }} papers): {{ get_claim_text(num)[:80] }}...
                    </option>
                    {% endfor %}
                </optgroup>
            </select>
            <div style="margin-top: 0.5rem; font-size: 0.75rem; color: #666;">
                <span id="claimDescription"></span>
            </div>
        </div>

        <div class="filters">
            <div class="filter-row">
                <span class="filter-label">Search:</span>
                <input type="text" id="searchInput" placeholder="Search papers, claims, quotes, or claim number (e.g., 12)..." style="flex: 1;">
                <span class="filter-label">Sort:</span>
                <select id="sortSelect">
                    <option value="date">Date (Newest)</option>
                    <option value="date-asc">Date (Oldest)</option>
                    <option value="claims">Claim Count</option>
                    <option value="title">Title A-Z</option>
                    <option value="insights">Insights Count</option>
                </select>
            </div>

            <div class="filter-row">
                <span class="filter-label">Strength:</span>
                <div class="checkbox-group">
                    <label class="checkbox-item">
                        <input type="checkbox" class="strength-filter" value="strong" checked>
                        Strong
                    </label>
                    <label class="checkbox-item">
                        <input type="checkbox" class="strength-filter" value="moderate" checked>
                        Moderate
                    </label>
                    <label class="checkbox-item">
                        <input type="checkbox" class="strength-filter" value="weak" checked>
                        Weak
                    </label>
                    <label class="checkbox-item">
                        <input type="checkbox" class="strength-filter" value="none" checked>
                        No Evidence
                    </label>
                </div>
            </div>

            <div class="filter-row">
                <span class="filter-label">Claims:</span>
                <input type="number" id="minClaims" placeholder="Min" min="0">
                <span style="margin: 0 0.5rem;">to</span>
                <input type="number" id="maxClaims" placeholder="Max" min="0">

                <span class="filter-label" style="margin-left: 1rem;">Model:</span>
                <select id="modelFilter">
                    <option value="all">All Models</option>
                    <option value="gpt-5">GPT-5</option>
                    <option value="gpt-5-mini">GPT-5 Mini</option>
                    <option value="gpt-5-nano">GPT-5 Nano</option>
                </select>

                <span class="filter-label" style="margin-left: 1rem;">Has Insights:</span>
                <select id="insightsFilter">
                    <option value="all">All</option>
                    <option value="yes">Yes</option>
                    <option value="no">No</option>
                </select>
            </div>

            <div class="filter-stats" id="filterStats">
                Showing <span id="visibleCount">{{ papers|length }}</span> of {{ papers|length }} papers
            </div>
        </div>

        <div id="papersContainer">
            {% if error %}
            <div class="error">{{ error }}</div>
            {% endif %}

            {% if papers %}
                {% for paper in papers %}
                <div class="paper" data-paper-index="{{ loop.index0 }}" 
                     data-claims-count="{{ extract_claims_list(paper.supported_claims)|length }}"
                     data-insights-count="{{ (paper.additional_or_contradictory_insights or [])|length }}"
                     data-model="{{ paper._metadata.model_used if paper._metadata else 'unknown' }}"
                     data-strengths="{{ get_paper_strengths(paper) }}">
                    <div class="paper-header">
                        {% if paper.paper_metadata %}
                            <h2 class="paper-title">
                                {{ paper.paper_metadata.title or 'Untitled Paper' }}
                            </h2>
                            {% if paper.paper_metadata.link %}
                            <a href="{{ paper.paper_metadata.link }}" target="_blank" class="paper-link">
                                {{ paper.paper_metadata.link }}
                            </a>
                            {% endif %}
                        {% else %}
                            <h2 class="paper-title">Analysis Result {{ loop.index }}</h2>
                        {% endif %}

                        <div class="paper-meta">
                            {% if paper._metadata %}
                                <span>Model: {{ paper._metadata.model_used }}</span>
                                <span>Analyzed: {{ format_timestamp(paper._metadata.analysis_timestamp) }}</span>
                            {% endif %}
                            {% if paper._filename %}
                                <span>File: {{ paper._filename }}</span>
                            {% endif %}
                        </div>
                    </div>

                    <div class="paper-body">
                        {% if paper.theory_synthesis %}
                        <div class="section">
                            <h3 class="section-title">
                                <span class="section-icon">T</span>
                                Theory Synthesis
                            </h3>
                            <div class="theory-synthesis">
                                {% if paper.theory_synthesis is mapping %}
                                    {{ paper.theory_synthesis.description or paper.theory_synthesis }}
                                    {% if paper.theory_synthesis.type %}
                                    <div class="theory-type">Type: {{ paper.theory_synthesis.type }}</div>
                                    {% endif %}
                                {% else %}
                                    {{ paper.theory_synthesis }}
                                {% endif %}
                            </div>
                        </div>
                        {% endif %}

                        {% set claims_list = extract_claims_list(paper.supported_claims) %}
                        {% if claims_list %}
                        <div class="section">
                            <h3 class="section-title">
                                <span class="section-icon">{{ claims_list|length }}</span>
                                Supported Claims
                            </h3>
                            <div class="claims-container">
                                {% for claim in claims_list %}
                                <div class="claim-tag-full" data-claim-number="{{ claim }}">
                                    <span class="claim-number">#{{ claim }}:</span>
                                    <span class="claim-text">{{ get_claim_text(claim) }}</span>
                                </div>
                                {% endfor %}
                            </div>
                        </div>
                        {% else %}
                        <div class="section">
                            <h3 class="section-title">
                                <span class="section-icon">0</span>
                                Supported Claims
                            </h3>
                            <p class="empty-state">No claims were supported by evidence in this paper</p>
                        </div>
                        {% endif %}

                        {% if paper.evidence_details and paper.evidence_details|length > 0 %}
                        <div class="section evidence-section">
                            <h3 class="section-title">
                                <span class="section-icon">E</span>
                                Evidence Details
                                <span class="evidence-count" style="font-size: 0.75rem; color: #666; margin-left: 0.5rem;">
                                    (<span class="visible-evidence-count">{{ paper.evidence_details|length }}</span> of {{ paper.evidence_details|length }})
                                </span>
                            </h3>
                            <details open>
                                <summary>View evidence</summary>
                                {% for claim_num, evidence in paper.evidence_details.items() %}
                                <div class="evidence-item" data-strength="{{ evidence.strength|lower if evidence.strength else 'none' }}">
                                    <div class="evidence-claim">
                                        Claim #{{ claim_num }}: {{ evidence.claim_text }}
                                        {% if evidence.strength %}
                                        <span class="strength-badge strength-{{ evidence.strength }}">
                                            {{ evidence.strength|upper }}
                                        </span>
                                        {% endif %}
                                    </div>

                                    {% if evidence.interpretation %}
                                    <p style="margin: 0.4rem 0; font-size: 0.8rem;">{{ evidence.interpretation }}</p>
                                    {% endif %}

                                    {% if evidence.direct_quotes %}
                                    <details open>
                                        <summary style="margin: 0.4rem 0;">
                                            Quotes ({{ evidence.direct_quotes|length }})
                                        </summary>
                                        {% for quote_obj in evidence.direct_quotes %}
                                        <div class="quote">
                                            <div class="quote-text">"{{ quote_obj.quote }}"</div>
                                            {% if quote_obj.page_or_section %}
                                            <div class="quote-source">— {{ quote_obj.page_or_section }}</div>
                                            {% endif %}
                                        </div>
                                        {% endfor %}
                                    </details>
                                    {% endif %}

                                    {% if evidence.limitations %}
                                    <p style="font-size: 0.75rem; color: #666; margin-top: 0.4rem;">
                                        <strong>Limitations:</strong> {{ evidence.limitations }}
                                    </p>
                                    {% endif %}
                                </div>
                                {% endfor %}
                                <div class="no-evidence-message hidden" style="padding: 1rem; text-align: center; color: #999; font-style: italic;">
                                    No evidence matches the selected strength filters
                                </div>
                            </details>
                        </div>
                        {% endif %}

                        {% if paper.additional_or_contradictory_insights and paper.additional_or_contradictory_insights|length > 0 %}
                        <div class="section">
                            <h3 class="section-title">
                                <span class="section-icon">!</span>
                                Additional Insights ({{ paper.additional_or_contradictory_insights|length }})
                            </h3>
                            <details open>
                                <summary>View all {{ paper.additional_or_contradictory_insights|length }} insights</summary>
                                <div class="insights">
                                    {% for insight in paper.additional_or_contradictory_insights %}
                                    <div class="insight-item">
                                        <strong>{{ insight.finding }}</strong>
                                        {% if insight.relevance %}
                                        <p style="margin-top: 0.4rem;">
                                            {{ insight.relevance }}
                                        </p>
                                        {% endif %}
                                        {% if insight.quotes %}
                                        <details style="margin-top: 0.4rem;">
                                            <summary style="font-size: 0.8rem;">
                                                Quotes ({{ insight.quotes|length }})
                                            </summary>
                                            {% for quote in insight.quotes %}
                                            <div class="quote" style="margin-top: 0.4rem;">
                                                <div class="quote-text">"{{ quote }}"</div>
                                            </div>
                                            {% endfor %}
                                        </details>
                                        {% endif %}
                                    </div>
                                    {% endfor %}
                                </div>
                            </details>
                        </div>
                        {% endif %}

                        <details class="json-details">
                            <summary>View Complete JSON Data</summary>
                            <pre>{{ paper|tojson(indent=2) }}</pre>
                        </details>
                    </div>
                </div>
                {% endfor %}
            {% else %}
                <div class="no-results">
                    <h2>No analysis results found</h2>
                    <p>Make sure JSON files are present in: {{ output_dir }}</p>
                </div>
            {% endif %}
        </div>
    </div>

    <script>
        // DOM elements
        const searchInput = document.getElementById('searchInput');
        const sortSelect = document.getElementById('sortSelect');
        const claimSelect = document.getElementById('claimSelect');
        const claimDescription = document.getElementById('claimDescription');
        const strengthFilters = document.querySelectorAll('.strength-filter');
        const minClaimsInput = document.getElementById('minClaims');
        const maxClaimsInput = document.getElementById('maxClaims');
        const modelFilter = document.getElementById('modelFilter');
        const insightsFilter = document.getElementById('insightsFilter');
        const visibleCountSpan = document.getElementById('visibleCount');
        const papers = document.querySelectorAll('.paper');

        // Event listeners
        searchInput.addEventListener('input', applyFilters);
        sortSelect.addEventListener('change', sortPapers);
        claimSelect.addEventListener('change', handleClaimSelect);
        strengthFilters.forEach(filter => filter.addEventListener('change', applyFilters));
        minClaimsInput.addEventListener('input', applyFilters);
        maxClaimsInput.addEventListener('input', applyFilters);
        modelFilter.addEventListener('change', applyFilters);
        insightsFilter.addEventListener('change', applyFilters);

        // Claim descriptions
        const claimDescriptions = {{ CONSCIOUSNESS_CLAIMS|tojson }};

        function handleClaimSelect() {
            const selectedClaim = claimSelect.value;
            if (selectedClaim) {
                // Update search input with claim number
                searchInput.value = selectedClaim;

                // Show full claim description
                claimDescription.textContent = `Full claim: ${claimDescriptions[selectedClaim]}`;

                // Apply filters
                applyFilters();
            } else {
                claimDescription.textContent = '';
                searchInput.value = '';
                applyFilters();
            }
        }

        function applyFilters() {
            const searchTerm = searchInput.value.toLowerCase();
            const selectedStrengths = Array.from(strengthFilters)
                .filter(cb => cb.checked)
                .map(cb => cb.value);
            const minClaims = parseInt(minClaimsInput.value) || 0;
            const maxClaims = parseInt(maxClaimsInput.value) || Infinity;
            const selectedModel = modelFilter.value;
            const insightsRequired = insightsFilter.value;

            let visibleCount = 0;

            papers.forEach(paper => {
                // Search filter - enhanced to search claim numbers
                const text = paper.textContent.toLowerCase();
                const searchTermLower = searchTerm.toLowerCase();

                // Check if search term is a claim number
                let matchesSearch = !searchTerm || text.includes(searchTermLower);

                // Special handling for numeric searches (claim numbers)
                if (searchTerm && /^\d+$/.test(searchTerm)) {
                    const claimNumber = searchTerm;
                    const hasClaimNumber = paper.querySelector(`[data-claim-number="${claimNumber}"]`) !== null ||
                                         paper.querySelector(`.evidence-item .evidence-claim`)?.textContent.includes(`Claim #${claimNumber}:`);
                    matchesSearch = hasClaimNumber;
                }

                // Claims filter
                const claimsCount = parseInt(paper.dataset.claimsCount);
                const matchesClaims = claimsCount >= minClaims && claimsCount <= maxClaims;

                // Model filter
                const matchesModel = selectedModel === 'all' || 
                    paper.dataset.model === selectedModel;

                // Insights filter
                const insightsCount = parseInt(paper.dataset.insightsCount);
                const matchesInsights = insightsRequired === 'all' ||
                    (insightsRequired === 'yes' && insightsCount > 0) ||
                    (insightsRequired === 'no' && insightsCount === 0);

                // Apply strength filter to individual evidence items
                const evidenceItems = paper.querySelectorAll('.evidence-item');
                let hasVisibleEvidence = false;
                let visibleEvidenceCount = 0;

                evidenceItems.forEach(item => {
                    const itemStrength = item.dataset.strength || 'none';
                    if (selectedStrengths.includes(itemStrength)) {
                        item.classList.remove('hidden');
                        hasVisibleEvidence = true;
                        visibleEvidenceCount++;
                    } else {
                        item.classList.add('hidden');
                    }
                });

                // Update evidence count display
                const evidenceSection = paper.querySelector('.evidence-section');
                if (evidenceSection) {
                    const countSpan = evidenceSection.querySelector('.visible-evidence-count');
                    const noEvidenceMsg = evidenceSection.querySelector('.no-evidence-message');

                    if (countSpan) {
                        countSpan.textContent = visibleEvidenceCount;
                    }

                    if (noEvidenceMsg) {
                        if (visibleEvidenceCount === 0 && evidenceItems.length > 0) {
                            noEvidenceMsg.classList.remove('hidden');
                        } else {
                            noEvidenceMsg.classList.add('hidden');
                        }
                    }
                }

                // For papers with no evidence, check if "none" is selected
                if (evidenceItems.length === 0) {
                    hasVisibleEvidence = selectedStrengths.includes('none');
                }

                // Show/hide paper based on all filters
                if (matchesSearch && hasVisibleEvidence && matchesClaims && 
                    matchesModel && matchesInsights) {
                    paper.classList.remove('hidden');
                    visibleCount++;
                } else {
                    paper.classList.add('hidden');
                }
            });

            // Update count
            visibleCountSpan.textContent = visibleCount;
        }

        function sortPapers() {
            const sortBy = sortSelect.value;
            const container = document.getElementById('papersContainer');
            const papersArray = Array.from(papers);

            papersArray.sort((a, b) => {
                switch(sortBy) {
                    case 'date':
                        const dateA = a.querySelector('.paper-meta')?.textContent || '';
                        const dateB = b.querySelector('.paper-meta')?.textContent || '';
                        return dateB.localeCompare(dateA);
                    case 'date-asc':
                        const dateAscA = a.querySelector('.paper-meta')?.textContent || '';
                        const dateAscB = b.querySelector('.paper-meta')?.textContent || '';
                        return dateAscA.localeCompare(dateAscB);
                    case 'claims':
                        const claimsA = parseInt(a.dataset.claimsCount);
                        const claimsB = parseInt(b.dataset.claimsCount);
                        return claimsB - claimsA;
                    case 'title':
                        const titleA = a.querySelector('.paper-title')?.textContent || '';
                        const titleB = b.querySelector('.paper-title')?.textContent || '';
                        return titleA.localeCompare(titleB);
                    case 'insights':
                        const insightsA = parseInt(a.dataset.insightsCount);
                        const insightsB = parseInt(b.dataset.insightsCount);
                        return insightsB - insightsA;
                    default:
                        return 0;
                }
            });

            // Re-append papers in sorted order
            papersArray.forEach(paper => container.appendChild(paper));
        }

        // Initialize
        applyFilters();
    </script>
</body>
</html>
'''


def get_claim_text(claim_number):
    """Get the full text of a claim by its number"""
    return CONSCIOUSNESS_CLAIMS.get(str(claim_number), f"Claim {claim_number} (text not found)")


def format_timestamp(timestamp):
    """Format ISO timestamp to readable date"""
    if not timestamp:
        return 'Unknown date'
    try:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M')
    except:
        return timestamp


def extract_claims_list(claims):
    """Extract claims list from various formats"""
    if not claims:
        return []

    if isinstance(claims, dict):
        if 'items' in claims:
            items = claims['items']
            if isinstance(items, list):
                return items
            elif isinstance(items, (int, str)):
                return [items]
        return []
    elif isinstance(claims, list):
        return claims
    return []


def get_paper_strengths(paper):
    """Extract all strength values from a paper for filtering"""
    strengths = set()

    # Check evidence details for strength values
    evidence_details = paper.get('evidence_details', {})
    if evidence_details:
        for evidence in evidence_details.values():
            strength = evidence.get('strength', '').lower()
            if strength:
                strengths.add(strength)

    # If no evidence, mark as 'none'
    if not strengths:
        strengths.add('none')

    return ','.join(strengths)


def load_analysis_results():
    """Load all JSON files from the output directory"""
    papers = []
    errors = []

    if not OUTPUT_DIR.exists():
        logger.error(f"Output directory does not exist: {OUTPUT_DIR}")
        return papers, f"Output directory not found: {OUTPUT_DIR}"

    json_files = list(OUTPUT_DIR.glob("*.json"))

    if not json_files:
        logger.warning(f"No JSON files found in: {OUTPUT_DIR}")
        return papers, None

    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                data['_filename'] = json_file.name
                papers.append(data)
                logger.info(f"Loaded: {json_file.name}")
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON in {json_file.name}: {str(e)}"
            logger.error(error_msg)
            errors.append(error_msg)
        except Exception as e:
            error_msg = f"Error loading {json_file.name}: {str(e)}"
            logger.error(error_msg)
            errors.append(error_msg)

    # Sort by timestamp if available
    papers.sort(key=lambda p: p.get('_metadata', {}).get('analysis_timestamp', ''), reverse=True)

    error_summary = " | ".join(errors) if errors else None
    return papers, error_summary


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

        # Count papers per claim
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

    # Add helper functions to template context
    return render_template_string(
        HTML_TEMPLATE,
        papers=papers,
        error=error,
        output_dir=OUTPUT_DIR,
        format_timestamp=format_timestamp,
        extract_claims_list=extract_claims_list,
        get_paper_strengths=get_paper_strengths,
        get_claim_text=get_claim_text,
        CONSCIOUSNESS_CLAIMS=CONSCIOUSNESS_CLAIMS,
        **stats
    )


@app.route('/api/papers')
def api_papers():
    """API endpoint returning papers as JSON"""
    papers, error = load_analysis_results()
    return jsonify({
        'papers': papers,
        'error': error,
        'count': len(papers)
    })


@app.route('/api/statistics')
def api_statistics():
    """API endpoint returning statistics"""
    papers, _ = load_analysis_results()
    stats = calculate_statistics(papers)
    stats['paper_count'] = len(papers)
    return jsonify(stats)


@app.route('/api/claims')
def api_claims():
    """API endpoint returning claim distribution"""
    papers, _ = load_analysis_results()
    claim_counts = {}

    for paper in papers:
        claims = extract_claims_list(paper.get('supported_claims', []))
        for claim in claims:
            claim_counts[str(claim)] = claim_counts.get(str(claim), 0) + 1

    return jsonify({
        'claim_distribution': claim_counts,
        'total_unique_claims': len(claim_counts)
    })


@app.errorhandler(404)
def not_found(error):
    return "Page not found", 404


@app.errorhandler(500)
def internal_error(error):
    return f"Internal server error: {str(error)}", 500


if __name__ == '__main__':
    print(f"\n{'=' * 60}")
    print("Consciousness Theory Analysis Viewer")
    print(f"{'=' * 60}")
    print(f"Project Root: {PROJECT_ROOT}")
    print(f"Output Directory: {OUTPUT_DIR}")
    print(f"Output Dir Exists: {OUTPUT_DIR.exists()}")

    if OUTPUT_DIR.exists():
        json_files = list(OUTPUT_DIR.glob("*.json"))
        print(f"JSON Files Found: {len(json_files)}")
        for f in json_files[:5]:
            print(f"  - {f.name}")
        if len(json_files) > 5:
            print(f"  ... and {len(json_files) - 5} more")

    print(f"\nStarting Flask server on http://localhost:5009")
    print(f"{'=' * 60}\n")

    app.run(debug=True, port=5009, host='0.0.0.0')