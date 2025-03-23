import csv
import importlib.resources
import json
import logging
import math
from pathlib import Path
import re
import sys
from typing import Literal

import blessings

def initialize_logging() -> tuple[logging.Logger, logging.Formatter]:
    term = blessings.Terminal()
    class HipsFormatter(logging.Formatter):
        Colors = {
            logging.DEBUG: term.green,
            logging.INFO: term.blue,
            logging.WARNING: term.yellow,
            logging.ERROR: term.red,
            logging.CRITICAL: term.bold_red,
        }

        def __init__(self, *args, **kwargs):
            self.spacing = 0
            self.supports_color = sys.stdout.isatty() and sys.stderr.isatty()
            super().__init__(*args, **kwargs)

        def format(self, record):
            record.levelname = record.levelname.ljust(len('CRITICAL'))
            record.msg = ' ' * self.spacing + record.msg
            color = self.__class__.Colors.get(record.levelno, term.normal)
            if self.supports_color:
                record.msg = color(record.msg)
            return super().format(record)

        def indent(self):
            self.spacing += 2

        def dedent(self):
            self.spacing -= 2
            if self.spacing < 0:
                self.spacing = 0

    logger = logging.getLogger(__name__)
    formatter = HipsFormatter('[%(name)s/%(levelname)s] %(message)s')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    return logger, formatter

logger, formatter = initialize_logging()

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


def convert_intfloat(value: str) -> int | None:
    """
    Convert a string to an integer, raising an exception for bad input.

    `value` is a string encoding an integer value as a floating point value.
    """
    try:
        floatval = float(value)
        intval = int(floatval)
        if floatval != intval:
            logger.warning(f"Value {value} is not a valid intfloat.")
            return None
        return intval
    except (ValueError, TypeError) as e:
        logger.warning(f"Invalid intfloat value: {value}")
        return None


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
        logger.warning(f"Invalid float value: {value}")
        return None


def convert_int(value: str) -> int | None:
    """Convert a string to an integer, raising an exception for bad input."""
    try:
        return int(value)
    except (ValueError, TypeError) as e:
        logger.warning(f"Invalid int value: {value}")
        return None


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
                        logger.warning(f"Invalid enum value '{value}' for field '{key}'.")
                        value = None
                case _:
                    raise RuntimeError(f"Unknown type '{conversion_type}' in {type} types.")
            row[key] = value

    for key in floatint:
        if False not in floatint[key]:
            logger.warning(f"Float field '{key}' contains only int values. (Should it be a floatint?)")

    return rows


def type_convert_meta(rows: list[dict]) -> list[dict]:
    """Convert the raw meta rows to a properly typed rows."""
    return type_convert_rows(rows, "meta")


def type_convert_props(rows: list[dict]) -> list[dict]:
    """Convert the raw props rows to a properly typed rows."""
    return type_convert_rows(rows, "props")


def validate_hips_data_dir(data_dir: Path) -> bool:
    """Validate the data in a hips data directory."""

    success = True

    # Check that the data directory exists and is a directory.
    if not dir_exists(data_dir):
        logger.critical(f"No such directory {data_dir}.")
        return False

    # Check that the data directory contains `nucleiMeta` and `nucleiProps` subdirectories.
    meta_dir = data_dir / "nucleiMeta"
    props_dir = data_dir / "nucleiProps"
    if not dir_exists(meta_dir) or not dir_exists(props_dir):
        logger.critical(f"Subdirectories {meta_dir} and {props_dir} must both exist.")
        return False

    # Make sure that each subdirectory contains the same set of files.
    filenames = check_same_filenames(meta_dir, props_dir)
    if filenames is None:
        logger.critical(f"Files in {meta_dir} and {props_dir} do not match.")
        return False

    # Validate each file in the directories.
    for filename in filenames:
        logger.info(f'Validating {filename}')
        formatter.indent()

        # Check that the filename matches the expected pattern.
        match = csv_filename_pattern.match(filename)
        if not match:
            logger.warning(f"Filename {filename} does not match the pattern.")
            success = False

        # Check that the case name matches the directory name.
        if match.group('case_name') != data_dir.name:
            logger.warning(f"Case name for {filename} does not match directory name {data_dir.name}.")
            success = False

        # Read the CSV files and check that the fields match the expected fields.
        meta_rows, meta_fields = read_csv(meta_dir / filename)
        if not fields_match(meta_fields, common_fields | meta_only_fields):
            logger.error(f"Meta fields for {filename} do not match expected fields.")
            return False

        props_rows, props_fields = read_csv(props_dir / filename)
        if not fields_match(props_fields, common_fields | props_only_fields):
            logger.error(f"Props fields for {filename} do not match expected fields.")
            return False

        meta_rows = type_convert_meta(meta_rows)
        props_rows = type_convert_props(props_rows)

        # Construct a mapping from ObjectCode to row for both meta and props.
        meta_dict = get_object_mapping(meta_rows)
        if meta_dict is None:
            logger.error(f"Duplicate ObjectCodes found in meta data for {filename}.")
            return False

        props_dict = get_object_mapping(props_rows)
        if props_dict is None:
            logger.error(f"Duplicate ObjectCodes found in props data for {filename}.")
            return False

        # Check that the ObjectCodes in meta and props match.
        if set(meta_dict.keys()) != set(props_dict.keys()):
            logger.error(f"ObjectCodes in {filename} do not match between meta and props.")
            return False

        # Check the data integrity properties between meta and props.
        for id in meta_dict.keys():
            meta = meta_dict[id]
            props = props_dict[id]

            # Ensure no missing values in meta and props.
            for key in meta:
                if meta[key] is None:
                    logger.error(f"meta[{id}][{key}] is missing.")
                    success = False

            for key in props:
                if props[key] is None:
                    logger.error(f"props[{id}][{key}] is missing.")
                    success = False

            # Check that the [X|Y]min values match.
            if meta['Identifier.Xmin'] != props['Identifier.Xmin']:
                logger.warning(f"Xmin values do not match for ObjectCode {id} in {filename}.")
                success = False
            if meta['Identifier.Ymin'] != props['Identifier.Ymin']:
                logger.warning(f"Ymin values do not match for ObjectCode {id} in {filename}.")
                success = False

            # Check the the [X|Y]max values are off-by-one.
            if meta['Identifier.Xmax'] != props['Identifier.Xmax'] - 1:
                logger.warning(f"Xmax values do not match for ObjectCode {id} in {filename}.")
                success = False
            if meta['Identifier.Ymax'] != props['Identifier.Ymax'] - 1:
                logger.warning(f"Ymax values do not match for ObjectCode {id} in {filename}.")
                success = False

            # Check for properly rounded centroid values.
            if meta['Identifier.CentroidX'] != math.floor(props['Identifier.CentroidX']):
                logger.warning(f"Identifier.CentroidX values do not match for ObjectCode {id}.")
                success = False

            if meta['Identifier.CentroidY'] != math.floor(props['Identifier.CentroidY']):
                logger.warning(f"Identifier.CentroidY values do not match for ObjectCode {id}.")
                success = False

        formatter.dedent()

    if success:
        logger.info("Data directory is valid.")
    else:
        logger.error("Data directory is invalid.")
    return success
