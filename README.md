# GitHub Fork Diff Summarizer

A tool to analyze and summarize differences between a forked GitHub repository and its original repository.

## Features

- Analyzes differences between a forked GitHub repository and its original
- Generates a detailed diff output
- Summarizes the changes using an LLM
- Filters files to focus on relevant code changes

## Installation

### Using uv (Recommended)

The fastest way to install dependencies is with [uv](https://github.com/astral-sh/uv), a fast Python package installer written in Rust.

1. Install uv:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Install dependencies:

```bash
uv pip install -r requirements.txt
```

### Traditional pip

If you prefer using pip:

```bash
pip install -r requirements.txt
```

## Usage

Run the `diff_summarizer.sh` script with the fork URL and branch name:

```bash
./diff_summarizer.sh <fork_repository_url> <fork_branch_name>
```

Example:

```bash
./diff_summarizer.sh https://github.com/user/forked-repo.git main
```

By default, the script compares against the `develop` branch of the original repository (https://github.com/HumanSignal/label-studio).

## Advanced Usage

If you need more control, you can run `get_diff.py` directly:

```bash
python get_diff.py <fork_url> <fork_branch> [--original_url ORIGINAL_URL] [--original_branch ORIGINAL_BRANCH] [--output_file OUTPUT_FILE] [--file-filters FILTERS]
```

See `python get_diff.py --help` for more details.

## Requirements

- Python 3.6+
- Git
- `llm_summarize` tool (for summarization)
