from pathlib import Path
import sys
import click

from hips_etl import validate_hips_dir


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
def main(data_dir, skip_missing):
    """
    Validate a HiPS data directory.

    DATA_DIR is the path to the directory to validate.
    """
    try:
        success = validate_hips_dir(data_dir, skip_missing=skip_missing)
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
