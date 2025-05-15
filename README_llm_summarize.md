# Git Diff Summarizer with Claude 3.7

A simple utility that uses Claude 3.7 to summarize git diff output, providing a concise explanation of the changes made.

## Setup

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Set your Anthropic API key as an environment variable:
   ```
   export ANTHROPIC_API_KEY=your_api_key_here
   ```

## Usage

### Basic Usage

```bash
./llm_summarize path/to/diff_file.diff
```

### Using a Custom Prompt

You can provide a custom prompt template file:

```bash
./llm_summarize path/to/diff_file.diff --prompt path/to/custom_prompt.txt
```

### Generating a Diff File

You can generate a diff file using git commands:

```bash
# For uncommitted changes
git diff > changes.diff

# For changes between commits
git diff commit1..commit2 > changes.diff

# For changes in a specific file
git diff -- path/to/file > changes.diff
```

## Prompt Template

The default prompt template is located in `prompt.txt`. You can customize it for your specific needs. The template uses the `${diff_content}` variable to insert the git diff content.

## Example

```bash
# Generate a diff file
git diff HEAD~1 > recent_changes.diff

# Summarize the changes
./llm_summarize recent_changes.diff
``` 