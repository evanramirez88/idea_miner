# Idea Miner

Idea Miner is a command line application that analyzes ChatGPT conversation export files
(JSON or ZIP) to identify recurring themes, key topics, and sentiment trends. The tool
was inspired by the insights requested in `idea_miner_draft.txt` and helps surface
opportunities for new product ideas based on past conversations.

## Features

- Parses large ChatGPT conversation exports (`.json` or `.zip`).
- Extracts message text, tokenizes, and identifies the most frequent keywords.
- Uses a lightweight lexicon-based sentiment analyzer to summarize emotional tone.
- Highlights recurring themes aligned to consulting focus areas (Toast POS,
  automation, data integration, field services, and web development).
- Generates actionable opportunity statements for the detected themes.
- Produces both JSON and Markdown reports that can be shared with stakeholders.

## Quick start

1. (Optional) create and activate a virtual environment.
2. Install the project in editable mode with development dependencies:

   ```bash
   pip install -e .[dev]
   ```

3. Run the analyzer against one or more export files:

   ```bash
   idea-miner 12-24-23_conversations.json 12-30-23_conversations.json
   ```

   Reports will be written to the `analysis_output/` directory by default. You can
   change the location with `--output-dir`.

4. Review the generated files:

   - `analysis_output/analysis_report.json`
   - `analysis_output/analysis_report.md`

## Running tests

```bash
pytest
```

## Project structure

```
├── pyproject.toml
├── src
│   └── idea_miner
│       ├── __init__.py
│       ├── analysis.py
│       ├── loader.py
│       ├── main.py
│       └── report.py
└── tests
    └── ...
```

## Limitations

- The theme detection relies on keyword heuristics and may miss nuanced topics.
- Sentiment scoring uses a lexicon-based approach and should be interpreted as a
  directional signal.
- Very large exports may take several minutes to process depending on available memory.

## License

This project is provided for analytical and educational purposes.
