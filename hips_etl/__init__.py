import csv
import importlib.resources
import json
from pathlib import Path
import re


csv_filename_pattern = re.compile(r'^(?P<case_name>.*)_roi-(?P<roi>[0-9]+)_left-(?P<left>[0-9]+)_top-(?P<top>[0-9]+)_right-(?P<right>[0-9]+)_bottom-(?P<bottom>[0-9]+)\.csv$')


def dir_exists(directory: Path) -> bool:
    """Check if a directory exists and is a directory."""
    return directory.exists() and directory.is_dir()


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
    meta_files = set(meta_dir.iterdir())
    props_files = set(props_dir.iterdir())
    if {x.name for x in meta_files} != {x.name for x in props_files}:
        raise ValueError(f"Files in {meta_dir} and {props_dir} do not match.")

    with open(importlib.resources.files(__package__) / "fields" / "common.json") as f:
        common_fields = set(json.load(f))

    with open(importlib.resources.files(__package__) / "fields" / "meta_only.json") as f:
        meta_only_fields = set(json.load(f))

    with open(importlib.resources.files(__package__) / "fields" / "props_only.json") as f:
        props_only_fields = set(json.load(f))

    # Capture one set of just the common file basenames.
    filenames = {x.name for x in meta_files}

    # Check that each filename matches the correct pattern.
    for filename in filenames:
        print(f'Validating {filename}...')

        match = csv_filename_pattern.match(filename)
        if not match:
            raise ValueError(f"Filename {filename} does not match the pattern.")

        # Check that the case name matches the directory name.
        if match.group('case_name') != data_dir.name:
            raise ValueError(f"Case name for {filename} does not match directory name {data_dir.name}.")

        with open(meta_dir / filename) as f:
            reader = csv.DictReader(f)
            meta_fields = set(reader.fieldnames)
            meta_rows = list(reader)

        if not all(k in meta_fields for k in common_fields):
            raise ValueError(f"Meta fields missing some common keys.")

        if not all(k in meta_fields for k in meta_only_fields):
            raise ValueError(f"Meta fields missing some meta-only keys.")

        if len(meta_fields) > len(common_fields) + len(meta_only_fields):
            raise ValueError(f"Unexpected meta fields.")

        with open(props_dir / filename) as f:
            reader = csv.DictReader(f)
            props_fields = set(reader.fieldnames)
            props_rows = list(reader)

        if not all(k in props_fields for k in common_fields):
            raise ValueError(f"Props fields missing some common keys.")

        if not all(k in props_fields for k in props_only_fields):
            raise ValueError(f"Props fields missing some props-only keys.")

        if len(props_fields) > len(common_fields) + len(props_only_fields):
            raise ValueError(f"Unexpected props fields.")

        # Check that meta and props contain the same number of rows and matching row IDs.
        if len(meta_rows) != len(props_rows):
            raise ValueError(f"Meta and props files have different number of rows for {filename}.")

        if set(int(float(row['Identifier.ObjectCode'])) for row in meta_rows) != set(int(float(row['Identifier.ObjectCode'])) for row in props_rows):
            raise ValueError(f"Meta and props files have different ObjectCodes for {filename}.")

        # Construct a mapping from id to row for both meta and props.
        meta_dict = {int(float(row['Identifier.ObjectCode'])): row for row in meta_rows}
        props_dict = {int(float(row['Identifier.ObjectCode'])): row for row in props_rows}

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
