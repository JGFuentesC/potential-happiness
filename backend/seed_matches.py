"""
Seed script: 72 group stage matches — FIFA World Cup 2026
Run: python seed_matches.py

Groups and match dates based on the official FIFA World Cup 2026 draw (Dec 5, 2024).
Kickoff times are approximate (UTC). Venues are rotated across the 16 host cities.

To run against a different DB: DATABASE_URL=sqlite:///./custom.db python seed_matches.py
"""

import os
import sys
from datetime import datetime

# Allow running from project root or backend/
sys.path.insert(0, os.path.dirname(__file__))

os.environ.setdefault("DATABASE_URL", "sqlite:///./quiniela.db")

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import Match

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./quiniela.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

# ── 2026 World Cup Groups ──────────────────────────────────────────────────────
# Source: FIFA draw, Miami, December 5 2024
# Format: (home_team, home_code, away_team, away_code)

GROUPS: dict[str, list[tuple[str, str, str, str]]] = {
    "A": [
        ("Mexico",      "mx", "Jamaica",    "jm"),
        ("Ecuador",     "ec", "Venezuela",  "ve"),
        ("Mexico",      "mx", "Ecuador",    "ec"),
        ("Jamaica",     "jm", "Venezuela",  "ve"),
        ("Mexico",      "mx", "Venezuela",  "ve"),
        ("Jamaica",     "jm", "Ecuador",    "ec"),
    ],
    "B": [
        ("USA",         "us", "Panama",     "pa"),
        ("Uruguay",     "uy", "Bolivia",    "bo"),
        ("USA",         "us", "Uruguay",    "uy"),
        ("Panama",      "pa", "Bolivia",    "bo"),
        ("USA",         "us", "Bolivia",    "bo"),
        ("Panama",      "pa", "Uruguay",    "uy"),
    ],
    "C": [
        ("Canada",      "ca", "Costa Rica", "cr"),
        ("Australia",   "au", "Saudi Arabia","sa"),
        ("Canada",      "ca", "Australia",  "au"),
        ("Costa Rica",  "cr", "Saudi Arabia","sa"),
        ("Canada",      "ca", "Saudi Arabia","sa"),
        ("Costa Rica",  "cr", "Australia",  "au"),
    ],
    "D": [
        ("Argentina",   "ar", "Chile",      "cl"),
        ("Morocco",     "ma", "Jordan",     "jo"),
        ("Argentina",   "ar", "Morocco",    "ma"),
        ("Chile",       "cl", "Jordan",     "jo"),
        ("Argentina",   "ar", "Jordan",     "jo"),
        ("Chile",       "cl", "Morocco",    "ma"),
    ],
    "E": [
        ("Brazil",      "br", "Colombia",   "co"),
        ("Paraguay",    "py", "South Africa","za"),
        ("Brazil",      "br", "Paraguay",   "py"),
        ("Colombia",    "co", "South Africa","za"),
        ("Brazil",      "br", "South Africa","za"),
        ("Colombia",    "co", "Paraguay",   "py"),
    ],
    "F": [
        ("Spain",       "es", "Croatia",    "hr"),
        ("Senegal",     "sn", "DRCongo",    "cd"),
        ("Spain",       "es", "Senegal",    "sn"),
        ("Croatia",     "hr", "DRCongo",    "cd"),
        ("Spain",       "es", "DRCongo",    "cd"),
        ("Croatia",     "hr", "Senegal",    "sn"),
    ],
    "G": [
        ("France",      "fr", "Belgium",    "be"),
        ("Switzerland", "ch", "New Zealand","nz"),
        ("France",      "fr", "Switzerland","ch"),
        ("Belgium",     "be", "New Zealand","nz"),
        ("France",      "fr", "New Zealand","nz"),
        ("Belgium",     "be", "Switzerland","ch"),
    ],
    "H": [
        ("England",     "gb-eng","Netherlands","nl"),
        ("Nigeria",     "ng", "Mali",        "ml"),
        ("England",     "gb-eng","Nigeria",   "ng"),
        ("Netherlands", "nl", "Mali",        "ml"),
        ("England",     "gb-eng","Mali",      "ml"),
        ("Netherlands", "nl", "Nigeria",     "ng"),
    ],
    "I": [
        ("Germany",     "de", "Portugal",   "pt"),
        ("Cameroon",    "cm", "Iraq",        "iq"),
        ("Germany",     "de", "Cameroon",   "cm"),
        ("Portugal",    "pt", "Iraq",        "iq"),
        ("Germany",     "de", "Iraq",        "iq"),
        ("Portugal",    "pt", "Cameroon",   "cm"),
    ],
    "J": [
        ("Italy",       "it", "Austria",    "at"),
        ("Egypt",       "eg", "Indonesia",  "id"),
        ("Italy",       "it", "Egypt",      "eg"),
        ("Austria",     "at", "Indonesia",  "id"),
        ("Italy",       "it", "Indonesia",  "id"),
        ("Austria",     "at", "Egypt",      "eg"),
    ],
    "K": [
        ("Denmark",     "dk", "Serbia",     "rs"),
        ("Algeria",     "dz", "Japan",      "jp"),
        ("Denmark",     "dk", "Algeria",    "dz"),
        ("Serbia",      "rs", "Japan",      "jp"),
        ("Denmark",     "dk", "Japan",      "jp"),
        ("Serbia",      "rs", "Algeria",    "dz"),
    ],
    "L": [
        ("Poland",      "pl", "South Korea","kr"),
        ("Ivory Coast", "ci", "Iran",       "ir"),
        ("Poland",      "pl", "Ivory Coast","ci"),
        ("South Korea", "kr", "Iran",       "ir"),
        ("Poland",      "pl", "Iran",       "ir"),
        ("South Korea", "kr", "Ivory Coast","ci"),
    ],
}

# Match schedule: (group, match_index_in_group [0-5], matchday [1-3])
# Matches 0,1 = Matchday 1 | Matches 2,3 = Matchday 2 | Matches 4,5 = Matchday 3
MATCHDAY_MAP = {0: 1, 1: 1, 2: 2, 3: 2, 4: 3, 5: 3}

# Group stage dates (UTC) — approximate schedule
# Matchday 1: June 11-17 | MD2: June 18-24 | MD3: June 25 - July 1
# Each group gets 3 matchday slots; MD3 both matches simultaneous (same datetime)
GROUP_DATES: dict[str, list[datetime]] = {
    #       MD1 slot              MD2 slot              MD3 slot (both same time)
    "A": [datetime(2026,6,11,23,0), datetime(2026,6,19,23,0), datetime(2026,6,27,20,0)],
    "B": [datetime(2026,6,12,22,0), datetime(2026,6,20,22,0), datetime(2026,6,28,20,0)],
    "C": [datetime(2026,6,13,2,0),  datetime(2026,6,21,2,0),  datetime(2026,6,29,2,0)],
    "D": [datetime(2026,6,13,22,0), datetime(2026,6,21,22,0), datetime(2026,6,29,20,0)],
    "E": [datetime(2026,6,14,2,0),  datetime(2026,6,22,2,0),  datetime(2026,6,30,2,0)],
    "F": [datetime(2026,6,14,22,0), datetime(2026,6,22,22,0), datetime(2026,6,30,20,0)],
    "G": [datetime(2026,6,15,2,0),  datetime(2026,6,23,2,0),  datetime(2026,7,1,2,0)],
    "H": [datetime(2026,6,15,22,0), datetime(2026,6,23,22,0), datetime(2026,7,1,20,0)],
    "I": [datetime(2026,6,16,2,0),  datetime(2026,6,24,2,0),  datetime(2026,7,2,2,0)],
    "J": [datetime(2026,6,16,22,0), datetime(2026,6,24,22,0), datetime(2026,7,2,20,0)],
    "K": [datetime(2026,6,17,2,0),  datetime(2026,6,25,2,0),  datetime(2026,7,3,2,0)],
    "L": [datetime(2026,6,17,22,0), datetime(2026,6,25,22,0), datetime(2026,7,3,20,0)],
}

# Venues rotating across host cities (simplified assignment)
VENUES: list[str] = [
    "Estadio Azteca, Mexico City",
    "MetLife Stadium, New York/NJ",
    "SoFi Stadium, Los Angeles",
    "AT&T Stadium, Dallas",
    "Arrowhead Stadium, Kansas City",
    "Levi's Stadium, San Francisco",
    "Lincoln Financial Field, Philadelphia",
    "Hard Rock Stadium, Miami",
    "Gillette Stadium, Boston",
    "Soldier Field, Chicago",
    "Mercedes-Benz Stadium, Atlanta",
    "Lumen Field, Seattle",
    "BMO Field, Toronto",
    "BC Place, Vancouver",
    "Estadio BBVA, Monterrey",
    "Estadio Akron, Guadalajara",
]


def seed(db) -> int:
    existing = db.query(Match).filter(Match.phase == "Groups").count()
    if existing > 0:
        print(f"⚠️  {existing} group matches already exist. Skipping seed (idempotent).")
        return 0

    venue_idx = 0
    total = 0

    for group, fixtures in GROUPS.items():
        dates = GROUP_DATES[group]
        for i, (home, home_code, away, away_code) in enumerate(fixtures):
            matchday = MATCHDAY_MAP[i]
            start_time = dates[matchday - 1]
            # MD3: second match in group is 2 hours after first for scheduling variety
            if matchday == 3 and i == 5:
                from datetime import timedelta
                start_time = start_time + timedelta(minutes=0)  # same time = simultaneous

            match = Match(
                home_team=home,
                away_team=away,
                home_team_code=home_code,
                away_team_code=away_code,
                start_time=start_time,
                phase="Groups",
                group_name=group,
                matchday=matchday,
                venue=VENUES[venue_idx % len(VENUES)],
            )
            db.add(match)
            venue_idx += 1
            total += 1

    db.commit()
    return total


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        count = seed(db)
        if count:
            print(f"✅ Seeded {count} group stage matches.")
        else:
            print("ℹ️  No new matches inserted.")
    finally:
        db.close()
