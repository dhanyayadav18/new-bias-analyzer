# News Framing & Bias Analysis System

An automated data pipeline and NLP platform designed to analyze news framing, political stance, entity omissions, and sentiment divergence across multi-outlet coverage of identical events.

---

## Overview

Media outlets frequently cover identical events using contrasting narrative frames, selective source attributions, and entity omissions. This project provides a programmatic infrastructure to:

1. **Ingest & Extract:** Automatically collect and parse full-text news coverage from major global and domestic Indian outlets via standardized RSS feeds.
2. **Normalize & Persist:** Hash, deduplicate, and store structured metadata in a relational database engine.
3. **Analyze (In Progress):** Perform Named Entity Recognition (NER), stance detection, and omission scoring across outlet pairs.
4. **Visualize (Planned):** Present comparative bias metrics through an interactive analytical dashboard.

---

## Architecture & Data Flow

```text
   [ Domestic & Global RSS Feeds ]
                  │
                  ▼
      [ Ingestion Engine ]
   (feedparser + newspaper4k)
                  │
                  ▼
       [ Deduplication Layer ]
       (SHA-256 URL Hashing)
                  │
                  ▼
       [ Persistence Layer ]
       (SQLAlchemy + SQLite)
                  │
                  ▼
   [ Auto-Retention Purge (14d) ]
