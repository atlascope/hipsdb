# hips
A Django app for storing and serving HiPS data

## Setup

1. **Install project dependencies.** If you are using Nix, run `nix develop` to
   install dependencies; otherwise, ensure that you have Python 3.10 and `uv`
   0.7.19 (or more recent) installed.
2. **Install Python dependencies.** Run `uv sync --dev`. This will create a
   virtual environment in the `.venv` directory.
3. **Optional: Activate virtual environment.** Run `source .venv/bin/activate`
   (or similar) to activate the virtual environment. This step is optional; you
   can skip it and run Python commands by prefixing with `uv run` as well.

## Validate a HiPS data directory

To validate a HiPS data directory, you can run the validator as a Python script
with `python -m hips_etl`. That invocation will show a usage message; to
validate a directory, supply a data directory as an argument.

## Run tests

To run the tests, simply run `pytest` at the top level of the repository.

## Run linting/formatting

To run the linter, use the `ruff check` (to display linting errors) and `ruff
check --fix` (to autofix them) commands.

To run the formatter, use the `ruff format --check` or `ruff format --diff` (to
indicate/display formatting issues) and `ruff format` (to autofix them)
commands.
