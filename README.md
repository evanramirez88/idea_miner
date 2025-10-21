# Idea Miner

Idea Miner is a command-line analytics toolkit that processes ChatGPT conversation exports and distills the dominant themes, keywords, sentiment, and strategic opportunities.

## Features

- Loads ChatGPT export JSON files or ZIP archives
- Extracts message transcripts and aggregates participants & timelines
- Highlights dominant keywords and bigrams across the corpus
- Provides rule-based sentiment scoring tuned for business conversations
- Buckets conversations into curated business themes
- Suggests strategic initiatives tailored to the detected focus areas
- Exports human-friendly text or Markdown reports

## Installation

1. Create a virtual environment (optional but recommended).
2. Install the required dependency:

```bash
pip install -r requirements.txt
```

## Usage

Generate a text report by pointing the CLI at one or more export files:

```bash
python -m idea_miner.cli 12-24-23_conversations.json
```

Create a Markdown report and save it to disk:

```bash
python -m idea_miner.cli 12-24-23_conversations.json 12-30-23_conversations.json \
  "RG_10-21-25_conversations - Copy.zip" --format markdown --output report.md
```

The CLI supports both JSON exports and ZIP archives that contain JSON transcripts.

## Running Tests

```bash
pytest
```
