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

## Work with data

### Validate and ingest a HiPS data directory

To validate and ingest a HiPS data directory, you can run the Django
management command `./manage.py ingest`. That invocation will show a usage
message; to validate/ingest a directory, supply a data directory as an argument.

### List existing HiPS data

Run the management command `./manage.py list` to see information about available
images along with their creation time, ROI count, and nucleus count.

### Delete HiPS data

Run the management command `./manage.py delete` to delete images (along with
their ROI and nucleus data). Supply at least one image ID (found by looking at
the list command output, above), or use the `--all` flag to delete all images.
Be careful!

## Run tests

To run the tests, simply run `pytest` at the top level of the repository.

## Run linting/formatting

To run the linter, use the `ruff check` (to display linting errors) and `ruff
check --fix` (to autofix them) commands.

To run the formatter, use the `ruff format --check` or `ruff format --diff` (to
indicate/display formatting issues) and `ruff format` (to autofix them)
commands.
