import csv
import importlib.resources
import json
from pathlib import Path
import re

from typing import Literal


csv_filename_pattern = re.compile(r'^(?P<case_name>.*)_roi-(?P<roi>[0-9]+)_left-(?P<left>[0-9]+)_top-(?P<top>[0-9]+)_right-(?P<right>[0-9]+)_bottom-(?P<bottom>[0-9]+)\.csv$')

with open(importlib.resources.files(__package__) / "fields" / "common.json") as f:
    common_fields = set(json.load(f))

with open(importlib.resources.files(__package__) / "fields" / "meta_only.json") as f:
    meta_only_fields = set(json.load(f))

with open(importlib.resources.files(__package__) / "fields" / "props_only.json") as f:
    props_only_fields = set(json.load(f))

with open(importlib.resources.files(__package__) / "fields" / "types.json") as f:
    types = json.load(f)


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

    return mapping if len(mapping) == len(rows) else None


def convert_intfloat(value: str) -> int:
    """
    Convert a string to an integer, raising an exception for bad input.

    `value` is a string encoding an integer value as a floating point value.
    """
    try:
        floatval = float(value)
        intval = int(floatval)
        if floatval != intval:
            print(f"Value {value} is not a valid intfloat.")
        return intval
    except (ValueError, TypeError) as e:
        print(f"Invalid intfloat value: {value}")


def convert_float(value: str, ints: list[bool]) -> float | None:
    """
    Convert a string to a float, raising an exception for bad input.

    This function also tracks whether the float value is an integer over
    multiple invocations with the intent of determining whether the field
    should be considered an intfloat instead.
    """
    try:
        # TODO: handle missing values in a better way.
        if value == "":
            return None
        floatval = float(value)
        ints.append(floatval == int(floatval))
        return floatval
    except (ValueError, TypeError) as e:
        print(f"Invalid float value: {value}")


def convert_int(value: str) -> int:
    """Convert a string to an integer, raising an exception for bad input."""
    try:
        return int(value)
    except (ValueError, TypeError) as e:
        print(f"Invalid int value: {value}")


def type_convert_rows(rows: list[dict], type: Literal["meta", "props"]) -> list[dict]:
    """Convert the raw rows to a properly typed rows."""
    typemap = types[type]
    floatint = {}
    for row in rows:
        for key in row:
            value = row[key]
            conversion_type = typemap.get(key)
            match conversion_type:
                case "int":
                    value = convert_int(value)
                case "intfloat":
                    value = convert_intfloat(value)
                case "float":
                    floatints = floatint.setdefault(key, [])
                    value = convert_float(value, floatints)
                case "string":
                    # String data needs no conversion.
                    pass
                case "enum":
                    enum_values = types["enum_values"][type].get(key)
                    if enum_values is None:
                        raise RuntimeError(f"Field '{key}' is not registered as an enum type.")

                    if value not in enum_values:
                        print(f"Invalid enum value '{value}' for field '{key}'.")
                case _:
                    raise RuntimeError(f"Unknown type '{conversion_type}' in {type} types.")
            row[key] = value

    for key in floatint:
        if False not in floatint[key]:
            print(f"Float field '{key}' contains only int values. (Should it be a floatint?)")

    return rows


def type_convert_meta(rows: list[dict]) -> list[dict]:
    """Convert the raw meta rows to a properly typed rows."""
    return type_convert_rows(rows, "meta")


def type_convert_props(rows: list[dict]) -> list[dict]:
    """Convert the raw props rows to a properly typed rows."""
    return type_convert_rows(rows, "props")


def validate_hips_data_dir(data_dir: Path) -> bool:
    """Validate the data in a hips data directory."""

    # Check that the data directory exists and is a directory.
    if not dir_exists(data_dir):
        print(f"No such directory {data_dir}.")
        return False

    # Check that the data directory contains `nucleiMeta` and `nucleiProps` subdirectories.
    meta_dir = data_dir / "nucleiMeta"
    props_dir = data_dir / "nucleiProps"
    if not dir_exists(meta_dir) or not dir_exists(props_dir):
        print(f"Subdirectories {meta_dir} and {props_dir} must both exist.")
        return False

    # Make sure that each subdirectory contains the same set of files.
    filenames = check_same_filenames(meta_dir, props_dir)
    if filenames is None:
        print(f"Files in {meta_dir} and {props_dir} do not match.")
        return False

    # Validate each file in the directories.
    for filename in filenames:
        print(f'Validating {filename}...')

        # Check that the filename matches the expected pattern.
        match = csv_filename_pattern.match(filename)
        if not match:
            print(f"Filename {filename} does not match the pattern.")

        # Check that the case name matches the directory name.
        if match.group('case_name') != data_dir.name:
            print(f"Case name for {filename} does not match directory name {data_dir.name}.")

        # Read the CSV files and check that the fields match the expected fields.
        meta_rows, meta_fields = read_csv(meta_dir / filename)
        if not fields_match(meta_fields, common_fields | meta_only_fields):
            print(f"Meta fields for {filename} do not match expected fields.")
            return False

        props_rows, props_fields = read_csv(props_dir / filename)
        if not fields_match(props_fields, common_fields | props_only_fields):
            print(f"Props fields for {filename} do not match expected fields.")
            return False

        meta_rows = type_convert_meta(meta_rows)
        props_rows = type_convert_props(props_rows)

        # Construct a mapping from ObjectCode to row for both meta and props.
        meta_dict = get_object_mapping(meta_rows)
        if meta_dict is None:
            print(f"Duplicate ObjectCodes found in meta data for {filename}.")
            return False

        props_dict = get_object_mapping(props_rows)
        if props_dict is None:
            print(f"Duplicate ObjectCodes found in props data for {filename}.")
            return False

        # Check that the ObjectCodes in meta and props match.
        if set(meta_dict.keys()) != set(props_dict.keys()):
            print(f"ObjectCodes in {filename} do not match between meta and props.")
            return False

        # Check the data integrity properties between meta and props.
        for id in meta_dict.keys():
            meta = meta_dict[id]
            props = props_dict[id]

            # Check that the [X|Y]min values match.
            if meta['Identifier.Xmin'] != props['Identifier.Xmin']:
                print(f"Xmin values do not match for ObjectCode {id} in {filename}.")
            if meta['Identifier.Ymin'] != props['Identifier.Ymin']:
                print(f"Ymin values do not match for ObjectCode {id} in {filename}.")

            # Check the the [X|Y]max values are off-by-one.
            if meta['Identifier.Xmax'] != props['Identifier.Xmax'] - 1:
                print(f"Xmax values do not match for ObjectCode {id} in {filename}.")
            if meta['Identifier.Ymax'] != props['Identifier.Ymax'] - 1:
                print(f"Ymax values do not match for ObjectCode {id} in {filename}.")

    print("Data directory is valid.")
    return True
