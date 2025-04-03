# hips
A Django app for storing and serving HiPS data

## Setup

1. **Install project dependencies.** If you are using Nix, run `nix develop` to
   install dependencies; otherwise, ensure that you have Python 3.10 installed.
2. **Create a virtual environment.** Run `python -m venv ./.venv` followed by `.
   ./.venv/bin/activate`.
3. **Install Python dependencies.** Run `pip install -r requirements.txt`.

## Validate a HiPS data directory

To validate a HiPS data directory, you can run the validator as a Python script
with `python -m hips_etl`. That invocation will show a usage message; to
validate a directory, supply a data directory as an argument.

## Run tests

To run the tests, simply run `pytest` at the top level of the repository.
