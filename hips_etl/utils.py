import csv
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def dir_exists(directory: Path) -> bool:
    """Check if a directory exists and is a directory."""
    return directory.exists() and directory.is_dir()


def check_same_filenames(dir1: Path, dir2: Path):
    """
    Check if two directories contain the same set of filenames.
    Returns the set of filenames if they match, otherwise returns None.
    """
    files1 = set(dir1.iterdir())
    files2 = set(dir2.iterdir())
    if {x.name for x in files1} != {x.name for x in files2}:
        return None
    return {x.name for x in files1}


def read_csv(csv_file: Path) -> tuple[list[dict], list[str]]:
    """Read a CSV file and return its contents as a list of dictionaries."""
    with open(csv_file) as f:
        reader = csv.DictReader(f)
        fields = set(reader.fieldnames)
        return (list(reader), fields)


def fields_match(fields: set, expected_fields: set) -> bool:
    missing_fields = expected_fields - fields
    extra_fields = fields - expected_fields
    if missing_fields or extra_fields:
        logger.error(f"Fields mismatch: missing {missing_fields}, extra {extra_fields}")
        return False
    return True


def get_object_mapping(rows: list[dict]) -> dict[int, dict] | None:
    """Construct a mapping from ObjectCode to row for a list of dictionaries."""
    mapping = {int(float(row["Identifier.ObjectCode"])): row for row in rows}

    return mapping if len(mapping) == len(rows) else None
