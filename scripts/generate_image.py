#!/usr/bin/env python3
"""
scripts/generate_image.py
Generates the 1024x1024 editorial news poster for Monday, 23 November 2026.
Bakes /workspace/news-image-20261123/entry.png deterministically.
"""

import os
import sys
import time
import hashlib
from PIL import Image

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
OUTPUT_PNG = os.path.join(PROJECT_DIR, "entry.png")
TMP_HTML = "/tmp/news_entry_render.html"
TMP_PNG = "/tmp/news_entry_chrome.png"

HTML_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<style>
  * {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }
  @page {
    size: 1024px 1024px;
    margin: 0;
  }
  html, body {
    width: 1024px;
    height: 1024px;
    overflow: hidden;
    background: #f5efe6;
    color: #1a1714;
    font-family: 'IBM Plex Sans', 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    -webkit-font-smoothing: antialiased;
  }

  .broadsheet {
    width: 1024px;
    height: 1024px;
    padding: 10px 14px 10px 14px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    background: #f6f0e7;
    position: relative;
  }

  /* 1. HEADER SECTION */
  .header-masthead {
    border-bottom: 2px solid #221e1a;
    padding-bottom: 4px;
    flex-shrink: 0;
  }
  .top-meta {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 8.5px;
    font-weight: 700;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    color: #5c544d;
    border-bottom: 1px solid #d8cfc4;
    padding-bottom: 2px;
  }
  .top-meta .flag {
    color: #8b0000;
    font-weight: 800;
  }
  .masthead-main {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    margin: 2px 0 1px 0;
  }
  .masthead-date {
    font-family: 'DM Serif Display', 'Newsreader', 'Libre Baskerville', serif;
    font-size: 38px;
    line-height: 44px;
    font-weight: 900;
    letter-spacing: -0.5px;
    color: #161311;
    text-transform: capitalize;
  }
  .masthead-edition {
    text-align: right;
    font-size: 8.5px;
    line-height: 11px;
    font-weight: 600;
    color: #4a423a;
  }
  .sub-leads {
    font-family: 'IBM Plex Serif', 'Libre Baskerville', serif;
    font-size: 9.8px;
    line-height: 12px;
    font-style: italic;
    color: #2b2520;
    border-top: 1px solid #221e1a;
    padding-top: 3px;
    margin-top: 2px;
    display: flex;
    justify-content: space-between;
  }

  /* 2. REGION PILLS */
  .region-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: #eae2d5;
    border: 1px solid #cfc4b4;
    border-radius: 3px;
    padding: 3px 6px;
    margin-top: 4px;
    flex-shrink: 0;
  }
  .region-pill {
    font-size: 7.8px;
    font-weight: 700;
    letter-spacing: 0.4px;
    text-transform: uppercase;
    color: #38312a;
  }
  .region-pill span {
    background: #2b2520;
    color: #fff;
    padding: 0 4px;
    border-radius: 2px;
    font-size: 7px;
    margin-left: 2px;
  }

  /* 3. UTC TIMELINE */
  .timeline-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: #221d18;
    color: #e5ded5;
    border-radius: 2px;
    padding: 3px 6px;
    margin-top: 4px;
    font-size: 7.4px;
    flex-shrink: 0;
  }
  .timeline-title {
    font-weight: 800;
    color: #f59e0b;
    letter-spacing: 0.8px;
    margin-right: 6px;
  }
  .time-stop {
    display: flex;
    align-items: center;
    gap: 3px;
  }
  .time-tag {
    font-weight: 700;
    color: #fcd34d;
  }

  /* 4. DAY IN NUMBERS */
  .numbers-bar {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 4px;
    margin-top: 4px;
    flex-shrink: 0;
  }
  .num-card {
    background: #fdfcf9;
    border: 1px solid #cfc4b4;
    border-top: 2px solid #8b0000;
    border-radius: 2px;
    padding: 2px 4px;
    text-align: center;
  }
  .num-val {
    font-family: 'DM Serif Display', 'IBM Plex Serif', serif;
    font-size: 14.5px;
    line-height: 15px;
    font-weight: 900;
    color: #8b0000;
  }
  .num-lbl {
    font-size: 6.8px;
    line-height: 8.5px;
    font-weight: 600;
    color: #38312a;
    margin-top: 1px;
  }

  /* 5. ILLUSTRATED CARDS GRID (15 CARDS, 5x3) */
  .cards-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    grid-template-rows: repeat(3, 136px);
    gap: 5px;
    margin-top: 5px;
    flex-shrink: 0;
  }
  .card {
    background: #fdfbf7;
    border: 1px solid #d2c7b7;
    border-radius: 3px;
    padding: 4px 5px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    overflow: hidden;
  }
  .card-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 7.2px;
    font-weight: 700;
    text-transform: uppercase;
    color: #524a42;
    margin-bottom: 2px;
    border-bottom: 1px dashed #ded4c5;
    padding-bottom: 2px;
  }
  .card-num {
    background: #1a1714;
    color: #fff;
    width: 13px;
    height: 13px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 7px;
    margin-right: 3px;
  }
  .loc-topic {
    display: flex;
    align-items: center;
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
  }

  /* BADGES */
  .badge {
    font-size: 6.5px;
    font-weight: 800;
    padding: 1px 3px;
    border-radius: 2px;
    text-transform: uppercase;
    letter-spacing: 0.3px;
  }
  .badge-confirmed { background: #fee2e2; color: #991b1b; border: 1px solid #f87171; }
  .badge-official  { background: #e0e7ff; color: #3730a3; border: 1px solid #818cf8; }
  .badge-reported  { background: #fef3c7; color: #92400e; border: 1px solid #fcd34d; }
  .badge-ongoing   { background: #ffedd5; color: #9a3412; border: 1px solid #fb923c; }
  .badge-claim     { background: #f3e8ff; color: #6b21a8; border: 1px solid #c084fc; }

  .card-art {
    width: 100%;
    height: 38px;
    background: #f1ebd8;
    border: 1px solid #e2d9c8;
    border-radius: 2px;
    margin-bottom: 2px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .card-headline {
    font-family: 'DM Serif Display', 'IBM Plex Serif', serif;
    font-size: 9.2px;
    line-height: 10.8px;
    font-weight: 700;
    color: #161311;
    margin-bottom: 2px;
  }
  .card-body {
    font-size: 7.2px;
    line-height: 9.2px;
    color: #38312a;
    flex-grow: 1;
  }
  .card-src {
    font-size: 6.2px;
    color: #786f66;
    text-align: right;
    margin-top: 1px;
    font-style: italic;
  }

  /* 6. ALSO ON MONDAY + MAP ROW */
  .also-map-row {
    display: flex;
    gap: 6px;
    margin-top: 5px;
    height: 162px;
    flex-shrink: 0;
  }
  .also-panel {
    width: 650px;
    background: #fdfbf7;
    border: 1px solid #d2c7b7;
    border-radius: 3px;
    padding: 4px 6px;
    display: flex;
    flex-direction: column;
  }
  .panel-header {
    font-family: 'IBM Plex Sans', 'Inter', sans-serif;
    font-size: 10.5px;
    line-height: 13px;
    font-weight: 700;
    letter-spacing: 0.1px;
    text-transform: uppercase;
    color: #1a1714;
    font-variant-numeric: lining-nums tabular-nums;
    border-bottom: 1px solid #221d18;
    padding-bottom: 2px;
    margin-bottom: 3px;
    display: flex;
    justify-content: space-between;
  }
  .also-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    grid-template-rows: repeat(5, 1fr);
    gap: 3px 6px;
    flex-grow: 1;
  }
  .also-item {
    font-size: 7.1px;
    line-height: 9px;
    color: #2b2520;
    display: flex;
    align-items: flex-start;
  }
  .also-num {
    background: #2b2520;
    color: #fff;
    font-size: 6.5px;
    font-weight: 700;
    min-width: 12px;
    height: 12px;
    border-radius: 50%;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    margin-right: 3px;
    flex-shrink: 0;
    margin-top: 0.5px;
  }
  .also-text {
    flex-grow: 1;
  }
  .also-text strong {
    color: #161311;
  }
  .also-tag {
    font-size: 6px;
    font-weight: 700;
    color: #6b21a8;
  }

  .map-panel {
    width: 340px;
    background: #fdfbf7;
    border: 1px solid #d2c7b7;
    border-radius: 3px;
    padding: 4px 6px;
    display: flex;
    flex-direction: column;
  }
  .map-container {
    width: 100%;
    height: 134px;
    background: #ede6d8;
    border: 1px solid #ded5c5;
    border-radius: 2px;
    position: relative;
    overflow: hidden;
  }

  /* 7. FOOTER SECTION: DATE CHECK + HOW SURE */
  .footer-row {
    display: flex;
    gap: 6px;
    margin-top: 5px;
    height: 108px;
    flex-shrink: 0;
  }
  .year {
    font-family: 'IBM Plex Sans', 'Inter', sans-serif;
    font-size: 10.5px;
    font-weight: 700;
    letter-spacing: 0.1px;
    font-variant-numeric: lining-nums tabular-nums;
  }
  .date-check-box {
    width: 650px;
    background: #fdfcf9;
    border: 1px solid #b91c1c;
    border-radius: 3px;
    padding: 4px 6px;
    font-size: 7.8px;
    line-height: 10px;
    color: #2b2520;
    font-variant-numeric: lining-nums tabular-nums;
  }
  .date-check-title {
    font-family: 'IBM Plex Sans', 'Inter', sans-serif;
    font-size: 10.5px;
    line-height: 13px;
    font-weight: 700;
    color: #b91c1c;
    letter-spacing: 0.1px;
    text-transform: uppercase;
    font-variant-numeric: lining-nums tabular-nums;
    margin-bottom: 2px;
  }
  .date-check-box strong {
    color: #161311;
  }

  .how-sure-box {
    width: 340px;
    background: #fdfcf9;
    border: 1px solid #cfc4b4;
    border-radius: 3px;
    padding: 4px 6px;
    font-size: 6.8px;
    line-height: 8.8px;
    color: #38312a;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }
  .how-sure-title {
    font-weight: 800;
    color: #1a1714;
    letter-spacing: 0.6px;
    text-transform: uppercase;
    border-bottom: 1px solid #d8cfc4;
    padding-bottom: 1px;
    margin-bottom: 2px;
  }
  .colophon {
    font-size: 6.4px;
    color: #786f66;
    border-top: 1px solid #d8cfc4;
    padding-top: 1px;
    margin-top: 1px;
    text-align: right;
  }
</style>
</head>
<body>
<div class="broadsheet">

  <!-- 1. HEADER SECTION -->
  <div class="header-masthead">
    <div class="top-meta">
      <div>THE WORLD IN ONE DAY · VERIFIED GLOBAL BROADSHEET</div>
      <div class="flag">30 DATED STORIES · 9 REGIONS · STRICT UTC VERIFICATION</div>
      <div>PRICE: OPEN RECORD · ED. <span class="year">2026</span>.11.23</div>
    </div>
    <div class="masthead-main">
      <div class="masthead-date">Monday 23 November 2026</div>
      <div class="masthead-edition">
        FINAL GLOBAL COMPILATION<br>
        ALL EVENTS REPORTED ON THIS ONE DAY
      </div>
    </div>
    <div class="sub-leads">
      <span>Ukraine confirms 7 drones sank corvette Merkury at Benghazi</span>
      <span>·</span>
      <span>Dymer rescue ends, toll 11</span>
      <span>·</span>
      <span>COP31 fallout: Bowen faces resignation calls</span>
      <span>·</span>
      <span>Huang reinstated at Nvidia (+31.5%)</span>
    </div>
  </div>

  <!-- 2. REGION PILLS -->
  <div class="region-row">
    <div class="region-pill">Europe <span>7</span></div>
    <div class="region-pill">Middle East <span>3</span></div>
    <div class="region-pill">Africa <span>3</span></div>
    <div class="region-pill">South Asia <span>3</span></div>
    <div class="region-pill">East Asia <span>4</span></div>
    <div class="region-pill">Southeast Asia <span>3</span></div>
    <div class="region-pill">Americas <span>3</span></div>
    <div class="region-pill">Oceania / Climate <span>2</span></div>
    <div class="region-pill">Caucasus / Space <span>2</span></div>
  </div>

  <!-- 3. UTC TIMELINE -->
  <div class="timeline-bar">
    <span class="timeline-title">THE DAY IN UTC</span>
    <div class="time-stop"><span class="time-tag">06:12</span> COP31 fallout files</div>
    <div>·</div>
    <div class="time-stop"><span class="time-tag">Morn</span> 450 German school hoaxes</div>
    <div>·</div>
    <div class="time-stop"><span class="time-tag">Midday</span> NATO AWACS to Poland</div>
    <div>·</div>
    <div class="time-stop"><span class="time-tag">13:59</span> Nvidia rehires Huang</div>
    <div>·</div>
    <div class="time-stop"><span class="time-tag">15:30</span> Centurion Day 1 (BAN 91)</div>
    <div>·</div>
    <div class="time-stop"><span class="time-tag">Eve</span> Spain SC shelves Puigdemont</div>
  </div>

  <!-- 4. DAY IN NUMBERS -->
  <div class="numbers-bar">
    <div class="num-card">
      <div class="num-val">7</div>
      <div class="num-lbl">Naval drones sank corvette Merkury</div>
    </div>
    <div class="num-card">
      <div class="num-val">11</div>
      <div class="num-lbl">Dymer dead as rescue concludes</div>
    </div>
    <div class="num-card">
      <div class="num-val">24</div>
      <div class="num-lbl">Dead at Cikande factory fire toll</div>
    </div>
    <div class="num-card">
      <div class="num-val">450</div>
      <div class="num-lbl">German schools emailed threats</div>
    </div>
    <div class="num-card">
      <div class="num-val">+31.5%</div>
      <div class="num-lbl">Nvidia stock surge (+$1T value)</div>
    </div>
    <div class="num-card">
      <div class="num-val">$1.62B</div>
      <div class="num-lbl">India-Nepal aid package agreed</div>
    </div>
    <div class="num-card">
      <div class="num-val">91</div>
      <div class="num-lbl">Bangladesh all out at Centurion</div>
    </div>
  </div>

  <!-- 5. 15 ILLUSTRATED LEAD CARDS (5x3 GRID) -->
  <div class="cards-grid">

    <!-- Card 1: Benghazi -->
    <div class="card">
      <div class="card-top">
        <div class="loc-topic"><div class="card-num">1</div>BENGHAZI · WAR</div>
        <div class="badge badge-confirmed">CONFIRMED</div>
      </div>
      <div class="card-art">
        <svg viewBox="0 0 180 36" width="100%" height="100%">
          <rect width="180" height="36" fill="#ded5c5"/>
          <path d="M0 26 Q45 23 90 26 T180 26 L180 36 L0 36 Z" fill="#7a8b99"/>
          <!-- Corvette silhouette listing -->
          <path d="M35 24 L50 16 L120 16 L145 22 L140 26 L30 26 Z" fill="#2b333c" transform="rotate(7 90 22)"/>
          <rect x="75" y="10" width="16" height="8" fill="#1b222a"/>
          <line x1="83" y1="5" x2="83" y2="10" stroke="#1b222a" stroke-width="1.5"/>
          <!-- Drone explosion splash -->
          <circle cx="125" cy="18" r="8" fill="#e25822" opacity="0.8"/>
          <circle cx="125" cy="18" r="4" fill="#ffdd55"/>
          <!-- Drone trails -->
          <path d="M165 30 L135 21" stroke="#fff" stroke-dasharray="2 2" stroke-width="1.2"/>
        </svg>
      </div>
      <div class="card-headline">Ukraine Confirms Sinking of Russian Corvette Merkury</div>
      <div class="card-body">Zelenskyy & SBU confirm Monday: 7 naval drones launched from mothership sank corvette Merkury in Sunday strike at Benghazi base; MV Angara also hit. UNSMIL urges probe.</div>
      <div class="card-src">Reuters · AP · The Guardian</div>
    </div>

    <!-- Card 2: Dymer -->
    <div class="card">
      <div class="card-top">
        <div class="loc-topic"><div class="card-num">2</div>DYMER · WAR</div>
        <div class="badge badge-official">OFFICIAL</div>
      </div>
      <div class="card-art">
        <svg viewBox="0 0 180 36" width="100%" height="100%">
          <rect width="180" height="36" fill="#ded5c5"/>
          <!-- Ruined building -->
          <rect x="30" y="8" width="55" height="24" fill="#4a423a"/>
          <path d="M45 8 L60 20 L75 8 Z" fill="#ded5c5"/>
          <!-- Search beam & emergency personnel -->
          <polygon points="120,4 165,28 110,28" fill="#fef08a" opacity="0.35"/>
          <rect x="135" y="18" width="18" height="12" fill="#c2410c"/>
          <circle cx="144" cy="15" r="3" fill="#1e293b"/>
        </svg>
      </div>
      <div class="card-headline">Dymer Rescue Concludes as Strike Toll Rises to 11</div>
      <div class="card-body">Search-and-rescue ends Monday after Sunday's Russian drone strike on a 5-storey apartment building. Toll rose from 6 to 11, including a child; 2 survivors pulled from rubble.</div>
      <div class="card-src">Ukrinform · Interfax-Ukraine</div>
    </div>

    <!-- Card 3: COP31 Fallout -->
    <div class="card">
      <div class="card-top">
        <div class="loc-topic"><div class="card-num">3</div>ANTALYA / SYDNEY</div>
        <div class="badge badge-confirmed">CONFIRMED</div>
      </div>
      <div class="card-art">
        <svg viewBox="0 0 180 36" width="100%" height="100%">
          <rect width="180" height="36" fill="#ded5c5"/>
          <!-- Podium and broken globe -->
          <rect x="75" y="16" width="30" height="18" fill="#334155"/>
          <circle cx="90" cy="10" r="7" fill="#0284c7"/>
          <path d="M85 8 Q90 12 95 10" stroke="#fff" stroke-width="1.2" fill="none"/>
          <!-- Resignation gavel / crack -->
          <line x1="88" y1="3" x2="92" y2="17" stroke="#b91c1c" stroke-width="1.5"/>
          <text x="120" y="22" font-size="8" font-weight="bold" fill="#b91c1c">NO DEAL</text>
        </svg>
      </div>
      <div class="card-headline">Bowen Faces Resignation Calls After COP31 Collapse</div>
      <div class="card-body">Monday political storm in Australia after COP31 closed Sunday with no deal. Angus Taylor demands Bowen quit; Albanese defends him. Marshall Islands: "let down on all sides."</div>
      <div class="card-src">Reuters · SMH · Guardian</div>
    </div>

    <!-- Card 4: Nvidia -->
    <div class="card">
      <div class="card-top">
        <div class="loc-topic"><div class="card-num">4</div>SANTA CLARA · TECH</div>
        <div class="badge badge-confirmed">CONFIRMED</div>
      </div>
      <div class="card-art">
        <svg viewBox="0 0 180 36" width="100%" height="100%">
          <rect width="180" height="36" fill="#ded5c5"/>
          <!-- Semiconductor chip & soaring chart -->
          <rect x="25" y="8" width="22" height="22" fill="#15803d" rx="2"/>
          <rect x="30" y="13" width="12" height="12" fill="#22c55e"/>
          <path d="M65 28 L95 20 L125 22 L155 7" fill="none" stroke="#16a34a" stroke-width="2.5"/>
          <polygon points="155,7 148,8 152,14" fill="#16a34a"/>
          <text x="100" y="14" font-size="8" font-weight="bold" fill="#15803d">+31.5%</text>
        </svg>
      </div>
      <div class="card-headline">Huang Reinstated as Nvidia CEO; Shares Surge 31.5%</div>
      <div class="card-body">Nvidia rehires Jensen Huang Monday following Donald Trump intervention. Shares jump 31.5%, adding ~$1T in market value. Board rules no national security risk; lawmakers raise questions.</div>
      <div class="card-src">Reuters 13:59 UTC · CNBC</div>
    </div>

    <!-- Card 5: NATO AWACS -->
    <div class="card">
      <div class="card-top">
        <div class="loc-topic"><div class="card-num">5</div>WARSAW · SECURITY</div>
        <div class="badge badge-confirmed">CONFIRMED</div>
      </div>
      <div class="card-art">
        <svg viewBox="0 0 180 36" width="100%" height="100%">
          <rect width="180" height="36" fill="#ded5c5"/>
          <!-- AWACS Radar Plane -->
          <ellipse cx="90" cy="14" rx="14" ry="4" fill="#1e293b"/>
          <path d="M50 20 L80 18 L130 18 L140 22 L50 22 Z" fill="#475569"/>
          <path d="M85 18 L95 28 L90 28 Z" fill="#334155"/>
          <!-- Radar waves -->
          <path d="M110 10 A8 8 0 0 1 120 18" stroke="#0284c7" stroke-width="1.2" fill="none"/>
          <path d="M115 6 A14 14 0 0 1 130 18" stroke="#0284c7" stroke-width="1.2" fill="none"/>
        </svg>
      </div>
      <div class="card-headline">NATO Deploys AWACS Radar Plane to Poland</div>
      <div class="card-body">Monday decision: NATO deploys AWACS early-warning jet to Poland after three Russian Kh-101 missiles landed on Polish soil Friday. SACEUR Gen. Grynkewich authorised mission.</div>
      <div class="card-src">Reuters, Warsaw</div>
    </div>

    <!-- Card 6: German Schools -->
    <div class="card">
      <div class="card-top">
        <div class="loc-topic"><div class="card-num">6</div>GERMANY / DENMARK</div>
        <div class="badge badge-reported">REPORTED</div>
      </div>
      <div class="card-art">
        <svg viewBox="0 0 180 36" width="100%" height="100%">
          <rect width="180" height="36" fill="#ded5c5"/>
          <!-- School building with alert envelope -->
          <polygon points="40,28 40,16 55,8 70,16 70,28" fill="#64748b"/>
          <rect x="105" y="10" width="35" height="20" fill="#fff" stroke="#334155" stroke-width="1.2"/>
          <path d="M105 10 L122 22 L140 10" fill="none" stroke="#334155" stroke-width="1.2"/>
          <circle cx="122" cy="18" r="5" fill="#ef4444"/>
          <text x="120" y="21" font-size="7" font-weight="bold" fill="#fff">!</text>
        </svg>
      </div>
      <div class="card-headline">450 German Schools Hit by Email Bomb Threat Hoaxes</div>
      <div class="card-body">Coordinated wave of emailed bomb threats targeted 450 German schools and Danish campuses Monday morning. Police found no specific threat, advising against mass evacuations.</div>
      <div class="card-src">Reuters · Euronews · DW</div>
    </div>

    <!-- Card 7: Gaza / Jabalia -->
    <div class="card">
      <div class="card-top">
        <div class="loc-topic"><div class="card-num">7</div>GAZA · JABALIA</div>
        <div class="badge badge-official">OFFICIAL</div>
      </div>
      <div class="card-art">
        <svg viewBox="0 0 180 36" width="100%" height="100%">
          <rect width="180" height="36" fill="#ded5c5"/>
          <!-- Water well & UNRWA badge -->
          <rect x="45" y="16" width="20" height="14" fill="#78716c"/>
          <polygon points="42,16 55,8 68,16" fill="#a8a29e"/>
          <rect x="100" y="8" width="40" height="22" fill="#0284c7" rx="2"/>
          <text x="106" y="22" font-size="8" font-weight="bold" fill="#fff">UNRWA</text>
        </svg>
      </div>
      <div class="card-headline">UNRWA Staff Worker Killed in Jabalia Camp Strike</div>
      <div class="card-body">Israeli airstrike on Monday killed UNRWA worker Adel Al-Helo near a water well in northern Gaza's Jabalia refugee camp, the agency and local officials reported; three others wounded.</div>
      <div class="card-src">Reuters · Democracy Now</div>
    </div>

    <!-- Card 8: Iran Blockade -->
    <div class="card">
      <div class="card-top">
        <div class="loc-topic"><div class="card-num">8</div>TEHRAN · MIDEAST</div>
        <div class="badge badge-official">OFFICIAL</div>
      </div>
      <div class="card-art">
        <svg viewBox="0 0 180 36" width="100%" height="100%">
          <rect width="180" height="36" fill="#ded5c5"/>
          <!-- Naval blockade barrier & oil tanker -->
          <rect x="30" y="16" width="45" height="12" fill="#1e293b"/>
          <rect x="35" y="12" width="10" height="4" fill="#334155"/>
          <line x1="95" y1="4" x2="95" y2="32" stroke="#dc2626" stroke-width="2" stroke-dasharray="3 2"/>
          <circle cx="130" cy="18" r="8" fill="#15803d" opacity="0.3"/>
          <text x="115" y="21" font-size="7" font-weight="bold" fill="#15803d">TEHRAN</text>
        </svg>
      </div>
      <div class="card-headline">Iran Vows to Use "All Tools" Against US Naval Blockade</div>
      <div class="card-body">Foreign ministry spokesman Baghaei announced Monday that Tehran will deploy all means against US naval blockade on oil exports. Trump told Fox News blockade runners would be sunk.</div>
      <div class="card-src">Reuters · Anadolu</div>
    </div>

    <!-- Card 9: Cikande Fire -->
    <div class="card">
      <div class="card-top">
        <div class="loc-topic"><div class="card-num">9</div>INDONESIA · DISASTER</div>
        <div class="badge badge-ongoing">ONGOING</div>
      </div>
      <div class="card-art">
        <svg viewBox="0 0 180 36" width="100%" height="100%">
          <rect width="180" height="36" fill="#ded5c5"/>
          <!-- Factory profile with smoke plume -->
          <polygon points="35,28 35,16 50,22 50,16 65,22 65,28" fill="#475569"/>
          <path d="M70 14 Q80 4 95 8 T120 4" fill="none" stroke="#71717a" stroke-width="3"/>
          <circle cx="50" cy="24" r="5" fill="#ea580c"/>
          <text x="125" y="22" font-size="8" font-weight="bold" fill="#991b1b">24 DEAD</text>
        </svg>
      </div>
      <div class="card-headline">24 Confirmed Dead in Cikande Confectionery Factory Fire</div>
      <div class="card-body">Indonesian officials confirmed Monday that 24 workers died in Saturday's blaze at PT Fonusa Agung Mulia plant in Banten. Search operations continue for ~30 people still missing.</div>
      <div class="card-src">Reuters 23 Nov</div>
    </div>

    <!-- Card 10: India-Nepal -->
    <div class="card">
      <div class="card-top">
        <div class="loc-topic"><div class="card-num">10</div>NEW DELHI · DIPLOMACY</div>
        <div class="badge badge-official">OFFICIAL</div>
      </div>
      <div class="card-art">
        <svg viewBox="0 0 180 36" width="100%" height="100%">
          <rect width="180" height="36" fill="#ded5c5"/>
          <!-- Diplomatic handshake / aid icon -->
          <circle cx="55" cy="18" r="10" fill="#f97316"/>
          <circle cx="80" cy="18" r="10" fill="#0284c7"/>
          <rect x="62" y="14" width="11" height="8" fill="#15803d"/>
          <text x="105" y="22" font-size="9" font-weight="bold" fill="#15803d">$1.62B AID</text>
        </svg>
      </div>
      <div class="card-headline">India Pledges Record $1.62B Aid Package to Flood-Hit Nepal</div>
      <div class="card-body">PM Narendra Modi and Nepali counterpart Balendra Shah agreed on a $1.62 billion economic package in Delhi Monday during Shah's first overseas bilateral visit since taking office.</div>
      <div class="card-src">Reuters, New Delhi</div>
    </div>

    <!-- Card 11: Spain Puigdemont -->
    <div class="card">
      <div class="card-top">
        <div class="loc-topic"><div class="card-num">11</div>MADRID · COURTS</div>
        <div class="badge badge-official">OFFICIAL</div>
      </div>
      <div class="card-art">
        <svg viewBox="0 0 180 36" width="100%" height="100%">
          <rect width="180" height="36" fill="#ded5c5"/>
          <!-- Judicial scales / gavel -->
          <line x1="60" y1="10" x2="60" y2="28" stroke="#1e293b" stroke-width="2"/>
          <line x1="45" y1="14" x2="75" y2="14" stroke="#1e293b" stroke-width="2"/>
          <circle cx="45" cy="20" r="4" fill="#a16207"/>
          <circle cx="75" cy="20" r="4" fill="#a16207"/>
          <text x="95" y="22" font-size="8" font-weight="bold" fill="#1e293b">CASE SHELVED</text>
        </svg>
      </div>
      <div class="card-headline">Spain Supreme Court Shelves Puigdemont Case</div>
      <div class="card-body">Spain's Supreme Court on Monday closed the criminal case against Catalan separatist Carles Puigdemont, removing his last legal obstacle to return from nine years of Belgian exile.</div>
      <div class="card-src">Reuters, Madrid</div>
    </div>

    <!-- Card 12: Bangladesh Hasina -->
    <div class="card">
      <div class="card-top">
        <div class="loc-topic"><div class="card-num">12</div>DHAKA · POLITICS</div>
        <div class="badge badge-official">OFFICIAL</div>
      </div>
      <div class="card-art">
        <svg viewBox="0 0 180 36" width="100%" height="100%">
          <rect width="180" height="36" fill="#ded5c5"/>
          <!-- Law arrest warrant / handcuffs -->
          <circle cx="60" cy="18" r="7" fill="none" stroke="#334155" stroke-width="2"/>
          <circle cx="80" cy="18" r="7" fill="none" stroke="#334155" stroke-width="2"/>
          <line x1="67" y1="18" x2="73" y2="18" stroke="#334155" stroke-width="2"/>
          <text x="100" y="22" font-size="8" font-weight="bold" fill="#b91c1c">WARRANT</text>
        </svg>
      </div>
      <div class="card-headline">Dhaka Reaffirms Immediate Arrest if Hasina Returns</div>
      <div class="card-body">State Minister Shama Obaed Islam told Reuters Monday Bangladesh will arrest and jail ousted PM Sheikh Hasina if she returns from India, pursuing extradition under bilateral treaty.</div>
      <div class="card-src">Reuters, Dhaka</div>
    </div>

    <!-- Card 13: South Korea NIS -->
    <div class="card">
      <div class="card-top">
        <div class="loc-topic"><div class="card-num">13</div>SEOUL · SECURITY</div>
        <div class="badge badge-official">OFFICIAL</div>
      </div>
      <div class="card-art">
        <svg viewBox="0 0 180 36" width="100%" height="100%">
          <rect width="180" height="36" fill="#ded5c5"/>
          <!-- National Intelligence Service shield -->
          <path d="M60 8 L75 14 L75 24 Q75 30 60 34 Q45 30 45 24 L45 14 Z" fill="#1e3a8a"/>
          <polygon points="60,14 63,22 57,22" fill="#facc15"/>
          <text x="90" y="22" font-size="8" font-weight="bold" fill="#1e3a8a">1ST WOMAN CHIEF</text>
        </svg>
      </div>
      <div class="card-headline">Kang Kum-sil Nominated as S. Korea's First Female Spy Chief</div>
      <div class="card-body">President Lee Jae Myung unveiled a surprise security reshuffle Monday, naming former justice minister Kang to lead the NIS, alongside new foreign and unification ministers.</div>
      <div class="card-src">Reuters, Seoul</div>
    </div>

    <!-- Card 14: Cricket Test -->
    <div class="card">
      <div class="card-top">
        <div class="loc-topic"><div class="card-num">14</div>CENTURION · SPORT</div>
        <div class="badge badge-official">OFFICIAL</div>
      </div>
      <div class="card-art">
        <svg viewBox="0 0 180 36" width="100%" height="100%">
          <rect width="180" height="36" fill="#ded5c5"/>
          <!-- Cricket wickets and ball -->
          <line x1="50" y1="12" x2="50" y2="28" stroke="#854d0e" stroke-width="1.8"/>
          <line x1="56" y1="12" x2="56" y2="28" stroke="#854d0e" stroke-width="1.8"/>
          <line x1="62" y1="12" x2="62" y2="28" stroke="#854d0e" stroke-width="1.8"/>
          <line x1="48" y1="12" x2="64" y2="12" stroke="#854d0e" stroke-width="1.5"/>
          <circle cx="80" cy="20" r="5" fill="#dc2626"/>
          <text x="100" y="22" font-size="8" font-weight="bold" fill="#1e293b">BAN 91 ALL OUT</text>
        </svg>
      </div>
      <div class="card-headline">SA Skittles Bangladesh for 91 on Centurion Day 1</div>
      <div class="card-body">2nd Test, Day 1 at Centurion: South Africa bowlers skittle Bangladesh for 91 before reaching 88 for 1 at stumps, seizing commanding control on the opening day.</div>
      <div class="card-src">ESPNcricinfo Match Report</div>
    </div>

    <!-- Card 15: China Secrets -->
    <div class="card">
      <div class="card-top">
        <div class="loc-topic"><div class="card-num">15</div>BEIJING · SECURITY</div>
        <div class="badge badge-official">OFFICIAL</div>
      </div>
      <div class="card-art">
        <svg viewBox="0 0 180 36" width="100%" height="100%">
          <rect width="180" height="36" fill="#ded5c5"/>
          <!-- Classified document stamp -->
          <rect x="45" y="8" width="22" height="24" fill="#fff" stroke="#475569" stroke-width="1.2"/>
          <rect x="40" y="16" width="32" height="8" fill="#b91c1c" transform="rotate(-12 55 20)"/>
          <text x="44" y="22" font-size="5" font-weight="bold" fill="#fff" transform="rotate(-12 55 20)">SECRETS</text>
          <text x="85" y="22" font-size="8" font-weight="bold" fill="#b91c1c">DEATH SENTENCE</text>
        </svg>
      </div>
      <div class="card-headline">Official "Ma" Sentenced to Death for State Secrets Leak</div>
      <div class="card-body">China's state secrets watchdog Baomiguan disclosed Monday an administrative official surnamed Ma was sentenced to death for leaking state secrets to a foreign spy agency while abroad.</div>
      <div class="card-src">Reuters · Baomiguan</div>
    </div>

  </div>

  <!-- 6. ALSO ON MONDAY + MAP ROW -->
  <div class="also-map-row">

    <!-- Also on Monday list (Stories 16 to 30) -->
    <div class="also-panel">
      <div class="panel-header">
        <div>ALSO ON MONDAY 23 NOVEMBER <span class="year">2026</span> · VERIFIED WORLD BRIEFS</div>
        <div>15 ADDITIONAL DATED DISPATCHES</div>
      </div>
      <div class="also-grid">

        <div class="also-item">
          <div class="also-num">16</div>
          <div class="also-text"><strong>Trump Fox Interview:</strong> Inclined to resume Iran military strikes post-New Year if talks fail; warns blockade runners sink. <span class="also-tag">[REPORTED]</span></div>
        </div>

        <div class="also-item">
          <div class="also-num">17</div>
          <div class="also-text"><strong>Baltic Sea / Kremlin:</strong> Moscow accuses Ukraine of "terrorist activity" after Saturday drone strike on cargo ship Sparta II. <span class="also-tag">[OFFICIAL]</span></div>
        </div>

        <div class="also-item">
          <div class="also-num">18</div>
          <div class="also-text"><strong>Zakarpattia:</strong> Hungarian PM Peter Magyar announces visit to western Ukraine to support ethnic Hungarian minority. <span class="also-tag">[OFFICIAL]</span></div>
        </div>

        <div class="also-item">
          <div class="also-num">19</div>
          <div class="also-text"><strong>Belgium:</strong> PM Bart De Wever sets Dec 31 budget deadline, warning deadlock brings government coalition to an end. <span class="also-tag">[OFFICIAL]</span></div>
        </div>

        <div class="also-item">
          <div class="also-num">20</div>
          <div class="also-text"><strong>Indonesia:</strong> President Prabowo nominates two cabinet ministers as VP candidates following Gibran's official resignation. <span class="also-tag">[OFFICIAL]</span></div>
        </div>

        <div class="also-item">
          <div class="also-num">21</div>
          <div class="also-text"><strong>Thailand:</strong> Appeals Court halves 6-year lèse-majesté prison sentence for opposition lawmaker over social media post. <span class="also-tag">[OFFICIAL]</span></div>
        </div>

        <div class="also-item">
          <div class="also-num">22</div>
          <div class="also-text"><strong>China Demographics:</strong> NDRC issues 2030 blueprint upgrading elderly & childcare infrastructure to combat aging trends. <span class="also-tag">[OFFICIAL]</span></div>
        </div>

        <div class="also-item">
          <div class="also-num">23</div>
          <div class="also-text"><strong>China–Switzerland:</strong> FM Wang Yi urges Swiss counterpart to oppose Taiwan independence and aid China-EU trade. <span class="also-tag">[OFFICIAL]</span></div>
        </div>

        <div class="also-item">
          <div class="also-num">24</div>
          <div class="also-text"><strong>Samsung Cyber:</strong> Confirms 8,000+ customer accounts breached via customer-response portal detected Saturday. <span class="also-tag">[OFFICIAL]</span></div>
        </div>

        <div class="also-item">
          <div class="also-num">25</div>
          <div class="also-text"><strong>Colombia:</strong> MinTIC files formal regulatory charges against Starlink Colombia for failing to block prison signals. <span class="also-tag">[OFFICIAL]</span></div>
        </div>

        <div class="also-item">
          <div class="also-num">26</div>
          <div class="also-text"><strong>Delta Air Lines:</strong> Resolves weight-and-balance software glitch that triggered nationwide holiday flight delays. <span class="also-tag">[OFFICIAL]</span></div>
        </div>

        <div class="also-item">
          <div class="also-num">27</div>
          <div class="also-text"><strong>Zambia:</strong> Opposition leader Brian Mundubile & 12 associates committed to High Court for treason trial. <span class="also-tag">[OFFICIAL]</span></div>
        </div>

        <div class="also-item">
          <div class="also-num">28</div>
          <div class="also-text"><strong>Benghazi Denial:</strong> Egypt formally denies reports it withdrew military experts amid eastern Libyan rift. <span class="also-tag">[OFFICIAL]</span></div>
        </div>

        <div class="also-item">
          <div class="also-num">29</div>
          <div class="also-text"><strong>Armenia:</strong> Yerevan unveils draft constitution toward Azerbaijan peace treaty; move welcomed by Baku. <span class="also-tag">[OFFICIAL]</span></div>
        </div>

        <div class="also-item">
          <div class="also-num">30</div>
          <div class="also-text"><strong>Space Intel:</strong> German media report NATO intelligence warned Russia plans 'Sputnik-S' orbital nuclear weapon. <span class="also-tag">[CLAIM]</span></div>
        </div>

      </div>
    </div>

    <!-- Where it Happened World Map -->
    <div class="map-panel">
      <div class="panel-header">
        <div>WHERE IT HAPPENED · GEOGRAPHIC LOCATOR</div>
        <div>PINS 1–30</div>
      </div>
      <div class="map-container">
        <svg viewBox="0 0 326 142" width="100%" height="100%">
          <!-- Ocean background & gridlines -->
          <rect width="326" height="142" fill="#ede5d5"/>
          <line x1="0" y1="71" x2="326" y2="71" stroke="#d5cabb" stroke-width="0.8" stroke-dasharray="3 3"/>
          <line x1="163" y1="0" x2="163" y2="142" stroke="#d5cabb" stroke-width="0.8" stroke-dasharray="3 3"/>

          <!-- Simplified Continent Outlines (Equirectangular) -->
          <!-- North America -->
          <path d="M25 20 L75 16 L88 32 L78 50 L65 52 L55 68 L48 66 L42 50 L20 38 Z" fill="#d9cfbe" stroke="#b8ab96" stroke-width="0.8"/>
          <!-- South America -->
          <path d="M58 75 L82 78 L95 98 L85 130 L72 135 L62 95 Z" fill="#d9cfbe" stroke="#b8ab96" stroke-width="0.8"/>
          <!-- Europe -->
          <path d="M142 22 L172 20 L180 34 L162 46 L145 42 L138 32 Z" fill="#d9cfbe" stroke="#b8ab96" stroke-width="0.8"/>
          <!-- Africa -->
          <path d="M140 50 L175 48 L188 75 L175 116 L155 118 L142 85 L132 62 Z" fill="#d9cfbe" stroke="#b8ab96" stroke-width="0.8"/>
          <!-- Asia -->
          <path d="M182 20 L275 20 L285 45 L260 70 L228 72 L215 58 L182 46 Z" fill="#d9cfbe" stroke="#b8ab96" stroke-width="0.8"/>
          <!-- Australia -->
          <path d="M250 96 L285 95 L290 120 L255 125 Z" fill="#d9cfbe" stroke="#b8ab96" stroke-width="0.8"/>

          <!-- Numbered Pin Dots -->
          <!-- 1: Benghazi -->
          <circle cx="158" cy="48" r="4.2" fill="#b91c1c"/>
          <text x="158" y="50" font-size="5" font-weight="bold" fill="#fff" text-anchor="middle">1</text>

          <!-- 2: Dymer/Kyiv -->
          <circle cx="166" cy="32" r="4.2" fill="#b91c1c"/>
          <text x="166" y="34" font-size="5" font-weight="bold" fill="#fff" text-anchor="middle">2</text>

          <!-- 3: Sydney / Pacific -->
          <circle cx="282" cy="115" r="4.2" fill="#b91c1c"/>
          <text x="282" y="117" font-size="5" font-weight="bold" fill="#fff" text-anchor="middle">3</text>

          <!-- 4: Santa Clara (US) -->
          <circle cx="38" cy="42" r="4.2" fill="#b91c1c"/>
          <text x="38" y="44" font-size="5" font-weight="bold" fill="#fff" text-anchor="middle">4</text>

          <!-- 5: Warsaw -->
          <circle cx="158" cy="28" r="4.2" fill="#b91c1c"/>
          <text x="158" y="30" font-size="5" font-weight="bold" fill="#fff" text-anchor="middle">5</text>

          <!-- 6: Germany / Denmark -->
          <circle cx="150" cy="26" r="4.2" fill="#b91c1c"/>
          <text x="150" y="28" font-size="5" font-weight="bold" fill="#fff" text-anchor="middle">6</text>

          <!-- 7: Gaza -->
          <circle cx="170" cy="50" r="4.2" fill="#b91c1c"/>
          <text x="170" y="52" font-size="5" font-weight="bold" fill="#fff" text-anchor="middle">7</text>

          <!-- 8: Tehran -->
          <circle cx="182" cy="46" r="4.2" fill="#b91c1c"/>
          <text x="182" y="48" font-size="5" font-weight="bold" fill="#fff" text-anchor="middle">8</text>

          <!-- 9: Cikande/Jakarta -->
          <circle cx="240" cy="85" r="4.2" fill="#b91c1c"/>
          <text x="240" y="87" font-size="5" font-weight="bold" fill="#fff" text-anchor="middle">9</text>

          <!-- 10: New Delhi -->
          <circle cx="212" cy="52" r="4.2" fill="#b91c1c"/>
          <text x="212" y="54" font-size="5" font-weight="bold" fill="#fff" text-anchor="middle">10</text>

          <!-- 11: Madrid -->
          <circle cx="136" cy="40" r="4.2" fill="#b91c1c"/>
          <text x="136" y="42" font-size="5" font-weight="bold" fill="#fff" text-anchor="middle">11</text>

          <!-- 12: Dhaka -->
          <circle cx="224" cy="54" r="4.2" fill="#b91c1c"/>
          <text x="224" y="56" font-size="5" font-weight="bold" fill="#fff" text-anchor="middle">12</text>

          <!-- 13: Seoul -->
          <circle cx="258" cy="40" r="4.2" fill="#b91c1c"/>
          <text x="258" y="42" font-size="5" font-weight="bold" fill="#fff" text-anchor="middle">13</text>

          <!-- 14: Centurion -->
          <circle cx="166" cy="108" r="4.2" fill="#b91c1c"/>
          <text x="166" y="110" font-size="5" font-weight="bold" fill="#fff" text-anchor="middle">14</text>

          <!-- 15: Beijing -->
          <circle cx="248" cy="36" r="4.2" fill="#b91c1c"/>
          <text x="248" y="38" font-size="5" font-weight="bold" fill="#fff" text-anchor="middle">15</text>

          <!-- Secondary pins (16 to 30) -->
          <!-- 16: Washington DC -->
          <circle cx="56" cy="34" r="4.2" fill="#1e3a8a"/>
          <text x="56" y="36" font-size="5" font-weight="bold" fill="#fff" text-anchor="middle">16</text>

          <!-- 17: Baltic / Kremlin -->
          <circle cx="174" cy="24" r="4.2" fill="#1e3a8a"/>
          <text x="174" y="26" font-size="5" font-weight="bold" fill="#fff" text-anchor="middle">17</text>

          <!-- 18: Zakarpattia -->
          <circle cx="160" cy="37" r="4.2" fill="#1e3a8a"/>
          <text x="160" y="39" font-size="5" font-weight="bold" fill="#fff" text-anchor="middle">18</text>

          <!-- 19: Belgium -->
          <circle cx="144" cy="30" r="4.2" fill="#1e3a8a"/>
          <text x="144" y="32" font-size="5" font-weight="bold" fill="#fff" text-anchor="middle">19</text>

          <!-- 20: Indonesia -->
          <circle cx="249" cy="89" r="4.2" fill="#1e3a8a"/>
          <text x="249" y="91" font-size="5" font-weight="bold" fill="#fff" text-anchor="middle">20</text>

          <!-- 21: Thailand -->
          <circle cx="234" cy="66" r="4.2" fill="#1e3a8a"/>
          <text x="234" y="68" font-size="5" font-weight="bold" fill="#fff" text-anchor="middle">21</text>

          <!-- 22: China demographics -->
          <circle cx="240" cy="42" r="4.2" fill="#1e3a8a"/>
          <text x="240" y="44" font-size="5" font-weight="bold" fill="#fff" text-anchor="middle">22</text>

          <!-- 23: China–Switzerland -->
          <circle cx="146" cy="38" r="4.2" fill="#1e3a8a"/>
          <text x="146" y="40" font-size="5" font-weight="bold" fill="#fff" text-anchor="middle">23</text>

          <!-- 24: Samsung / Suwon -->
          <circle cx="266" cy="44" r="4.2" fill="#1e3a8a"/>
          <text x="266" y="46" font-size="5" font-weight="bold" fill="#fff" text-anchor="middle">24</text>

          <!-- 25: Colombia -->
          <circle cx="70" cy="80" r="4.2" fill="#1e3a8a"/>
          <text x="70" y="82" font-size="5" font-weight="bold" fill="#fff" text-anchor="middle">25</text>

          <!-- 26: Delta / Atlanta -->
          <circle cx="50" cy="46" r="4.2" fill="#1e3a8a"/>
          <text x="50" y="48" font-size="5" font-weight="bold" fill="#fff" text-anchor="middle">26</text>

          <!-- 27: Zambia -->
          <circle cx="164" cy="94" r="4.2" fill="#1e3a8a"/>
          <text x="164" y="96" font-size="5" font-weight="bold" fill="#fff" text-anchor="middle">27</text>

          <!-- 28: Egypt / Cairo -->
          <circle cx="166" cy="54" r="4.2" fill="#1e3a8a"/>
          <text x="166" y="56" font-size="5" font-weight="bold" fill="#fff" text-anchor="middle">28</text>

          <!-- 29: Armenia -->
          <circle cx="178" cy="36" r="4.2" fill="#1e3a8a"/>
          <text x="178" y="38" font-size="5" font-weight="bold" fill="#fff" text-anchor="middle">29</text>

          <!-- 30: Space intel -->
          <circle cx="150" cy="16" r="4.2" fill="#1e3a8a"/>
          <text x="150" y="18" font-size="5" font-weight="bold" fill="#fff" text-anchor="middle">30</text>
        </svg>
      </div>
    </div>

  </div>

  <!-- 7. FOOTER SECTION: DATE CHECK + HOW SURE -->
  <div class="footer-row">

    <!-- Date Check Box -->
    <div class="date-check-box">
      <div class="date-check-title">DATE CHECK · STRICT MONDAY 23 NOVEMBER <span class="year">2026</span> AUDIT (UTC)</div>
      <div><strong>INCLUDED:</strong> Every story on this broadsheet happened or was first reported on Monday 23 November <span class="year">2026</span> (UTC).</div>
      <div style="margin-top:2px;"><strong>LEFT OUT (Occurred on earlier days):</strong> COP31 closing plenary & no-deal gavel (Sunday 22 Nov) · Dymer initial 186-drone attack & 6-dead toll (Sunday; Monday was 11-dead toll & search conclusion) · Pre-dawn Benghazi explosions (Sunday; Ukrainian official confirmation Monday) · US Democrats reaching 258 House seats (Sunday call) · Sunday sports: Verstappen Las Vegas GP, Alcaraz ATP Finals, Márquez 8th MotoGP title, HK committee poll 98.79%, India 720/9, Liverpool 4-0 Man Utd · Saturday Cikande confectionery fire start (Monday 24 confirmed dead toll) & Baltic Sparta II fire · Friday Polish border Kh-101 missiles (Monday AWACS deployment).</div>
    </div>

    <!-- How Sure Box -->
    <div class="how-sure-box">
      <div>
        <div class="how-sure-title">HOW SURE · CERTAINTY CALIBRATION</div>
        <div><strong>CONFIRMED:</strong> 2+ independent global news wire outlets.</div>
        <div><strong>OFFICIAL:</strong> Government, court, military, or agency on record.</div>
        <div><strong>REPORTED:</strong> Single reputable global wire or broadcaster.</div>
        <div><strong>CLAIM:</strong> One side's allegation; explicitly attributed.</div>
        <div><strong>ONGOING:</strong> Search, rescue, or disaster operations in progress.</div>
        <div style="font-style:italic;margin-top:1px;">Illustrations are drawn editorial vector artwork, not photographs.</div>
      </div>
      <div class="colophon">
        Deterministic compilation for make.fun news-image-20261123 · Mon 23 Nov <span class="year">2026</span>
      </div>
    </div>

  </div>

</div>
</body>
</html>
"""

def generate_image():
    print("[*] Writing HTML template to /tmp/news_entry_render.html...")
    with open(TMP_HTML, "w", encoding="utf-8") as f:
        f.write(HTML_CONTENT)

    if os.path.exists(TMP_PNG):
        os.remove(TMP_PNG)

    print("[*] Executing headless Chrome render using deterministic recipe...")
    chrome_cmd = (
        f"timeout 60s /opt/google/chrome/chrome --headless=new --disable-gpu --no-sandbox "
        f"--disable-background-networking --disable-default-apps --disable-extensions --disable-sync "
        f"--metrics-recording-only --no-first-run --disable-component-update "
        f'--host-rules="MAP * ~NOTFOUND" '
        f"--window-size=1024,1024 --screenshot={TMP_PNG} "
        f"file://{TMP_HTML}"
    )

    rc = os.system(chrome_cmd)
    if not os.path.exists(TMP_PNG) or rc != 0:
        print(f"[*] First attempt returned {rc}, retrying once...")
        rc = os.system(chrome_cmd)

    if not os.path.exists(TMP_PNG):
        print(f"[!] Chrome command failed with return code {rc}")
        sys.exit(1)

    print("[*] Processing image with Pillow for exact 1024x1024 PNG...")
    img = Image.open(TMP_PNG)
    if img.size != (1024, 1024):
        print(f"[!] Resizing from {img.size} to (1024, 1024)...")
        img = img.resize((1024, 1024), Image.Resampling.LANCZOS)
    img = img.convert("RGB")

    os.makedirs(PROJECT_DIR, exist_ok=True)
    img.save(OUTPUT_PNG, format="PNG", optimize=True)

    # Clean up scratch files outside repo
    if os.path.exists(TMP_HTML):
        os.remove(TMP_HTML)
    if os.path.exists(TMP_PNG):
        os.remove(TMP_PNG)

    file_size = os.path.getsize(OUTPUT_PNG)
    with open(OUTPUT_PNG, "rb") as f:
        sha256 = hashlib.sha256(f.read()).hexdigest()

    print(f"[✓] Successfully generated {OUTPUT_PNG}")
    print(f"    Dimensions: {img.size[0]}x{img.size[1]} px")
    print(f"    File size:  {file_size:,} bytes ({file_size / 1024:.1f} KiB)")
    print(f"    SHA-256:    {sha256}")

    if file_size > 1048576:
        raise ValueError(f"Image exceeds 1 MiB limit! Size: {file_size} bytes")

if __name__ == "__main__":
    generate_image()
