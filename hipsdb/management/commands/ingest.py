import djclick as click
from pathlib import Path
import sys

from hips_etl.validation import validate_hips_dir


@click.command()
@click.argument(
    "data_dir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
)
@click.option(
    "--skip-missing",
    is_flag=True,
    default=False,
    help="Skip rows with missing data during validation.",
)
def ingest(data_dir, skip_missing):
    """
    Validate and ingest a HiPS data directory.

    :param data_dir: The path to the directory to validate/ingest.
    :param skip_missing: If set, skip rows with missing data during validation.
    """
    try:
        success = validate_hips_dir(data_dir, skip_missing=skip_missing)
        sys.exit(0 if success else 1)
    except Exception as e:
        raise click.ClickException(f"Unexpected error: {e}")
