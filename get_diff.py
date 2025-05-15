import argparse
import logging
import os
import subprocess
import sys
import tempfile
from typing import Optional, List, Tuple

# --- Logging Setup ---
log_formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
log_handler = logging.StreamHandler(sys.stdout)  # Log to console
log_handler.setFormatter(log_formatter)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)
# --- End Logging Setup ---


def _parse_diff_output(diff_text: str) -> tuple[int, int]:
    """Parses raw diff text to count additions and deletions."""
    additions = 0
    deletions = 0
    try:
        lines = diff_text.splitlines()
        for line in lines:
            if line.startswith("+") and not line.startswith("+++"):
                additions += 1
            elif line.startswith("-") and not line.startswith("---"):
                deletions += 1
    except Exception as e:
        logger.warning(f"Could not parse diff line counts: {e}")
    return additions, deletions


def analyze_fork_differences(
    original_repo_url: str,
    fork_repo_url: str,
    fork_repo_branch: str,
    original_repo_branch: str = "develop",
    file_filters: Optional[List[str]] = None,
) -> Tuple[str, Tuple[int, int]]:
    """
    Analyzes differences between an original repository and a specific fork.

    Args:
        original_repo_url: The clone URL of the original repository.
        fork_repo_url: The clone URL of the forked repository.
        fork_repo_branch: The branch of the fork to compare.
        original_repo_branch: The branch of the original repository to compare against.
        file_filters: Optional list of file patterns to filter the diff (e.g., ["*.py", "*.js"]).

    Returns:
        A tuple containing:
            - The raw diff output as a string
            - A tuple of (additions, deletions) counts
    """
    if file_filters is None:
        file_filters = []

    with tempfile.TemporaryDirectory() as tmpdir:
        logger.info(f"Created temporary directory: {tmpdir}")

        forked_path = os.path.join(tmpdir, "forked")

        clone_cmd = [
            "git",
            "clone",
            "--branch",
            fork_repo_branch,
            fork_repo_url,
            forked_path,
        ]
        logger.info(
            f"Cloning fork repository {fork_repo_url} branch {fork_repo_branch}..."
        )
        logger.info(f"Executing command: {' '.join(clone_cmd)}")
        try:
            subprocess.run(
                clone_cmd,
                check=True,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to clone fork repository: {e.stderr}")
            sys.exit(1)

        add_remote_cmd = ["git", "remote", "add", "upstream", original_repo_url]
        logger.info(
            f"Adding original repository {original_repo_url} as upstream remote..."
        )
        logger.info(f"Executing command: {' '.join(add_remote_cmd)}")
        try:
            subprocess.run(
                add_remote_cmd,
                cwd=forked_path,
                check=True,
                capture_output=True,
            )
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to add upstream remote: {e.stderr}")
            sys.exit(1)

        fetch_upstream_cmd = ["git", "fetch", "upstream", original_repo_branch]
        logger.info(f"Fetching upstream {original_repo_branch} branch...")
        logger.info(f"Executing command: {' '.join(fetch_upstream_cmd)}")
        try:
            subprocess.run(
                fetch_upstream_cmd,
                cwd=forked_path,
                check=True,
                capture_output=True,
            )
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to fetch upstream branch: {e.stderr}")
            sys.exit(1)

        diff_cmd = ["git", "diff", f"upstream/{original_repo_branch}...HEAD"]
        if file_filters:
            diff_cmd.append("--")
            diff_cmd.extend(file_filters)

        logger.info(f"Running diff command: {' '.join(diff_cmd)}")
        # Revert to check=False for git diff as it has specific exit codes
        # 0 = no diff, 1 = diff found, >1 = error
        result = subprocess.run(
            diff_cmd,
            cwd=forked_path,
            check=False,
            capture_output=True,
            text=True,
        )

        # Handle potential errors from git diff if returncode is not 0 or 1
        if result.returncode > 1:
            logger.error(
                f"Git diff command failed with return code {result.returncode}: {result.stderr}"
            )
            sys.exit(1)

        if not result.stdout and result.returncode == 0:
            logger.info("No differences found between branches.")
        elif not result.stdout and result.returncode == 1:
            logger.warning(
                "Git diff reported differences (exit code 1) but produced no stdout.Stderr: {result.stderr}"
            )

        diff_output = result.stdout
        additions, deletions = _parse_diff_output(diff_output)
        logger.info(
            f"Diff analysis complete: {additions} additions, {deletions} deletions"
        )

        return diff_output, (additions, deletions)


def main():
    parser = argparse.ArgumentParser(
        description="Collect code differences between a fork and its original repository."
    )
    parser.add_argument(
        "fork_url",
        help="URL of the forked GitHub repository (e.g., https://github.com/user/repo.git)",
    )
    parser.add_argument("fork_branch", help="Branch in the forked repository")
    parser.add_argument(
        "--original_url",
        help="URL of the original GitHub repository (e.g., https://github.com/owner/repo.git)",
        default="https://github.com/HumanSignal/label-studio",
    )
    parser.add_argument(
        "--original_branch", help="Branch in the original repository", default="develop"
    )
    parser.add_argument(
        "--output_file",
        help="Path to the plain text file to save the diff output",
        default="diff.txt",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose logging (DEBUG level)",
    )
    parser.add_argument(
        "-f",
        "--file-filters",
        nargs="+",
        help="File filters to apply to the diff (e.g., *.py, *.js)",
        default=[
            "*.py", "*.js", "*.jsx", "*.ts", "*.tsx",
            ":(exclude)**/dist/**",
            ":(exclude)**/build/**",
            ":(exclude)**/node_modules/**",
            ":(exclude)**/.cache/**",
            ":(exclude)**/coverage/**",
            ":(exclude)**/*.min.js",
            ":(exclude)**/*.bundle.js",
            ":(exclude)**/*.chunk.js",
            ":(exclude)**/*.generated.*",
            ":(exclude)**/*.d.ts",
            ":(exclude)**/package-lock.json",
            ":(exclude)**/yarn.lock"
        ],
    )

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)
        for handler in logger.handlers:
            handler.setLevel(logging.DEBUG)
        logger.debug("Verbose logging enabled.")

    logger.info(
        f"Starting diff collection for fork: {args.fork_url} (branch: {args.fork_branch}) "
        f"against original: {args.original_url} (branch: {args.original_branch})"
    )

    diff_text, (additions, deletions) = analyze_fork_differences(
        original_repo_url=args.original_url,
        fork_repo_url=args.fork_url,
        fork_repo_branch=args.fork_branch,
        original_repo_branch=args.original_branch,
        file_filters=args.file_filters,
    )

    try:
        with open(args.output_file, "w", encoding="utf-8") as f:
            f.write(diff_text)
        logger.info(f"Successfully saved diff output to {args.output_file}")
        print(f"Diff output saved to: {args.output_file}")
        print(f"Summary: {additions} additions, {deletions} deletions.")
    except IOError as e:
        logger.error(f"Failed to write diff to output file {args.output_file}: {e}")
        print(f"Error: Could not write to file {args.output_file}: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
