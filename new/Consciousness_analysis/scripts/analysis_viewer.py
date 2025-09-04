#!/usr/bin/env python3
"""
Flask Analysis Viewer - Consciousness Phenomena Analysis
Enhanced with complete evidence display and Fourth Offset design
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

    <!-- Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=EB+Garamond:wght@400;500&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">

    <style>
        /* Font definitions */
        @font-face {
            font-family: 'Palatino';
            src: local('Palatino'), local('Palatino Linotype'), local('Book Antiqua');
            font-weight: 400;
            font-style: normal;
        }

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
            font-family: 'Palatino', Georgia, serif;
            font-size: 18px;
            font-weight: 400;
            line-height: 1.65;
            color: #1a1a1a;
            background: #fff;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
            overflow-x: hidden;
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
            position: relative;
            text-align: left;
            max-width: 900px;
            padding: 80px 60px;
            z-index: 2;
        }

        .title-main {
            font-family: Georgia, serif;
            font-size: 52px;
            font-weight: 900;
            letter-spacing: -0.02em;
            line-height: 1.1;
            color: #fdfde7;
            margin-bottom: 24px;
            text-transform: uppercase;
        }

        .title-subtitle {
            font-family: 'Palatino', Georgia, serif;
            font-size: 20px;
            font-weight: 400;
            color: #fdfde7;
            opacity: 0.9;
            line-height: 1.5;
        }

        /* Scroll Indicator */
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
            top: 0.5%;
            bottom: 0.5%;
            width: 3%;
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 100;
            transition: none;
        }

        .sidebar-track {
            position: absolute;
            width: 1px;
            height: 100%;
            background: #e0e0e0;
        }

        .sidebar-progress {
            position: absolute;
            top: 0;
            width: 1px;
            background: #000;
            height: 0%;
            transition: none !important;
        }

        .nav-dots {
            position: relative;
            height: 90%;
            width: 100%;
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
            align-items: center;
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
            margin-left: 15px;
            max-width: 200px;
            font-size: 13px;
            font-weight: 400;
            color: #666;
            padding: 2px 8px;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.2s ease;
            font-family: 'Palatino', Georgia, serif;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .sidebar:hover .tooltip {
            opacity: 1;
        }

        /* Main Content */
        .main-content {
            margin-left: 12%;
            width: 60%;
            max-width: 980px;
            padding: 80px 0;
        }

        /* Typography */
        h1 {
            font-family: 'Palatino', Georgia, serif;
            font-size: 42px;
            font-weight: 400;
            line-height: 1.2;
            margin-bottom: 32px;
            letter-spacing: -0.01em;
            color: #1a1a1a;
        }

        h2 {
            font-family: 'Palatino', Georgia, serif;
            font-size: 32px;
            font-weight: 400;
            margin-top: 48px;
            margin-bottom: 24px;
            letter-spacing: -0.01em;
            color: #1a1a1a;
        }

        h3 {
            font-family: 'Palatino', Georgia, serif;
            font-size: 24px;
            font-weight: 500;
            margin-top: 32px;
            margin-bottom: 16px;
            color: #1a1a1a;
        }

        p {
            margin-bottom: 16px;
        }

        /* Stats Grid */
        .stats {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 0;
            margin-bottom: 48px;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            overflow: hidden;
        }

        .stat-card {
            text-align: center;
            padding: 24px 16px;
            border-right: 1px solid #e0e0e0;
            background: #fafafa;
        }

        .stat-card:last-child {
            border-right: none;
        }

        .stat-number {
            font-size: 36px;
            font-weight: 500;
            color: #1a1a1a;
            line-height: 1;
            margin-bottom: 8px;
            font-family: 'Inter', sans-serif;
        }

        .stat-label {
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #666;
            font-weight: 500;
            font-family: 'Inter', sans-serif;
        }

        /* Filters Section */
        .filters-section {
            background: #f8f8f8;
            padding: 24px;
            margin-bottom: 32px;
            border-radius: 8px;
            border: 1px solid #e0e0e0;
        }

        .filter-group {
            margin-bottom: 20px;
        }

        .filter-label {
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #666;
            margin-bottom: 12px;
            display: block;
            font-weight: 500;
            font-family: 'Inter', sans-serif;
        }

        input[type="text"] {
            width: 100%;
            padding: 10px 12px;
            font-family: 'Inter', sans-serif;
            font-size: 15px;
            border: 1px solid #d0d0d0;
            border-radius: 6px;
            background: white;
        }

        input[type="text"]:focus {
            outline: none;
            border-color: #666;
        }

        .system-filters {
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
        }

        .filter-option {
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .filter-option input[type="checkbox"] {
            width: 16px;
            height: 16px;
            cursor: pointer;
        }

        .filter-option label {
            cursor: pointer;
            font-size: 15px;
            font-family: 'Inter', sans-serif;
        }

        .filter-buttons {
            display: flex;
            gap: 12px;
            margin-top: 20px;
        }

        .filter-button {
            padding: 8px 20px;
            background: #1a1a1a;
            color: white;
            border: none;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: background 0.2s ease;
            font-family: 'Inter', sans-serif;
        }

        .filter-button:hover {
            background: #333;
        }

        .filter-button.secondary {
            background: #666;
        }

        /* Phenomena Grid */
        .phenomena-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 16px;
            margin: 32px 0;
        }

        .phenomenon-card {
            padding: 20px;
            background: #f8f8f8;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .phenomenon-card:hover {
            background: #f0f0f0;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        }

        .phenomenon-card.active {
            background: #fff;
            border-color: #1a1a1a;
            border-width: 2px;
        }

        .phenomenon-name {
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 8px;
            color: #1a1a1a;
            font-family: 'Inter', sans-serif;
        }

        .phenomenon-description {
            font-size: 14px;
            color: #666;
            line-height: 1.4;
            margin-bottom: 12px;
        }

        .phenomenon-markers {
            font-size: 12px;
            color: #888;
            margin-top: 8px;
        }

        .phenomenon-count {
            display: inline-block;
            padding: 3px 10px;
            background: #1a1a1a;
            color: #fff;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 500;
            font-family: 'Inter', sans-serif;
        }

        .phenomenon-count.zero {
            background: #d0d0d0;
            color: #888;
        }

        /* Papers Section */
        .paper {
            margin-bottom: 48px;
            padding: 32px;
            background: #fff;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            transition: box-shadow 0.2s ease;
        }

        .paper:hover {
            box-shadow: 0 4px 16px rgba(0,0,0,0.06);
        }

        .paper-header {
            margin-bottom: 24px;
            padding-bottom: 16px;
            border-bottom: 1px solid #e0e0e0;
        }

        .paper-title {
            font-size: 26px;
            font-weight: 500;
            margin-bottom: 8px;
            color: #1a1a1a;
            line-height: 1.3;
        }

        .paper-meta {
            font-size: 15px;
            color: #666;
            line-height: 1.5;
        }

        .paper-authors {
            color: #444;
            margin-bottom: 4px;
        }

        .paper-info {
            display: flex;
            gap: 16px;
            flex-wrap: wrap;
            align-items: center;
        }

        .paper-year {
            font-weight: 500;
        }

        .paper-domain {
            display: inline-block;
            padding: 3px 10px;
            background: #f0f0f0;
            border-radius: 4px;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-weight: 500;
            font-family: 'Inter', sans-serif;
        }

        .paper-doi {
            color: #0066cc;
            text-decoration: none;
            font-size: 14px;
        }

        .paper-doi:hover {
            text-decoration: underline;
        }

        /* Evidence Items */
        .evidence-section {
            margin-top: 24px;
        }

        .evidence-item {
            padding: 24px;
            margin: 16px 0;
            background: #fafafa;
            border-left: 3px solid #1a1a1a;
            border-radius: 0 6px 6px 0;
        }

        .evidence-header {
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            margin-bottom: 16px;
            flex-wrap: wrap;
            gap: 12px;
        }

        .evidence-labels {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            align-items: center;
        }

        .phenomenon-badge {
            display: inline-block;
            padding: 4px 12px;
            background: #1a1a1a;
            color: #fff;
            border-radius: 4px;
            font-size: 13px;
            font-weight: 500;
            font-family: 'Inter', sans-serif;
        }

        .system-badge {
            display: inline-block;
            padding: 4px 10px;
            border: 1px solid #666;
            border-radius: 4px;
            font-size: 13px;
            font-weight: 500;
            text-transform: uppercase;
            font-family: 'Inter', sans-serif;
        }

        .system-badge.bio {
            background: #e8f5e9;
            border-color: #4caf50;
            color: #2e7d32;
        }

        .system-badge.ai {
            background: #e3f2fd;
            border-color: #2196f3;
            color: #1565c0;
        }

        .system-badge.other {
            background: #fafafa;
            border-color: #999;
            color: #666;
        }

        .evidence-metadata {
            font-size: 14px;
            color: #666;
            margin-bottom: 12px;
            font-family: 'Inter', sans-serif;
        }

        .evidence-mechanism {
            font-size: 16px;
            line-height: 1.5;
            color: #1a1a1a;
            margin-bottom: 16px;
            font-weight: 500;
        }

        /* Quotes Section */
        .quotes-section {
            margin-top: 16px;
        }

        .quote-item {
            margin: 12px 0;
            padding-left: 16px;
            border-left: 2px solid #d0d0d0;
        }

        .quote-text {
            font-style: italic;
            color: #444;
            line-height: 1.5;
            margin-bottom: 8px;
        }

        .quote-source {
            font-size: 13px;
            color: #888;
            font-family: 'Inter', sans-serif;
        }

        .quote-interpretation {
            margin-top: 8px;
            font-size: 14px;
            color: #555;
            background: #f0f0f0;
            padding: 8px 12px;
            border-radius: 4px;
        }

        /* References Section */
        .references-section {
            margin-top: 16px;
            padding: 16px;
            background: #f8f8f8;
            border-radius: 6px;
        }

        .ref-label {
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #666;
            margin-bottom: 8px;
            font-weight: 500;
            font-family: 'Inter', sans-serif;
        }

        .ref-item {
            margin: 8px 0;
            font-size: 14px;
            color: #444;
        }

        .ref-figure {
            font-weight: 500;
            color: #1a1a1a;
        }

        /* Limitations */
        .limitations {
            margin-top: 16px;
            padding: 12px;
            background: #fff3e0;
            border-left: 3px solid #ff9800;
            border-radius: 0 4px 4px 0;
            font-size: 14px;
            color: #666;
        }

        /* No Results */
        .no-results {
            text-align: center;
            padding: 60px 20px;
            color: #666;
            font-style: italic;
        }

        /* Citations Container */
        .citations-container {
            position: absolute;
            left: 74%;
            width: 22%;
            top: 80px;
            padding-right: 40px;
        }

        .citation-item {
            padding: 16px 20px;
            font-family: 'Palatino', Georgia, serif;
            font-size: 14px;
            line-height: 1.4;
            color: #444;
            border-top: 1px solid #626F61;
            background: white;
            margin-bottom: -1px;
        }

        /* Mobile Menu Toggle */
        .mobile-menu-toggle {
            display: none;
            position: fixed;
            top: 20px;
            left: 20px;
            width: 30px;
            height: 30px;
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            cursor: pointer;
            z-index: 202;
            padding: 0;
        }

        .mobile-menu-toggle span {
            display: block;
            width: 16px;
            height: 1px;
            background: #1a1a1a;
            position: absolute;
            left: 50%;
            transition: all 0.3s ease;
        }

        .mobile-menu-toggle span:nth-child(1) {
            transform: translate(-50%, -6px);
        }

        .mobile-menu-toggle span:nth-child(2) {
            transform: translate(-50%, -2px);
        }

        .mobile-menu-toggle span:nth-child(3) {
            transform: translate(-50%, 2px);
        }

        .mobile-menu-toggle span:nth-child(4) {
            transform: translate(-50%, 6px);
        }

        .mobile-menu-toggle.active span:nth-child(1),
        .mobile-menu-toggle.active span:nth-child(4) {
            opacity: 0;
        }

        .mobile-menu-toggle.active span:nth-child(2) {
            transform: translate(-50%, 0) rotate(45deg);
        }

        .mobile-menu-toggle.active span:nth-child(3) {
            transform: translate(-50%, 0) rotate(-45deg);
        }

        /* Mobile Overlay */
        .mobile-overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            z-index: 98;
            opacity: 0;
            visibility: hidden;
            transition: opacity 0.3s ease, visibility 0.3s ease;
        }

        .mobile-overlay.active {
            display: block;
            opacity: 1;
            visibility: visible;
        }

        /* Responsive */
        @media (max-width: 1200px) {
            .main-content {
                margin-left: 8%;
                width: 70%;
            }

            .citations-container {
                display: none;
            }
        }

        @media (max-width: 768px) {
            .title-main {
                font-size: 32px;
            }

            .title-subtitle {
                font-size: 18px;
            }

            .mobile-menu-toggle {
                display: block;
            }

            .sidebar {
                position: fixed;
                width: 200px;
                left: -200px;
                top: 0;
                bottom: 0;
                background: white;
                box-shadow: 2px 0 5px rgba(0,0,0,0.1);
                transition: left 0.3s ease;
            }

            .sidebar.active {
                left: 0;
            }

            .sidebar.active .nav-dots {
                padding: 20px;
            }

            .sidebar.active .tooltip {
                position: relative;
                left: auto;
                margin-left: 10px;
                opacity: 1;
                max-width: none;
            }

            .main-content {
                margin-left: 0;
                width: 100%;
                padding: 60px 20px;
            }

            .phenomena-grid {
                grid-template-columns: 1fr;
            }

            .stats {
                grid-template-columns: repeat(2, 1fr);
            }

            h1 {
                font-size: 32px;
            }

            h2 {
                font-size: 26px;
            }

            .paper {
                padding: 20px;
            }
        }
    </style>
</head>
<body>
    <!-- Mobile Menu Toggle -->
    <button class="mobile-menu-toggle" id="mobileMenuToggle">
        <span></span>
        <span></span>
        <span></span>
        <span></span>
    </button>

    <!-- Title Page -->
    <div class="title-page" id="title-page">
        <div class="title-content">
            <h1 class="title-main">Consciousness Phenomena Analysis</h1>
            <p class="title-subtitle">Systematic evidence mapping across 9 core phenomena<br>in biological and artificial intelligence systems</p>
        </div>
        <div class="scroll-indicator" onclick="document.getElementById('overview').scrollIntoView({behavior: 'smooth'})">
            <div class="scroll-arrow"></div>
        </div>
    </div>

    <!-- Content Container -->
    <div class="content-container">
        <!-- Sidebar Navigation -->
        <nav class="sidebar" id="sidebar">
            <div class="sidebar-track"></div>
            <div class="sidebar-progress"></div>
            <div class="nav-dots">
                <a href="#overview" class="nav-dot active">
                    <span class="tooltip">Overview</span>
                </a>
                <a href="#phenomena" class="nav-dot">
                    <span class="tooltip">Phenomena</span>
                </a>
                <a href="#papers" class="nav-dot">
                    <span class="tooltip">Papers</span>
                </a>
            </div>
        </nav>

        <!-- Main Content -->
        <article class="main-content">
            <section id="overview">
                <h1>Analysis Overview</h1>

                <!-- Statistics -->
                <div class="stats">
                    <div class="stat-card">
                        <div class="stat-number">{{ papers|length }}</div>
                        <div class="stat-label">Papers Analyzed</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{{ total_evidence }}</div>
                        <div class="stat-label">Evidence Items</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{{ phenomena_count }}</div>
                        <div class="stat-label">Active Phenomena</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{{ unique_systems }}</div>
                        <div class="stat-label">System Types</div>
                    </div>
                </div>

                <!-- Filters -->
                <div class="filters-section">
                    <div class="filter-group">
                        <label class="filter-label">Search Papers & Evidence</label>
                        <input type="text" id="searchInput" placeholder="Search by title, author, phenomenon, quotes...">
                    </div>

                    <div class="filter-group">
                        <label class="filter-label">Filter by System Type</label>
                        <div class="system-filters">
                            <div class="filter-option">
                                <input type="checkbox" id="system-bio" checked>
                                <label for="system-bio">Biological</label>
                            </div>
                            <div class="filter-option">
                                <input type="checkbox" id="system-ai" checked>
                                <label for="system-ai">AI/Computational</label>
                            </div>
                            <div class="filter-option">
                                <input type="checkbox" id="system-other" checked>
                                <label for="system-other">Theoretical/Other</label>
                            </div>
                        </div>
                    </div>

                    <div class="filter-buttons">
                        <button class="filter-button" onclick="applyFilters()">Apply Filters</button>
                        <button class="filter-button secondary" onclick="clearFilters()">Clear All</button>
                    </div>
                </div>
            </section>

            <!-- Phenomena Section -->
            <section id="phenomena">
                <h2>Core Consciousness Phenomena</h2>
                <p style="color: #666; margin-bottom: 24px;">Click on phenomena cards to filter evidence by specific phenomena</p>

                <div class="phenomena-grid">
                    {% for pid, pdata in phenomena.items() %}
                    <div class="phenomenon-card" data-phenomenon="{{ pid }}" onclick="togglePhenomenon('{{ pid }}')">
                        <div class="phenomenon-name">{{ pdata.name }}</div>
                        <div class="phenomenon-description">{{ pdata.description }}</div>
                        <div class="phenomenon-markers">
                            <strong>Bio:</strong> {{ pdata.biological_markers[:2]|join(', ') }}...<br>
                            <strong>AI:</strong> {{ pdata.ai_markers[:2]|join(', ') }}...
                        </div>
                        <span class="phenomenon-count {% if phenomenon_counts.get(pid, 0) == 0 %}zero{% endif %}">
                            {{ phenomenon_counts.get(pid, 0) }} evidence items
                        </span>
                    </div>
                    {% endfor %}
                </div>
            </section>

            <!-- Papers Section -->
            <section id="papers">
                <h2>Analyzed Papers</h2>

                <div id="noResults" class="no-results" style="display: none;">
                    No evidence found matching your filters. Try adjusting your selection.
                </div>

                {% for paper in papers %}
                <div class="paper" data-paper-index="{{ loop.index0 }}">
                    <div class="paper-header">
                        <h3 class="paper-title">
                            {{ paper.paper_metadata.title if paper.paper_metadata else 'Untitled Paper' }}
                        </h3>
                        <div class="paper-meta">
                            {% if paper.paper_metadata %}
                                {% if paper.paper_metadata.authors %}
                                <div class="paper-authors">
                                    {{ paper.paper_metadata.authors|join(', ') }}
                                </div>
                                {% endif %}
                                <div class="paper-info">
                                    {% if paper.paper_metadata.year %}
                                    <span class="paper-year">{{ paper.paper_metadata.year }}</span>
                                    {% endif %}
                                    {% if paper.paper_metadata.domain %}
                                    <span class="paper-domain">{{ paper.paper_metadata.domain }}</span>
                                    {% endif %}
                                    {% if paper.paper_metadata.doi_or_arxiv %}
                                    <a href="https://doi.org/{{ paper.paper_metadata.doi_or_arxiv }}" 
                                       target="_blank" class="paper-doi">
                                        DOI: {{ paper.paper_metadata.doi_or_arxiv }}
                                    </a>
                                    {% endif %}
                                </div>
                            {% endif %}
                        </div>
                    </div>

                    <!-- Evidence Items -->
                    {% if paper.evidence %}
                    <div class="evidence-section">
                        <h4 style="font-size: 18px; margin-bottom: 16px; color: #444;">Evidence Items ({{ paper.evidence|length }})</h4>

                        {% for item in paper.evidence %}
                        <div class="evidence-item" 
                             data-phenomenon="{{ item.phenomenon_id }}"
                             data-system="{{ item.system_type }}">

                            <div class="evidence-header">
                                <div class="evidence-labels">
                                    <span class="phenomenon-badge">
                                        {{ phenomena[item.phenomenon_id].name if item.phenomenon_id in phenomena else item.phenomenon_id }}
                                    </span>
                                    <span class="system-badge {{ item.system_type }}">
                                        {{ item.system_type|upper }}
                                    </span>
                                </div>
                            </div>

                            <div class="evidence-metadata">
                                <strong>Species/Model:</strong> {{ item.species_or_model }} | 
                                <strong>Method:</strong> {{ item.method }} | 
                                <strong>State:</strong> {{ item.state }}
                                {% if item.time %}
                                    {% if item.time.bio_ms %}
                                    | <strong>Time:</strong> {{ item.time.bio_ms }}ms
                                    {% endif %}
                                    {% if item.time.ai_units %}
                                        {% if item.time.ai_units.layers %}
                                        | <strong>Layers:</strong> {{ item.time.ai_units.layers }}
                                        {% endif %}
                                        {% if item.time.ai_units.tokens %}
                                        | <strong>Tokens:</strong> {{ item.time.ai_units.tokens }}
                                        {% endif %}
                                    {% endif %}
                                {% endif %}
                            </div>

                            <div class="evidence-mechanism">
                                {{ item.brief_mechanism }}
                            </div>

                            <!-- Text References/Quotes -->
                            {% if item.text_refs %}
                            <div class="quotes-section">
                                {% for ref in item.text_refs[:3] %}
                                <div class="quote-item">
                                    <div class="quote-text">
                                        "{{ ref.quote }}"
                                    </div>
                                    <div class="quote-source">
                                        — {{ ref.section_title }} ({{ ref.section_type }})
                                        {% if ref.page %}, p. {{ ref.page }}{% endif %}
                                    </div>
                                    {% if ref.interpretation %}
                                    <div class="quote-interpretation">
                                        <strong>Interpretation:</strong> {{ ref.interpretation }}
                                    </div>
                                    {% endif %}
                                </div>
                                {% endfor %}
                                {% if item.text_refs|length > 3 %}
                                <div style="font-size: 13px; color: #888; margin-top: 8px;">
                                    + {{ item.text_refs|length - 3 }} more quotes...
                                </div>
                                {% endif %}
                            </div>
                            {% endif %}

                            <!-- Figures and Tables -->
                            {% if item.figure_refs or item.table_refs %}
                            <div class="references-section">
                                {% if item.figure_refs %}
                                <div class="ref-label">Figures:</div>
                                {% for fig in item.figure_refs %}
                                <div class="ref-item">
                                    <span class="ref-figure">{{ fig.figure_label }}</span>
                                    {% if fig.page %}(p. {{ fig.page }}){% endif %}
                                    {% if fig.interpretation_short %}: {{ fig.interpretation_short }}{% endif %}
                                </div>
                                {% endfor %}
                                {% endif %}

                                {% if item.table_refs %}
                                <div class="ref-label" style="margin-top: 12px;">Tables:</div>
                                {% for table in item.table_refs %}
                                <div class="ref-item">
                                    <span class="ref-figure">{{ table.table_label }}</span>
                                    {% if table.page %}(p. {{ table.page }}){% endif %}
                                    {% if table.caption_quote %}: {{ table.caption_quote[:100] }}...{% endif %}
                                </div>
                                {% endfor %}
                                {% endif %}
                            </div>
                            {% endif %}

                            <!-- Limitations -->
                            {% if item.limitations %}
                            <div class="limitations">
                                <strong>Limitations:</strong> {{ item.limitations }}
                            </div>
                            {% endif %}
                        </div>
                        {% endfor %}
                    </div>
                    {% else %}
                    <p style="color: #888; font-style: italic;">No evidence items found in this analysis.</p>
                    {% endif %}
                </div>
                {% endfor %}
            </section>
        </article>

        <!-- Citations Container -->
        <div class="citations-container">
            <div class="citation-item">
                <strong>Analysis Generated:</strong><br>
                {{ datetime.now().strftime('%B %d, %Y') }}<br><br>
                <strong>Source:</strong><br>
                Consciousness Phenomena Framework<br><br>
                <strong>Papers Analyzed:</strong> {{ papers|length }}<br>
                <strong>Total Evidence:</strong> {{ total_evidence }}
            </div>
        </div>
    </div>

    <!-- Mobile Overlay -->
    <div class="mobile-overlay" id="mobileOverlay"></div>

    <script>
        // State management
        let sidebarOpen = false;
        let selectedPhenomena = new Set();
        let selectedSystems = new Set(['bio', 'ai', 'other']);
        let searchTerm = '';

        // Mobile menu toggle
        const mobileToggle = document.getElementById('mobileMenuToggle');
        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('mobileOverlay');

        if (mobileToggle) {
            mobileToggle.addEventListener('click', () => {
                sidebarOpen = !sidebarOpen;
                mobileToggle.classList.toggle('active');
                sidebar.classList.toggle('active');
                overlay.classList.toggle('active');
                document.body.style.overflow = sidebarOpen ? 'hidden' : '';
            });
        }

        if (overlay) {
            overlay.addEventListener('click', () => {
                sidebarOpen = false;
                mobileToggle.classList.remove('active');
                sidebar.classList.remove('active');
                overlay.classList.remove('active');
                document.body.style.overflow = '';
            });
        }

        // Navigation
        document.querySelectorAll('.nav-dot').forEach(dot => {
            dot.addEventListener('click', (e) => {
                e.preventDefault();
                const target = document.querySelector(dot.getAttribute('href'));
                if (target) {
                    if (sidebarOpen) {
                        mobileToggle.classList.remove('active');
                        sidebar.classList.remove('active');
                        overlay.classList.remove('active');
                        document.body.style.overflow = '';
                        sidebarOpen = false;
                    }
                    target.scrollIntoView({ behavior: 'smooth' });
                }
            });
        });

        // Phenomenon filtering
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

            // Filter papers and evidence
            const papers = document.querySelectorAll('.paper');
            let visiblePapers = 0;

            papers.forEach(paper => {
                let paperHasMatch = false;
                const paperText = paper.textContent.toLowerCase();
                const matchesSearch = !searchTerm || paperText.includes(searchTerm);

                if (matchesSearch) {
                    const evidenceItems = paper.querySelectorAll('.evidence-item');

                    evidenceItems.forEach(item => {
                        const phenomenon = item.getAttribute('data-phenomenon');
                        const system = item.getAttribute('data-system');

                        const matchesPhenomenon = selectedPhenomena.size === 0 || selectedPhenomena.has(phenomenon);
                        const matchesSystem = selectedSystems.has(system);

                        if (matchesPhenomenon && matchesSystem) {
                            item.style.display = 'block';
                            paperHasMatch = true;
                        } else {
                            item.style.display = 'none';
                        }
                    });
                }

                if (paperHasMatch && matchesSearch) {
                    paper.style.display = 'block';
                    visiblePapers++;
                } else {
                    paper.style.display = 'none';
                }
            });

            // Show/hide no results message
            document.getElementById('noResults').style.display = 
                visiblePapers === 0 ? 'block' : 'none';
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
        document.getElementById('searchInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                applyFilters();
            }
        });

        // Progress bar
        function updateProgress() {
            const scrollTop = window.scrollY;
            const docHeight = document.documentElement.scrollHeight - window.innerHeight;
            const scrollPercent = (scrollTop / docHeight) * 90;

            const progressBar = document.querySelector('.sidebar-progress');
            if (progressBar) {
                progressBar.style.height = scrollPercent + '%';
            }
        }

        // Active nav dot
        function updateActiveNav() {
            const sections = document.querySelectorAll('section[id]');
            const navDots = document.querySelectorAll('.nav-dot');
            const scrollTop = window.scrollY + 100;

            let current = '';
            sections.forEach(section => {
                const sectionTop = section.offsetTop;
                if (scrollTop >= sectionTop) {
                    current = section.getAttribute('id');
                }
            });

            navDots.forEach(dot => {
                dot.classList.remove('active');
                if (dot.getAttribute('href') === '#' + current) {
                    dot.classList.add('active');
                }
            });
        }

        // Position nav dots
        function positionNavDots() {
            const dots = document.querySelectorAll('.nav-dot');
            const availableHeight = window.innerHeight * 0.9;
            const spacing = Math.min(availableHeight / (dots.length + 1), 80);

            dots.forEach((dot, index) => {
                dot.style.top = (50 + index * spacing) + 'px';
            });
        }

        // Event listeners
        window.addEventListener('scroll', () => {
            updateProgress();
            updateActiveNav();
        });

        window.addEventListener('resize', positionNavDots);

        // Initialize
        document.addEventListener('DOMContentLoaded', () => {
            positionNavDots();
            updateProgress();
            updateActiveNav();
        });
    </script>
</body>
</html>
'''

# Import datetime for the template
from datetime import datetime


def load_analysis_results():
    """Load all JSON files from the output directory"""
    papers = []

    if not OUTPUT_DIR.exists():
        logger.error(f"Output directory does not exist: {OUTPUT_DIR}")
        return papers, "Output directory not found"

    json_files = list(OUTPUT_DIR.glob("*.json"))

    for json_file in json_files:
        if json_file.name == "processed_papers.json":
            continue

        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                papers.append(data)
        except Exception as e:
            logger.error(f"Error loading {json_file.name}: {str(e)}")

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
            phenomenon_id = item.get('phenomenon_id')
            if phenomenon_id:
                phenomenon_counts[phenomenon_id] = phenomenon_counts.get(phenomenon_id, 0) + 1

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
        unique_systems=stats['unique_systems'],
        datetime=datetime  # Pass datetime to template
    )


if __name__ == '__main__':
    print(f"\nConsciousness Phenomena Analysis Viewer")
    print(f"Output Directory: {OUTPUT_DIR}")
    print(f"Starting server on http://localhost:5009")

    app.run(debug=True, port=5009, host='0.0.0.0')
