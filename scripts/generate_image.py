#!/usr/bin/env python3
"""
scripts/generate_image.py
Editorial broadsheet generator for Monday 23 November 2026.
Bakes a deterministic 1024x1024 RGB PNG to entry.png.
"""

import os
import sys
sys.dont_write_bytecode = True
import math
import hashlib
import tempfile
import subprocess
from PIL import Image

# -----------------------------------------------------------------------------
# News Data Definitions (Monday 23 November 2026 UTC)
# -----------------------------------------------------------------------------

REGION_PILLS = [
    ("EUROPE", 7),
    ("MIDDLE EAST", 3),
    ("AFRICA", 3),
    ("SOUTH ASIA", 3),
    ("EAST ASIA", 4),
    ("SOUTHEAST ASIA", 3),
    ("AMERICAS", 3),
    ("OCEANIA / CLIMATE", 2),
    ("CAUCASUS / SPACE", 2),
]

TIMELINE_EVENTS = [
    ("00:12", "COP31 fallout files"),
    ("Morn", "450 German school hoaxes"),
    ("Midday", "NATO AWACS to Poland"),
    ("13:59", "Nvidia rehires Huang"),
    ("15:30", "Centurion Day 1 (BAN 91)"),
    ("Eve", "Spain SC shelves Puigdemont"),
]

DAY_IN_NUMBERS = [
    ("7", "Naval drones sank corvette Merkury"),
    ("11", "Dymer dead as rescue concludes"),
    ("24", "Dead at Cikande factory fire toll"),
    ("450", "German schools emailed threats"),
    ("+31.5%", "Nvidia stock surge (+$1T value)"),
    ("$1.62B", "India-Nepal aid package agreed"),
    ("91", "Bangladesh all out at Centurion"),
]

LEAD_STORIES = [
    {
        "num": 1,
        "loc": "BENGHAZI · WAR",
        "certainty": "CONFIRMED",
        "headline": "Ukraine Confirms Sinking of Russian Corvette Merkury",
        "body": "Zelenskyy & SBU confirm Monday: 7 naval drones launched from mothership sank corvette Merkury in Sunday strike at Benghazi base; MV Angara also hit. UNSMIL urges probe.",
        "source": "Reuters · AP · The Guardian",
        "icon": "warship",
    },
    {
        "num": 2,
        "loc": "DYMER · WAR",
        "certainty": "OFFICIAL",
        "headline": "Dymer Rescue Concludes as Strike Toll Rises to 11",
        "body": "Search-and-rescue ends Monday after Sunday's Russian drone strike on a 5-storey apartment building. Toll rose from 6 to 11, including a child; 2 survivors pulled from rubble.",
        "source": "Ukrinform · Interfax-Ukraine",
        "icon": "building",
    },
    {
        "num": 3,
        "loc": "ANTALYA / SYDNEY",
        "certainty": "CONFIRMED",
        "headline": "Bowen Faces Resignation Calls After COP31 Collapse",
        "body": "Monday political storm in Australia after COP31 closed Sunday with no deal. Angus Taylor demands Bowen quit; Albanese defends him. Marshall Islands: 'let down on all sides.'",
        "source": "Reuters · SMH · Guardian",
        "icon": "cop31",
    },
    {
        "num": 4,
        "loc": "SANTA CLARA · TECH",
        "certainty": "CONFIRMED",
        "headline": "Huang Reinstated as Nvidia CEO; Shares Surge 31.5%",
        "body": "Nvidia rehires Jensen Huang Monday following Donald Trump intervention. Shares jump 31.5%, adding ~$1T in market value. Board rules no national security risk; lawmakers raise questions.",
        "source": "Reuters 13:59 UTC · CNBC",
        "icon": "nvidia",
    },
    {
        "num": 5,
        "loc": "WARSAW · SECURITY",
        "certainty": "CONFIRMED",
        "headline": "NATO Deploys AWACS Radar Plane to Poland",
        "body": "Monday decision: NATO deploys AWACS early-warning jet to Poland after three Russian Kh-101 missiles landed on Polish soil Friday. SACEUR Gen. Grynkewich authorised mission.",
        "source": "Reuters, Warsaw",
        "icon": "awacs",
    },
    {
        "num": 6,
        "loc": "GERMANY / DENMARK",
        "certainty": "REPORTED",
        "headline": "450 German Schools Hit by Email Bomb Threat Hoaxes",
        "body": "Coordinated wave of emailed bomb threats targeted 450 German schools and Danish campuses Monday morning. Police found no specific threat, advising against mass evacuations.",
        "source": "Reuters · Euronews · DW",
        "icon": "school",
    },
    {
        "num": 7,
        "loc": "GAZA · JABALIA",
        "certainty": "OFFICIAL",
        "headline": "UNRWA Staff Worker Killed in Jabalia Camp Strike",
        "body": "Israeli airstrike on Monday killed UNRWA worker Adel Al-Helo near a water well in northern Gaza's Jabalia refugee camp, the agency and local officials reported; three others wounded.",
        "source": "Reuters · Democracy Now",
        "icon": "unrwa",
    },
    {
        "num": 8,
        "loc": "TEHRAN · MIDEAST",
        "certainty": "OFFICIAL",
        "headline": "Iran Vows to Use 'All Tools' Against US Naval Blockade",
        "body": "Foreign ministry spokesman Baghaei announced Monday that Tehran will deploy all means against US naval blockade on oil exports. Trump told Fox News blockade runners would be sunk.",
        "source": "Reuters · Anadolu",
        "icon": "iran",
    },
    {
        "num": 9,
        "loc": "INDONESIA · DISASTER",
        "certainty": "ONGOING",
        "headline": "24 Confirmed Dead in Cikande Confectionery Factory Fire",
        "body": "Indonesian officials confirmed Monday that 24 workers died in Saturday's blaze at PT Fonusa Agung Mulia plant in Banten. Search operations continue for ~30 people still missing.",
        "source": "Reuters 23 Nov",
        "icon": "factory",
    },
    {
        "num": 10,
        "loc": "NEW DELHI · DIPLOMACY",
        "certainty": "OFFICIAL",
        "headline": "India Pledges Record $1.62B Aid Package to Flood-Hit Nepal",
        "body": "PM Narendra Modi and Nepali counterpart Balendra Shah agreed on a $1.62 billion economic package in Delhi Monday during Shah's first overseas bilateral visit since taking office.",
        "source": "Reuters, New Delhi",
        "icon": "diplomacy",
    },
    {
        "num": 11,
        "loc": "MADRID · COURTS",
        "certainty": "OFFICIAL",
        "headline": "Spain Supreme Court Shelves Puigdemont Case",
        "body": "Spain's Supreme Court on Monday closed the criminal case against Catalan separatist Carles Puigdemont, removing his last legal obstacle to return from nine years of Belgian exile.",
        "source": "Reuters, Madrid",
        "icon": "scales",
    },
    {
        "num": 12,
        "loc": "DHAKA · POLITICS",
        "certainty": "OFFICIAL",
        "headline": "Dhaka Reaffirms Immediate Arrest if Hasina Returns",
        "body": "State Minister Shama Obaed Islam told Reuters Monday Bangladesh will arrest and jail ousted PM Sheikh Hasina if she returns from India, pursuing extradition under bilateral treaty.",
        "source": "Reuters, Dhaka",
        "icon": "warrant",
    },
    {
        "num": 13,
        "loc": "SEOUL · SECURITY",
        "certainty": "OFFICIAL",
        "headline": "Kang Kum-sil Nominated as S. Korea's First Female Spy Chief",
        "body": "President Lee Jae Myung unveiled a surprise security reshuffle Monday, naming former justice minister Kang to lead the NIS, alongside new foreign and unification ministers.",
        "source": "Reuters, Seoul",
        "icon": "nis",
    },
    {
        "num": 14,
        "loc": "CENTURION · SPORT",
        "certainty": "OFFICIAL",
        "headline": "SA Skittles Bangladesh for 91 on Centurion Day 1",
        "body": "2nd Test, Day 1 at Centurion: South Africa bowlers skittle Bangladesh for 91 before reaching 88 for 1 at stumps, seizing commanding control on the opening day.",
        "source": "ESPNcricinfo Match Report",
        "icon": "cricket",
    },
    {
        "num": 15,
        "loc": "BEIJING · SECURITY",
        "certainty": "OFFICIAL",
        "headline": "Official 'Ma' Sentenced to Death for State Secrets Leak",
        "body": "China's state secrets watchdog Baomiguan disclosed Monday an administrative official surnamed Ma was sentenced to death for leaking state secrets to a foreign spy agency while abroad.",
        "source": "Reuters · Baomiguan",
        "icon": "secrets",
    },
]

BRIEF_STORIES = [
    {
        "num": 16,
        "label": "Trump Fox Interview",
        "text": "Inclined to resume Iran military strikes post-New Year if talks fail; warns blockade runners will be attacked and sunk.",
        "certainty": "REPORTED",
    },
    {
        "num": 17,
        "label": "Baltic Sea / Kremlin",
        "text": "Moscow accuses Ukraine of 'terrorist activity' after Saturday drone strike on Russian cargo ship Sparta II.",
        "certainty": "OFFICIAL",
    },
    {
        "num": 18,
        "label": "Zakarpattia",
        "text": "Hungarian PM Peter Magyar announces visit to western Ukraine to express support for ethnic Hungarian minority.",
        "certainty": "OFFICIAL",
    },
    {
        "num": 19,
        "label": "Belgium",
        "text": "PM Bart De Wever sets Dec 31 budget deadline, warning deadlock brings government coalition to an end.",
        "certainty": "OFFICIAL",
    },
    {
        "num": 20,
        "label": "Indonesia",
        "text": "President Prabowo nominates two cabinet ministers as VP candidates following Gibran's official resignation.",
        "certainty": "OFFICIAL",
    },
    {
        "num": 21,
        "label": "Thailand",
        "text": "Appeals Court halves 6-year lèse-majesté prison sentence for opposition lawmaker over social media post.",
        "certainty": "OFFICIAL",
    },
    {
        "num": 22,
        "label": "China Demographics",
        "text": "NDRC issues 2030 blueprint upgrading elderly & childcare infrastructure to combat aging trends.",
        "certainty": "OFFICIAL",
    },
    {
        "num": 23,
        "label": "China–Switzerland",
        "text": "FM Wang Yi urges Swiss counterpart to oppose Taiwan independence and aid China-EU trade.",
        "certainty": "OFFICIAL",
    },
    {
        "num": 24,
        "label": "Samsung Cyber",
        "text": "Confirms 8,000+ customer accounts breached via customer-response portal detected Saturday.",
        "certainty": "OFFICIAL",
    },
    {
        "num": 25,
        "label": "Colombia",
        "text": "MinTIC files formal regulatory charges against Starlink Colombia for failing to block prison signals.",
        "certainty": "OFFICIAL",
    },
    {
        "num": 26,
        "label": "Delta Air Lines",
        "text": "Resolves weight-and-balance software glitch that triggered nationwide holiday flight delays.",
        "certainty": "OFFICIAL",
    },
    {
        "num": 27,
        "label": "Zambia",
        "text": "Opposition leader Brian Mundubile & 12 associates committed to High Court for treason trial.",
        "certainty": "OFFICIAL",
    },
    {
        "num": 28,
        "label": "Benghazi Denial",
        "text": "Egypt formally denies reports it withdrew military experts amid eastern Libyan rift.",
        "certainty": "OFFICIAL",
    },
    {
        "num": 29,
        "label": "Armenia",
        "text": "Yerevan unveils draft constitution toward Azerbaijan peace treaty; move welcomed by Baku.",
        "certainty": "OFFICIAL",
    },
    {
        "num": 30,
        "label": "Space Intel",
        "text": "German media report NATO intelligence warned Russia plans 'Sputnik-S' orbital nuclear weapon.",
        "certainty": "CLAIM",
    },
]

# Map pins geographic coordinates (lat, lon)
MAP_LOCATIONS = [
    (1, 32.1, 20.0),      # Benghazi
    (2, 50.8, 30.3),      # Dymer
    (3, -33.9, 151.2),    # Sydney / COP31
    (4, 37.3, -122.0),    # Santa Clara
    (5, 52.2, 21.0),      # Warsaw
    (6, 52.5, 10.0),      # Germany
    (7, 31.5, 34.5),      # Gaza
    (8, 35.7, 51.4),      # Tehran
    (9, -6.2, 106.3),     # Cikande
    (10, 28.6, 77.2),     # New Delhi
    (11, 40.4, -3.7),     # Madrid
    (12, 23.8, 90.4),     # Dhaka
    (13, 37.5, 127.0),    # Seoul NIS
    (14, -25.8, 28.2),    # Centurion
    (15, 39.9, 116.4),    # Beijing
    (16, 38.9, -77.0),    # Washington DC
    (17, 59.5, 24.5),     # Baltic Sea
    (18, 48.5, 23.0),     # Zakarpattia
    (19, 50.8, 4.3),      # Brussels
    (20, -6.2, 106.8),    # Jakarta
    (21, 13.7, 100.5),    # Bangkok
    (22, 34.0, 108.0),    # China NDRC
    (23, 46.9, 7.4),      # Bern
    (24, 36.5, 128.0),    # Samsung Cyber
    (25, 4.7, -74.0),     # Colombia
    (26, 33.7, -84.4),    # Delta US
    (27, -15.4, 28.3),    # Zambia
    (28, 30.0, 31.2),     # Egypt
    (29, 40.1, 44.5),     # Armenia
    (30, 55.7, 37.6),     # Moscow Space
]

# -----------------------------------------------------------------------------
# SVG Icons Generation for Lead Cards
# -----------------------------------------------------------------------------

def get_card_icon_svg(icon_type: str) -> str:
    """Generate clean editorial vector illustrations for cards (viewBox 0 0 186 34)."""
    if icon_type == "warship":
        return """
        <svg viewBox="0 0 186 34" width="100%" height="34" xmlns="http://www.w3.org/2000/svg">
            <rect width="186" height="34" fill="#e8edf2" rx="2"/>
            <path d="M0 24 Q 45 22 90 24 T 186 24 L 186 34 L 0 34 Z" fill="#b9c9d6"/>
            <!-- Warship silhouette -->
            <path d="M45 22 L55 14 L85 14 L95 10 L105 10 L110 14 L135 15 L145 22 Z" fill="#2d3748"/>
            <rect x="75" y="6" width="4" height="8" fill="#1a202c"/>
            <line x1="77" y1="2" x2="77" y2="6" stroke="#1a202c" stroke-width="1.5"/>
            <!-- Drone boat -->
            <path d="M12 23 L22 23 L26 21 L16 21 Z" fill="#c53030"/>
            <path d="M5 24 Q 10 22 16 23" stroke="#ffffff" stroke-width="1" fill="none"/>
            <!-- Sinking smoke / fire -->
            <circle cx="102" cy="11" r="5" fill="#e53e3e" opacity="0.8"/>
            <circle cx="108" cy="8" r="4" fill="#dd6b20" opacity="0.85"/>
            <circle cx="114" cy="5" r="3.5" fill="#718096" opacity="0.6"/>
            <rect x="142" y="4" width="38" height="11" rx="2" fill="#991b1b"/>
            <text x="161" y="12" fill="#ffffff" font-size="6.5" font-weight="700" text-anchor="middle" font-family="'IBM Plex Sans', sans-serif">MERKURY</text>
        </svg>
        """
    elif icon_type == "building":
        return """
        <svg viewBox="0 0 186 34" width="100%" height="34" xmlns="http://www.w3.org/2000/svg">
            <rect width="186" height="34" fill="#f0ece6" rx="2"/>
            <!-- Building intact section -->
            <rect x="35" y="6" width="35" height="26" fill="#4a5568"/>
            <rect x="40" y="9" width="5" height="4" fill="#ecc94b"/>
            <rect x="50" y="9" width="5" height="4" fill="#cbd5e0"/>
            <rect x="60" y="9" width="5" height="4" fill="#ecc94b"/>
            <rect x="40" y="16" width="5" height="4" fill="#cbd5e0"/>
            <rect x="50" y="16" width="5" height="4" fill="#ecc94b"/>
            <rect x="60" y="16" width="5" height="4" fill="#cbd5e0"/>
            <rect x="40" y="23" width="5" height="4" fill="#cbd5e0"/>
            <rect x="50" y="23" width="5" height="4" fill="#cbd5e0"/>
            <rect x="60" y="23" width="5" height="4" fill="#ecc94b"/>
            <!-- Collapsed section & rubble -->
            <path d="M70 12 L85 22 L98 25 L108 32 L70 32 Z" fill="#2d3748"/>
            <polygon points="78,28 85,24 92,30 84,32" fill="#718096"/>
            <!-- Searchlight beam -->
            <polygon points="145,32 105,8 80,18" fill="#faf089" opacity="0.45"/>
            <rect x="132" y="4" width="48" height="11" rx="2" fill="#1d4ed8"/>
            <text x="156" y="12" fill="#ffffff" font-size="6.5" font-weight="700" text-anchor="middle" font-family="'IBM Plex Sans', sans-serif">TOLL: 11 DEAD</text>
        </svg>
        """
    elif icon_type == "cop31":
        return """
        <svg viewBox="0 0 186 34" width="100%" height="34" xmlns="http://www.w3.org/2000/svg">
            <rect width="186" height="34" fill="#f5ede8" rx="2"/>
            <!-- Globe wireframe -->
            <circle cx="50" cy="17" r="13" fill="#e2e8f0" stroke="#718096" stroke-width="0.8"/>
            <ellipse cx="50" cy="17" rx="13" ry="5.5" fill="none" stroke="#718096" stroke-width="0.8"/>
            <line x1="50" y1="4" x2="50" y2="30" stroke="#718096" stroke-width="0.8"/>
            <!-- Gavel -->
            <rect x="75" y="22" width="26" height="5" rx="1" fill="#744210"/>
            <rect x="78" y="8" width="16" height="8" rx="1.5" fill="#975a16" transform="rotate(-20 86 12)"/>
            <rect x="84" y="12" width="4" height="14" fill="#744210" transform="rotate(-20 86 19)"/>
            <!-- NO DEAL Stamp -->
            <rect x="122" y="6" width="56" height="15" rx="2" fill="#991b1b" stroke="#7f1d1d" stroke-width="1"/>
            <text x="150" y="17" fill="#ffffff" font-size="8" font-weight="800" text-anchor="middle" font-family="'IBM Plex Sans', sans-serif" letter-spacing="0.5">NO DEAL</text>
        </svg>
        """
    elif icon_type == "nvidia":
        return """
        <svg viewBox="0 0 186 34" width="100%" height="34" xmlns="http://www.w3.org/2000/svg">
            <rect width="186" height="34" fill="#eaf5ea" rx="2"/>
            <!-- Nvidia chip icon -->
            <rect x="18" y="7" width="20" height="20" rx="3" fill="#76b900"/>
            <path d="M23 17 C 23 13 28 13 31 15 C 33 16 34 18 34 20" fill="none" stroke="#ffffff" stroke-width="2" stroke-linecap="round"/>
            <circle cx="28" cy="17" r="1.5" fill="#ffffff"/>
            <!-- Surging stock chart -->
            <polyline points="50,26 70,22 88,24 105,14 122,8" fill="none" stroke="#15803d" stroke-width="2.5" stroke-linecap="round"/>
            <polygon points="120,5 128,8 122,12" fill="#15803d"/>
            <rect x="134" y="6" width="46" height="15" rx="2" fill="#15803d"/>
            <text x="157" y="17" fill="#ffffff" font-size="8" font-weight="700" text-anchor="middle" font-family="'IBM Plex Sans', sans-serif">+31.5%</text>
        </svg>
        """
    elif icon_type == "awacs":
        return """
        <svg viewBox="0 0 186 34" width="100%" height="34" xmlns="http://www.w3.org/2000/svg">
            <rect width="186" height="34" fill="#ebf3f9" rx="2"/>
            <!-- AWACS Aircraft silhouette -->
            <path d="M25 20 L50 18 L70 18 L100 16 L120 18 L130 20 L100 22 L50 22 Z" fill="#334155"/>
            <polygon points="65,18 78,8 88,18" fill="#475569"/>
            <polygon points="35,18 42,12 48,18" fill="#475569"/>
            <!-- Rotodome dish -->
            <ellipse cx="80" cy="11" rx="14" ry="3.5" fill="#0f172a"/>
            <!-- Radar arcs -->
            <path d="M100 7 A 10 10 0 0 1 112 16" fill="none" stroke="#0284c7" stroke-width="1.5"/>
            <path d="M106 4 A 18 18 0 0 1 124 18" fill="none" stroke="#0284c7" stroke-width="1.5" stroke-dasharray="2,2"/>
            <rect x="135" y="6" width="44" height="14" rx="2" fill="#0369a1"/>
            <text x="157" y="16.5" fill="#ffffff" font-size="7" font-weight="700" text-anchor="middle" font-family="'IBM Plex Sans', sans-serif">AWACS</text>
        </svg>
        """
    elif icon_type == "school":
        return """
        <svg viewBox="0 0 186 34" width="100%" height="34" xmlns="http://www.w3.org/2000/svg">
            <rect width="186" height="34" fill="#fdf2e9" rx="2"/>
            <!-- Schoolhouse -->
            <polygon points="35,10 18,22 52,22" fill="#c2410c"/>
            <rect x="22" y="22" width="26" height="9" fill="#fed7aa"/>
            <rect x="32" y="25" width="6" height="6" fill="#7c2d12"/>
            <!-- Envelope alert -->
            <rect x="68" y="10" width="28" height="18" rx="2" fill="#ffffff" stroke="#ea580c" stroke-width="1.2"/>
            <polyline points="68,10 82,20 96,10" fill="none" stroke="#ea580c" stroke-width="1.2"/>
            <circle cx="82" cy="19" r="4" fill="#dc2626"/>
            <text x="82" y="21.5" fill="#ffffff" font-size="6" font-weight="900" text-anchor="middle">!</text>
            <rect x="120" y="6" width="58" height="15" rx="2" fill="#b45309"/>
            <text x="149" y="17" fill="#ffffff" font-size="7" font-weight="700" text-anchor="middle" font-family="'IBM Plex Sans', sans-serif">450 HOAXES</text>
        </svg>
        """
    elif icon_type == "unrwa":
        return """
        <svg viewBox="0 0 186 34" width="100%" height="34" xmlns="http://www.w3.org/2000/svg">
            <rect width="186" height="34" fill="#eff6ff" rx="2"/>
            <!-- Water well -->
            <rect x="28" y="16" width="24" height="14" fill="#94a3b8" rx="1"/>
            <line x1="28" y1="16" x2="40" y2="8" stroke="#475569" stroke-width="1.5"/>
            <line x1="52" y1="16" x2="40" y2="8" stroke="#475569" stroke-width="1.5"/>
            <circle cx="40" cy="12" r="2" fill="#1e293b"/>
            <!-- UNRWA Badge -->
            <rect x="68" y="8" width="46" height="18" rx="2" fill="#0284c7"/>
            <text x="91" y="20" fill="#ffffff" font-size="8.5" font-weight="800" text-anchor="middle" font-family="'IBM Plex Sans', sans-serif" letter-spacing="0.5">UNRWA</text>
            <line x1="126" y1="5" x2="126" y2="29" stroke="#cbd5e1" stroke-width="1"/>
            <text x="156" y="20" fill="#dc2626" font-size="7" font-weight="700" text-anchor="middle" font-family="'IBM Plex Sans', sans-serif">AID WORKER</text>
        </svg>
        """
    elif icon_type == "iran":
        return """
        <svg viewBox="0 0 186 34" width="100%" height="34" xmlns="http://www.w3.org/2000/svg">
            <rect width="186" height="34" fill="#f8fafc" rx="2"/>
            <!-- Oil tanker -->
            <rect x="18" y="19" width="45" height="8" rx="1" fill="#334155"/>
            <rect x="22" y="15" width="8" height="4" fill="#475569"/>
            <rect x="52" y="13" width="7" height="6" fill="#64748b"/>
            <!-- Blockade dashed line barrier -->
            <line x1="85" y1="4" x2="85" y2="30" stroke="#dc2626" stroke-width="2.5" stroke-dasharray="3,2"/>
            <rect x="110" y="8" width="65" height="17" rx="2" fill="#15803d"/>
            <text x="142" y="20" fill="#ffffff" font-size="7.5" font-weight="700" text-anchor="middle" font-family="'IBM Plex Sans', sans-serif">TEHRAN: ALL TOOLS</text>
        </svg>
        """
    elif icon_type == "factory":
        return """
        <svg viewBox="0 0 186 34" width="100%" height="34" xmlns="http://www.w3.org/2000/svg">
            <rect width="186" height="34" fill="#fef2f2" rx="2"/>
            <!-- Sawtooth factory -->
            <polygon points="15,28 15,16 28,22 28,16 42,22 42,16 56,22 56,28" fill="#475569"/>
            <rect x="62" y="10" width="6" height="18" fill="#334155"/>
            <!-- Flames -->
            <path d="M72 26 Q 78 12 84 26 Q 88 16 94 26 Z" fill="#ea580c"/>
            <path d="M76 26 Q 81 18 86 26 Z" fill="#facc15"/>
            <circle cx="85" cy="10" r="5" fill="#94a3b8" opacity="0.6"/>
            <circle cx="92" cy="7" r="6" fill="#64748b" opacity="0.5"/>
            <rect x="122" y="6" width="56" height="15" rx="2" fill="#b91c1c"/>
            <text x="150" y="17" fill="#ffffff" font-size="7.5" font-weight="700" text-anchor="middle" font-family="'IBM Plex Sans', sans-serif">24 DEAD</text>
        </svg>
        """
    elif icon_type == "diplomacy":
        return """
        <svg viewBox="0 0 186 34" width="100%" height="34" xmlns="http://www.w3.org/2000/svg">
            <rect width="186" height="34" fill="#f0fdf4" rx="2"/>
            <!-- Interlocking diplomacy nodes -->
            <circle cx="32" cy="17" r="10" fill="#ea580c"/>
            <circle cx="48" cy="17" r="10" fill="#0284c7"/>
            <path d="M36 17 L44 17" stroke="#ffffff" stroke-width="2"/>
            <rect x="80" y="7" width="95" height="17" rx="2" fill="#15803d"/>
            <text x="127" y="19" fill="#ffffff" font-size="7.5" font-weight="700" text-anchor="middle" font-family="'IBM Plex Sans', sans-serif">$1.62B NEPAL AID</text>
        </svg>
        """
    elif icon_type == "scales":
        return """
        <svg viewBox="0 0 186 34" width="100%" height="34" xmlns="http://www.w3.org/2000/svg">
            <rect width="186" height="34" fill="#fdfbf7" rx="2"/>
            <!-- Scales of Justice -->
            <line x1="42" y1="8" x2="42" y2="28" stroke="#78350f" stroke-width="2"/>
            <line x1="26" y1="12" x2="58" y2="12" stroke="#78350f" stroke-width="1.8"/>
            <line x1="28" y1="12" x2="24" y2="20" stroke="#b45309" stroke-width="0.8"/>
            <line x1="28" y1="12" x2="32" y2="20" stroke="#b45309" stroke-width="0.8"/>
            <path d="M22 20 Q 28 23 34 20 Z" fill="#b45309"/>
            <line x1="56" y1="12" x2="52" y2="20" stroke="#b45309" stroke-width="0.8"/>
            <line x1="56" y1="12" x2="60" y2="20" stroke="#b45309" stroke-width="0.8"/>
            <path d="M50 20 Q 56 23 62 20 Z" fill="#b45309"/>
            <rect x="88" y="7" width="88" height="17" rx="2" fill="#1d4ed8"/>
            <text x="132" y="19" fill="#ffffff" font-size="7.5" font-weight="700" text-anchor="middle" font-family="'IBM Plex Sans', sans-serif">CASE SHELVED</text>
        </svg>
        """
    elif icon_type == "warrant":
        return """
        <svg viewBox="0 0 186 34" width="100%" height="34" xmlns="http://www.w3.org/2000/svg">
            <rect width="186" height="34" fill="#fafaf9" rx="2"/>
            <!-- Handcuffs silhouette -->
            <circle cx="32" cy="17" r="7" fill="none" stroke="#475569" stroke-width="2"/>
            <circle cx="54" cy="17" r="7" fill="none" stroke="#475569" stroke-width="2"/>
            <line x1="39" y1="17" x2="47" y2="17" stroke="#475569" stroke-width="2"/>
            <rect x="85" y="7" width="90" height="17" rx="2" fill="#c2410c"/>
            <text x="130" y="19" fill="#ffffff" font-size="7.5" font-weight="700" text-anchor="middle" font-family="'IBM Plex Sans', sans-serif">ARREST WARRANT</text>
        </svg>
        """
    elif icon_type == "nis":
        return """
        <svg viewBox="0 0 186 34" width="100%" height="34" xmlns="http://www.w3.org/2000/svg">
            <rect width="186" height="34" fill="#eff6ff" rx="2"/>
            <!-- NIS Shield -->
            <polygon points="35,6 48,10 48,22 35,28 22,22 22,10" fill="#1e3a8a"/>
            <polygon points="35,11 43,14 43,20 35,24 27,20 27,14" fill="#3b82f6"/>
            <rect x="68" y="7" width="108" height="17" rx="2" fill="#1e40af"/>
            <text x="122" y="19" fill="#ffffff" font-size="7.5" font-weight="700" text-anchor="middle" font-family="'IBM Plex Sans', sans-serif">1ST WOMAN NIS CHIEF</text>
        </svg>
        """
    elif icon_type == "cricket":
        return """
        <svg viewBox="0 0 186 34" width="100%" height="34" xmlns="http://www.w3.org/2000/svg">
            <rect width="186" height="34" fill="#fefce8" rx="2"/>
            <!-- Stumps & flying bails -->
            <line x1="25" y1="12" x2="25" y2="28" stroke="#854d0e" stroke-width="2"/>
            <line x1="32" y1="10" x2="32" y2="28" stroke="#854d0e" stroke-width="2"/>
            <line x1="39" y1="14" x2="39" y2="28" stroke="#854d0e" stroke-width="2"/>
            <line x1="28" y1="6" x2="36" y2="8" stroke="#ca8a04" stroke-width="1.8" transform="rotate(-30 32 7)"/>
            <circle cx="48" cy="18" r="4.5" fill="#dc2626"/>
            <rect x="75" y="7" width="100" height="17" rx="2" fill="#854d0e"/>
            <text x="125" y="19" fill="#ffffff" font-size="7.5" font-weight="700" text-anchor="middle" font-family="'IBM Plex Sans', sans-serif">BAN 91 ALL OUT</text>
        </svg>
        """
    elif icon_type == "secrets":
        return """
        <svg viewBox="0 0 186 34" width="100%" height="34" xmlns="http://www.w3.org/2000/svg">
            <rect width="186" height="34" fill="#fdf2f2" rx="2"/>
            <!-- Secret folder -->
            <polygon points="18,10 28,10 32,13 54,13 54,27 18,27" fill="#b91c1c"/>
            <rect x="22" y="15" width="28" height="9" fill="#ffffff"/>
            <text x="36" y="22" fill="#b91c1c" font-size="5.5" font-weight="800" text-anchor="middle">SECRETS</text>
            <rect x="68" y="7" width="108" height="17" rx="2" fill="#7f1d1d"/>
            <text x="122" y="19" fill="#ffffff" font-size="7.5" font-weight="700" text-anchor="middle" font-family="'IBM Plex Sans', sans-serif">DEATH SENTENCE</text>
        </svg>
        """
    return ""

# -----------------------------------------------------------------------------
# World Map SVG & Pin Placement
# -----------------------------------------------------------------------------

def relax_pin_positions(coords, min_dist=9.2, iterations=80, bounds=(9, 9, 331, 137)):
    """Collision avoidance relaxation to ensure circles and text never overlap."""
    pts = [list(pt) for pt in coords]
    n = len(pts)
    for _ in range(iterations):
        for i in range(n):
            for j in range(i + 1, n):
                dx = pts[j][0] - pts[i][0]
                dy = pts[j][1] - pts[i][1]
                dist = math.hypot(dx, dy)
                if dist < 0.001:
                    dx, dy, dist = 0.5, 0.5, 0.707
                if dist < min_dist:
                    overlap = (min_dist - dist) / 2.0
                    nx = (dx / dist) * overlap
                    ny = (dy / dist) * overlap
                    pts[i][0] -= nx
                    pts[i][1] -= ny
                    pts[j][0] += nx
                    pts[j][1] += ny
        for p in pts:
            p[0] = max(bounds[0], min(bounds[2], p[0]))
            p[1] = max(bounds[1], min(bounds[3], p[1]))
    return pts

def generate_world_map_svg() -> str:
    """Generate World Map SVG with landmasses and non-overlapping pins 1–30."""
    w, h = 340, 145
    # Calculate base equirectangular projection
    raw_coords = []
    for num, lat, lon in MAP_LOCATIONS:
        x = (lon + 180.0) / 360.0 * w
        y = (90.0 - lat) / 180.0 * h
        raw_coords.append((x, y))

    relaxed = relax_pin_positions(raw_coords, min_dist=9.2, iterations=80)

    # Simplified world continent landmasses
    map_svg = f"""
    <svg viewBox="0 0 {w} {h}" width="100%" height="100%" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
        <rect width="{w}" height="{h}" fill="#f0ebe1" rx="2" stroke="#d5cebe" stroke-width="1"/>
        <!-- Lat/Lon grid lines -->
        <line x1="0" y1="{h/2}" x2="{w}" y2="{h/2}" stroke="#e4ded0" stroke-width="0.8" stroke-dasharray="3,3"/>
        <line x1="{w/2}" y1="0" x2="{w/2}" y2="{h}" stroke="#e4ded0" stroke-width="0.8" stroke-dasharray="3,3"/>

        <!-- Continents -->
        <g fill="#dfd7c5" stroke="#cfc4b0" stroke-width="0.6">
            <!-- North America -->
            <path d="M 22 25 L 45 15 L 85 14 L 105 20 L 98 32 L 88 38 L 92 50 L 82 56 L 72 55 L 75 66 L 70 58 L 55 52 L 40 40 L 30 32 Z" />
            <!-- Greenland -->
            <path d="M 100 10 L 122 8 L 125 18 L 108 22 Z" />
            <!-- South America -->
            <path d="M 75 67 L 95 68 L 115 76 L 118 88 L 110 105 L 98 128 L 92 128 L 86 100 L 80 78 Z" />
            <!-- Europe -->
            <path d="M 160 38 L 168 34 L 175 26 L 188 18 L 192 25 L 184 28 L 198 25 L 202 36 L 188 38 L 184 45 L 172 44 L 162 42 Z" />
            <!-- Great Britain & Scandinavia -->
            <circle cx="166" cy="28" r="4" />
            <!-- Africa -->
            <path d="M 162 48 L 195 48 L 210 62 L 205 75 L 198 108 L 188 112 L 180 92 L 158 68 L 155 58 Z" />
            <circle cx="212" cy="95" r="3.5" /> <!-- Madagascar -->
            <!-- Asia -->
            <path d="M 202 24 L 240 18 L 285 20 L 295 32 L 280 42 L 272 55 L 260 66 L 245 68 L 235 55 L 218 52 L 212 42 L 202 36 Z" />
            <!-- Japan -->
            <path d="M 292 36 L 296 42 L 293 48 Z" />
            <!-- Southeast Asia & Indonesia -->
            <path d="M 255 76 L 278 77 L 272 82 L 252 80 Z" />
            <circle cx="280" cy="74" r="3" />
            <!-- Australia & Oceania -->
            <path d="M 278 95 L 305 88 L 318 94 L 315 114 L 300 118 L 282 112 Z" />
            <path d="M 325 116 L 330 124 L 322 126 Z" /> <!-- NZ -->
        </g>

        <!-- Pins 1–30 -->
        <g id="pins">
    """

    for i, (px, py) in enumerate(relaxed):
        num = i + 1
        # circle radius >= 4, font-size >= 5, lining-nums tabular-nums
        map_svg += f"""
        <g class="map-pin pin-{num}">
            <circle cx="{px:.1f}" cy="{py:.1f}" r="4.3" fill="#991b1b" stroke="#ffffff" stroke-width="0.8"/>
            <text x="{px:.1f}" y="{py + 1.8:.1f}" font-size="5.2" font-family="'IBM Plex Sans', sans-serif" font-weight="700" fill="#ffffff" text-anchor="middle">{num}</text>
        </g>
        """

    map_svg += """
        </g>
    </svg>
    """
    return map_svg

# -----------------------------------------------------------------------------
# CSS Styling & HTML Builder
# -----------------------------------------------------------------------------

def build_stylesheet() -> str:
    return """
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
        width: 1024px;
        height: 1024px;
        overflow: hidden;
        background-color: #f7f4eb;
        font-family: 'IBM Plex Sans', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        color: #1a1a1a;
        -webkit-font-smoothing: antialiased;
        padding: 12px 14px;
    }

    /* Masthead and Top Section */
    .top-eyebrow {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 7.2px;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        border-bottom: 1px solid #1a1a1a;
        padding-bottom: 2px;
        margin-bottom: 2px;
    }
    .eyebrow-center {
        color: #991b1b;
        font-weight: 800;
        letter-spacing: 0.8px;
    }
    .masthead {
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
        padding: 2px 0 3px 0;
    }
    .masthead-title {
        font-family: 'IBM Plex Serif', 'Playfair Display', Georgia, serif;
        font-size: 35px;
        font-weight: 800;
        letter-spacing: -0.5px;
        line-height: 1;
        color: #111111;
    }
    .masthead-meta {
        text-align: right;
        font-size: 7.2px;
        font-weight: 700;
        letter-spacing: 0.4px;
        line-height: 1.3;
        color: #333333;
    }
    .masthead-rule {
        border-top: 3px solid #111111;
        border-bottom: 1px solid #111111;
        height: 5px;
        margin-bottom: 3px;
    }
    .ticker-bar {
        font-size: 7.4px;
        font-style: italic;
        color: #262626;
        padding: 2px 0 3px 0;
        border-bottom: 1px solid #dcd7cb;
        margin-bottom: 4px;
        white-space: nowrap;
        overflow: hidden;
    }

    /* Region Pills */
    .pills-container {
        display: flex;
        justify-content: space-between;
        margin-bottom: 4px;
    }
    .pill {
        background: #eae4d5;
        border: 1px solid #cfc7b4;
        border-radius: 2px;
        padding: 2px 5px;
        font-size: 6.8px;
        font-weight: 700;
        letter-spacing: 0.3px;
        color: #2d2a26;
        display: flex;
        align-items: center;
        gap: 3px;
    }
    .pill-count {
        background: #1a1a1a;
        color: #ffffff;
        border-radius: 2px;
        padding: 0 3px;
        font-size: 6.2px;
        font-weight: 800;
    }

    /* Timeline Bar */
    .timeline-bar {
        background: #1c1917;
        color: #ffffff;
        border-radius: 2px;
        display: flex;
        align-items: center;
        padding: 3px 6px;
        font-size: 7.0px;
        margin-bottom: 5px;
        gap: 10px;
    }
    .timeline-badge {
        background: #d97706;
        color: #ffffff;
        font-weight: 800;
        padding: 1px 4px;
        border-radius: 2px;
        font-size: 6.8px;
        letter-spacing: 0.4px;
    }
    .timeline-item {
        display: flex;
        gap: 3px;
    }
    .timeline-time {
        color: #fbbf24;
        font-weight: 700;
    }

    /* Day in Numbers */
    .numbers-strip {
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 4px;
        margin-bottom: 6px;
    }
    .number-card {
        background: #ffffff;
        border: 1px solid #dcd7cb;
        border-radius: 2px;
        padding: 3px 4px;
        text-align: center;
    }
    .number-val {
        font-size: 12px;
        font-weight: 800;
        color: #991b1b;
        line-height: 1.1;
    }
    .number-lbl {
        font-size: 5.8px;
        font-weight: 600;
        color: #4b5563;
        line-height: 1.1;
        margin-top: 1px;
    }

    /* Lead Cards Grid (15 cards: 5x3) */
    .lead-grid {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        grid-template-rows: repeat(3, 140px);
        gap: 5px;
        margin-bottom: 6px;
    }
    .lead-card {
        background: #ffffff;
        border: 1px solid #dcd7cb;
        border-radius: 2px;
        padding: 4px 5px;
        display: flex;
        flex-direction: column;
        height: 140px;
    }
    .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 3px;
    }
    .card-header-left {
        display: flex;
        align-items: center;
        gap: 3px;
    }
    .card-num {
        background: #111111;
        color: #ffffff;
        font-size: 6.0px;
        font-weight: 800;
        width: 11px;
        height: 11px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .card-loc {
        font-size: 6.4px;
        font-weight: 800;
        color: #1f2937;
        letter-spacing: 0.2px;
    }
    .certainty-badge {
        font-size: 5.4px;
        font-weight: 800;
        padding: 0.5px 3px;
        border-radius: 2px;
        text-transform: uppercase;
        border: 1px solid currentColor;
    }
    .cert-confirmed { color: #991b1b; }
    .cert-official { color: #1d4ed8; }
    .cert-reported { color: #b45309; }
    .cert-ongoing { color: #b45309; }
    .cert-claim { color: #6b21a8; }

    .card-illustration {
        width: 100%;
        height: 42px;
        margin-bottom: 3px;
    }
    .card-headline {
        font-size: 8.0px;
        font-weight: 800;
        line-height: 9.6px;
        color: #0f172a;
        margin-bottom: 2px;
    }
    .card-body {
        font-size: 6.4px;
        line-height: 7.8px;
        color: #334155;
        flex-grow: 1;
    }
    .card-source {
        font-size: 5.4px;
        font-style: italic;
        color: #64748b;
        text-align: right;
        margin-top: 1px;
    }

    /* Briefs and Map Section */
    .middle-section {
        display: grid;
        grid-template-columns: 636px 350px;
        gap: 10px;
        height: 185px;
        margin-bottom: 6px;
    }
    .briefs-container {
        display: flex;
        flex-direction: column;
    }
    .section-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 7.0px;
        font-weight: 800;
        letter-spacing: 0.3px;
        text-transform: uppercase;
        border-bottom: 1px solid #111111;
        padding-bottom: 1.5px;
        margin-bottom: 4px;
    }
    .briefs-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        grid-template-rows: repeat(5, 31px);
        gap: 3px 6px;
    }
    .brief-item {
        font-size: 6.2px;
        line-height: 7.6px;
        color: #1e293b;
    }
    .brief-num {
        display: inline-block;
        background: #111111;
        color: #ffffff;
        font-size: 5.5px;
        font-weight: 800;
        width: 9px;
        height: 9px;
        border-radius: 50%;
        text-align: center;
        line-height: 9px;
        margin-right: 2px;
    }
    .brief-label {
        font-weight: 700;
        color: #0f172a;
    }
    .brief-cert {
        font-size: 5.0px;
        font-weight: 800;
        color: #1d4ed8;
        margin-left: 2px;
    }
    .brief-cert.claim { color: #6b21a8; }
    .brief-cert.reported { color: #b45309; }

    .map-container {
        display: flex;
        flex-direction: column;
    }
    .map-box {
        width: 100%;
        height: 165px;
    }

    /* Footer Section */
    .footer-section {
        display: grid;
        grid-template-columns: 636px 350px;
        gap: 10px;
        height: 125px;
    }
    .date-check-box {
        background: #ffffff;
        border: 1px solid #991b1b;
        border-radius: 2px;
        padding: 6px 8px;
    }
    .date-check-title {
        color: #991b1b;
        font-size: 8.0px;
        font-weight: 800;
        letter-spacing: 0.4px;
        margin-bottom: 3px;
        text-transform: uppercase;
    }
    .date-check-included {
        font-size: 7.0px;
        line-height: 8.8px;
        color: #1e293b;
        margin-bottom: 3px;
    }
    .date-check-leftout {
        font-size: 6.4px;
        line-height: 8.0px;
        color: #475569;
    }
    .how-sure-box {
        background: #ffffff;
        border: 1px solid #dcd7cb;
        border-radius: 2px;
        padding: 6px 8px;
    }
    .how-sure-title {
        color: #111111;
        font-size: 7.6px;
        font-weight: 800;
        letter-spacing: 0.4px;
        margin-bottom: 3px;
        text-transform: uppercase;
    }
    .how-sure-row {
        font-size: 6.4px;
        line-height: 8.6px;
        color: #334155;
    }
    .how-sure-note {
        font-size: 5.6px;
        font-style: italic;
        color: #64748b;
        margin-top: 3px;
    }

    /* Bottom Colophon */
    .colophon {
        text-align: right;
        font-size: 7.0px;
        color: #57534e;
        margin-top: 4px;
    }

    /* Fatal typography guarantee for footer years */
    span.year {
        font-size: 11px !important;
        font-weight: 700 !important;
        font-family: 'IBM Plex Sans', 'Inter', sans-serif !important;
        letter-spacing: 0.15px !important;
        font-variant-numeric: lining-nums tabular-nums !important;
        display: inline-block;
        color: inherit;
        line-height: 1;
    }
    """

def build_html() -> str:
    """Build the editorial broadsheet HTML document."""
    # Compose Region Pills
    pills_html = []
    for reg, cnt in REGION_PILLS:
        pills_html.append(f'<div class="pill">{reg} <span class="pill-count">{cnt}</span></div>')
    pills_str = "\n".join(pills_html)

    # Compose Timeline Events
    timeline_html = ['<div class="timeline-badge">THE DAY IN UTC</div>']
    for t_time, t_text in TIMELINE_EVENTS:
        timeline_html.append(
            f'<div class="timeline-item"><span class="timeline-time">{t_time}</span> <span>{t_text}</span></div>'
        )
    timeline_str = " · ".join(timeline_html[1:])
    timeline_full = f'<div class="timeline-bar">{timeline_html[0]} {timeline_str}</div>'

    # Compose Day in Numbers
    numbers_html = []
    for val, lbl in DAY_IN_NUMBERS:
        numbers_html.append(f"""
        <div class="number-card">
            <div class="number-val">{val}</div>
            <div class="number-lbl">{lbl}</div>
        </div>
        """)
    numbers_str = "\n".join(numbers_html)

    # Compose Lead Stories (1–15)
    lead_cards_html = []
    for item in LEAD_STORIES:
        cert_class = f"cert-{item['certainty'].lower()}"
        icon_svg = get_card_icon_svg(item['icon'])
        lead_cards_html.append(f"""
        <div class="lead-card">
            <div class="card-header">
                <div class="card-header-left">
                    <span class="card-num">{item['num']}</span>
                    <span class="card-loc">{item['loc']}</span>
                </div>
                <span class="certainty-badge {cert_class}">{item['certainty']}</span>
            </div>
            <div class="card-illustration">{icon_svg}</div>
            <div class="card-headline">{item['headline']}</div>
            <div class="card-body">{item['body']}</div>
            <div class="card-source">{item['source']}</div>
        </div>
        """)
    lead_cards_str = "\n".join(lead_cards_html)

    # Compose Briefs (16–30)
    briefs_html = []
    for b in BRIEF_STORIES:
        cert_cls = "claim" if b['certainty'] == "CLAIM" else ("reported" if b['certainty'] == "REPORTED" else "official")
        briefs_html.append(f"""
        <div class="brief-item">
            <span class="brief-num">{b['num']}</span>
            <span class="brief-label">{b['label']}:</span> {b['text']}
            <span class="brief-cert {cert_cls}">[{b['certainty']}]</span>
        </div>
        """)
    briefs_str = "\n".join(briefs_html)

    # World map SVG
    world_map_svg = generate_world_map_svg()

    # Compose Complete HTML
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Verified Global Broadsheet - Monday 23 November 2026</title>
    <style>
{build_stylesheet()}
    </style>
</head>
<body>
    <!-- Top Eyebrow -->
    <div class="top-eyebrow">
        <span>THE WORLD IN ONE DAY · VERIFIED GLOBAL BROADSHEET</span>
        <span class="eyebrow-center">30 DATED STORIES · 9 REGIONS · STRICT UTC VERIFICATION</span>
        <span>PRICE: OPEN RECORD · ED. <span class="year">2026</span>.11.23</span>
    </div>

    <!-- Masthead -->
    <div class="masthead">
        <h1 class="masthead-title">Monday 23 November 2026</h1>
        <div class="masthead-meta">
            <div>FINAL GLOBAL COMPILATION</div>
            <div>ALL EVENTS REPORTED ON THIS ONE DAY</div>
        </div>
    </div>
    <div class="masthead-rule"></div>

    <!-- Subhead ticker -->
    <div class="ticker-bar">
        Ukraine confirms 7 drones sank corvette Merkury at Benghazi &nbsp;·&nbsp;
        Dymer rescue ends, toll 11 &nbsp;·&nbsp;
        COP31 fallout: Bowen faces resignation calls &nbsp;·&nbsp;
        Huang reinstated at Nvidia (+31.5%) &nbsp;·&nbsp;
        NATO AWACS to Poland &nbsp;·&nbsp;
        India pledges $1.62B Nepal aid
    </div>

    <!-- Region Pills -->
    <div class="pills-container">
        {pills_str}
    </div>

    <!-- UTC Timeline -->
    {timeline_full}

    <!-- Day in Numbers -->
    <div class="numbers-strip">
        {numbers_str}
    </div>

    <!-- 15 Illustrated Lead Cards -->
    <div class="lead-grid">
        {lead_cards_str}
    </div>

    <!-- Middle-Bottom Section: Briefs & Map -->
    <div class="middle-section">
        <div class="briefs-container">
            <div class="section-header">
                <span>ALSO ON MONDAY 23 NOVEMBER <span class="year">2026</span> · VERIFIED WORLD BRIEFS</span>
                <span>15 ADDITIONAL DATED DISPATCHES</span>
            </div>
            <div class="briefs-grid">
                {briefs_str}
            </div>
        </div>
        <div class="map-container">
            <div class="section-header">
                <span>WHERE IT HAPPENED · GEOGRAPHIC LOCATOR</span>
                <span>PINS 1–30</span>
            </div>
            <div class="map-box">
                {world_map_svg}
            </div>
        </div>
    </div>

    <!-- Footer Section: DATE CHECK & HOW SURE -->
    <div class="footer-section">
        <div class="date-check-box">
            <div class="date-check-title">DATE CHECK · STRICT MONDAY 23 NOVEMBER <span class="year">2026</span> AUDIT (UTC)</div>
            <p class="date-check-included"><strong>INCLUDED:</strong> Every story on this broadsheet happened or was first reported on Monday 23 November <span class="year">2026</span> (UTC).</p>
            <p class="date-check-leftout"><strong>LEFT OUT (earlier days):</strong> COP31 closing plenary &amp; no-deal gavel (Sunday 22 Nov); Dymer initial 186-drone attack &amp; 6-dead toll (Sunday; Monday was 11-dead toll &amp; search conclusion); pre-dawn Benghazi explosions (Sunday; Ukrainian official confirmation Monday); US Democrats reaching 258 House seats (Sunday call); Sunday sports: Verstappen Las Vegas GP, Alcaraz ATP Finals, Márquez 8th MotoGP title, HK committee poll 98.79%, India 720/9, Liverpool 4-0 Man Utd; Saturday Cikande confectionery fire start (Monday 24 confirmed dead) &amp; Baltic Sparta II fire; Friday Polish border Kh-101 missiles (Monday AWACS deployment).</p>
        </div>
        <div class="how-sure-box">
            <div class="how-sure-title">HOW SURE · CERTAINTY CALIBRATION</div>
            <div class="how-sure-row"><strong>CONFIRMED:</strong> 2+ independent global news wire outlets.</div>
            <div class="how-sure-row"><strong>OFFICIAL:</strong> Government, court, military, or agency on record.</div>
            <div class="how-sure-row"><strong>REPORTED:</strong> Single reputable global wire or broadcaster.</div>
            <div class="how-sure-row"><strong>CLAIM:</strong> One side's allegation; explicitly attributed.</div>
            <div class="how-sure-row"><strong>ONGOING:</strong> Search, rescue, or disaster operations in progress.</div>
            <div class="how-sure-note">Illustrations are drawn editorial vector artwork, not photographs.</div>
        </div>
    </div>

    <!-- Bottom Colophon -->
    <div class="colophon">
        Deterministic compilation for make.fun news-image-20261123 · Mon 23 Nov <span class="year">2026</span>
    </div>
</body>
</html>
"""
    return html_content

# -----------------------------------------------------------------------------
# Headless Chrome Rendering & Deterministic Output
# -----------------------------------------------------------------------------

def render_image(html_str: str, output_path: str):
    """Render HTML to 1024x1024 RGB PNG using Headless Chrome and Pillow."""
    with tempfile.NamedTemporaryFile(suffix=".html", mode="w", delete=False, encoding="utf-8") as f:
        f.write(html_str)
        temp_html = f.name

    temp_png = temp_html.replace(".html", ".png")

    chrome_cmd = [
        "timeout", "60s",
        "/opt/google/chrome/chrome",
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--hide-scrollbars",
        "--force-device-scale-factor=1",
        "--run-all-compositor-stages-before-draw",
        "--no-first-run",
        "--no-default-browser-check",
        '--host-rules="MAP * ~NOTFOUND"',
        "--window-size=1024,1024",
        f"--screenshot={temp_png}",
        f"file://{temp_html}",
    ]

    try:
        subprocess.run(
            " ".join(chrome_cmd),
            shell=True,
            check=True,
            timeout=60,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        im = Image.open(temp_png).convert("RGB")
        if im.size != (1024, 1024):
            im = im.resize((1024, 1024), Image.Resampling.LANCZOS)

        # Save deterministically
        im.save(output_path, format="PNG", optimize=True)

    finally:
        if os.path.exists(temp_html):
            os.remove(temp_html)
        if os.path.exists(temp_png):
            os.remove(temp_png)

    # Verify output size and SHA-256
    with open(output_path, "rb") as f:
        bytes_data = f.read()

    size = len(bytes_data)
    sha256 = hashlib.sha256(bytes_data).hexdigest()
    print(f"Generated {output_path}: {size} bytes, SHA-256: {sha256}")

    if size == 0 or size > 1048576:
        raise ValueError(f"Generated image exceeds 1MB limit: {size} bytes")

def main():
    workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    output_path = os.path.join(workspace_root, "entry.png")
    html_content = build_html()
    render_image(html_content, output_path)

if __name__ == "__main__":
    main()
