import csv
import importlib.resources
import json
from pathlib import Path
import re


csv_filename_pattern = re.compile(r'^(?P<case_name>.*)_roi-(?P<roi>[0-9]+)_left-(?P<left>[0-9]+)_top-(?P<top>[0-9]+)_right-(?P<right>[0-9]+)_bottom-(?P<bottom>[0-9]+)\.csv$')

with open(importlib.resources.files(__package__) / "fields" / "common.json") as f:
    common_fields = set(json.load(f))

with open(importlib.resources.files(__package__) / "fields" / "meta_only.json") as f:
    meta_only_fields = set(json.load(f))

with open(importlib.resources.files(__package__) / "fields" / "props_only.json") as f:
    props_only_fields = set(json.load(f))


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


# TODO: report which fields are missing instead of just returning False.
def fields_match(fields: set, expected_fields: set) -> bool:
    """Check if the fields in a CSV file match the expected fields."""
    return fields == expected_fields


def get_object_mapping(rows: list[dict]) -> dict[int, dict] | None:
    """Construct a mapping from ObjectCode to row for a list of dictionaries."""
    mapping = {int(float(row['Identifier.ObjectCode'])): row for row in rows}

    if len(mapping) != len(rows):
        return None
        # raise ValueError("Duplicate ObjectCodes found in the data.")

    return mapping


def validate_hips_data_dir(data_dir: Path):
    """Validate the data in a hips data directory."""

    # Check that the data directory exists and is a directory.
    if not dir_exists(data_dir):
        raise ValueError(f"No such directory {data_dir}.")

    # Check that the data directory contains `nucleiMeta` and `nucleiProps` subdirectories.
    meta_dir = data_dir / "nucleiMeta"
    if not dir_exists(meta_dir):
        raise ValueError(f"Directory {meta_dir} is missing.")

    props_dir = data_dir / "nucleiProps"
    if not dir_exists(props_dir):
        raise ValueError(f"Directory {props_dir} is missing.")

    # Make sure that each subdirectory contains the same set of files.
    filenames = check_same_filenames(meta_dir, props_dir)
    if filenames is None:
        raise ValueError(f"Files in {meta_dir} and {props_dir} do not match.")

    # Validate each file in the directories.
    for filename in filenames:
        print(f'Validating {filename}...')

        # Check that the filename matches the expected pattern.
        match = csv_filename_pattern.match(filename)
        if not match:
            raise ValueError(f"Filename {filename} does not match the pattern.")

        # Check that the case name matches the directory name.
        if match.group('case_name') != data_dir.name:
            raise ValueError(f"Case name for {filename} does not match directory name {data_dir.name}.")

        # Read the CSV files and check that the fields match the expected fields.
        meta_rows, meta_fields = read_csv(meta_dir / filename)
        if not fields_match(meta_fields, common_fields | meta_only_fields):
            raise ValueError(f"Meta fields for {filename} do not match expected fields.")

        props_rows, props_fields = read_csv(props_dir / filename)
        if not fields_match(props_fields, common_fields | props_only_fields):
            raise ValueError(f"Props fields for {filename} do not match expected fields.")

        # Construct a mapping from ObjectCode to row for both meta and props.
        meta_dict = get_object_mapping(meta_rows)
        if meta_dict is None:
            raise ValueError(f"Duplicate ObjectCodes found in meta data for {filename}.")

        props_dict = get_object_mapping(props_rows)
        if props_dict is None:
            raise ValueError(f"Duplicate ObjectCodes found in props data for {filename}.")

        # Check that the ObjectCodes in meta and props match.
        if set(meta_dict.keys()) != set(props_dict.keys()):
            raise ValueError(f"ObjectCodes in {filename} do not match between meta and props.")

        # Check the data integrity properties between meta and props.
        for id in meta_dict.keys():
            meta = meta_dict[id]
            props = props_dict[id]

            # Check that the [X|Y]min values match.
            if float(meta['Identifier.Xmin']) != float(props['Identifier.Xmin']):
                raise ValueError(f"Xmin values do not match for ObjectCode {id} in {filename}.")
            if float(meta['Identifier.Ymin']) != float(props['Identifier.Ymin']):
                raise ValueError(f"Ymin values do not match for ObjectCode {id} in {filename}.")

            # Check the the [X|Y]max values are off-by-one.
            if float(meta['Identifier.Xmax']) != float(props['Identifier.Xmax']) - 1:
                raise ValueError(f"Xmax values do not match for ObjectCode {id} in {filename}.")
            if float(meta['Identifier.Ymax']) != float(props['Identifier.Ymax']) - 1:
                raise ValueError(f"Ymax values do not match for ObjectCode {id} in {filename}.")
