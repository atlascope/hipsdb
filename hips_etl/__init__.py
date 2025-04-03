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
            record.levelname = record.levelname.ljust(len("CRITICAL"))
            record.msg = " " * self.spacing + record.msg
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
    formatter = HipsFormatter("[%(name)s/%(levelname)s] %(message)s")
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    return logger, formatter


logger, formatter = initialize_logging()

csv_filename_pattern = re.compile(
    r"^(?P<image>.*)_roi-(?P<roi>[0-9]+)_left-(?P<left>[0-9]+)_top-(?P<top>[0-9]+)_right-(?P<right>[0-9]+)_bottom-(?P<bottom>[0-9]+)\.csv$"
)


def get_json_fields(jsonfile: str) -> set[str]:
    try:
        with open(importlib.resources.files(__package__) / "fields" / jsonfile) as f:
            fields = set(json.load(f))
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.critical(f"Failed to load {jsonfile}: {e}")
        sys.exit(1)

    return fields


common_fields = get_json_fields("common.json")
meta_only_fields = get_json_fields("meta_only.json")
props_only_fields = get_json_fields("props_only.json")

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


def convert_intfloat(value: str) -> int | None:
    """
    Convert a string to an integer, raising an exception for bad input.

    `value` is a string encoding an integer value as a floating point value.
    """
    try:
        floatval = float(value)

        if (
            math.isinf(floatval)
            or math.isnan(floatval)
            or (intval := int(floatval)) != floatval
        ):
            logger.warning(f"Value {value} is not a valid intfloat")
            return None

        return intval
    except (ValueError, TypeError):
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
        if not math.isinf(floatval) and not math.isnan(floatval):
            ints.append(floatval == int(floatval))
        return floatval
    except (ValueError, TypeError):
        logger.warning(f"Invalid float value: {value}")
        return None


def convert_int(value: str) -> int | None:
    """Convert a string to an integer, raising an exception for bad input."""
    try:
        return int(value)
    except (ValueError, TypeError):
        logger.warning(f"Invalid int value: {value}")
        return None


def type_convert_rows(
    rows: list[dict], type: Literal["meta", "props"]
) -> list[dict] | None:
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
                        logger.critical(
                            f"Field '{key}' is not registered as an enum type."
                        )
                        return None

                    if value not in enum_values:
                        logger.warning(
                            f"Invalid enum value '{value}' for field '{key}'"
                        )
                        value = None
                case _:
                    logger.critical(
                        f"Unknown type '{conversion_type}' in {type} types."
                    )
                    return None

            row[key] = value

    for key in floatint:
        if False not in floatint[key]:
            logger.warning(
                f"Float field '{key}' contains only int values (should it be a floatint?)"
            )

    return rows


def type_convert_meta(rows: list[dict]) -> list[dict]:
    """Convert the raw meta rows to a properly typed rows."""
    return type_convert_rows(rows, "meta")


def type_convert_props(rows: list[dict]) -> list[dict]:
    """Convert the raw props rows to a properly typed rows."""
    return type_convert_rows(rows, "props")


def validate_hips_dir(data_dir: Path, skip_missing: bool = False) -> bool:
    """Validate the data in a hips data directory."""

    success = True

    # Check that the data directory exists and is a directory.
    if not dir_exists(data_dir):
        logger.error(f"No such directory {data_dir}")
        return False

    # Check that the data directory contains `nucleiMeta` and `nucleiProps` subdirectories.
    meta_dir = data_dir / "nucleiMeta"
    props_dir = data_dir / "nucleiProps"
    if not dir_exists(meta_dir) or not dir_exists(props_dir):
        logger.error("Subdirectories nucleiMeta and nucleiProps must both exist")
        return False

    # Make sure that each subdirectory contains the same set of files.
    filenames = check_same_filenames(meta_dir, props_dir)
    if filenames is None:
        logger.error("Files in nucleiMeta and nucleiProps do not match")
        return False

    # Validate each file in the directories.
    for filename in filenames:
        logger.info(f"Validating {filename}")
        formatter.indent()

        # Check that the filename matches the expected pattern.
        match = csv_filename_pattern.match(filename)
        if not match:
            logger.warning(f"Filename {filename} does not match the pattern")
            success = False
            continue

        # Check that the case name matches the directory name.
        if match.group("image") != data_dir.name:
            logger.warning(
                f"Image name for {filename} does not match directory name {data_dir.name}"
            )
            success = False

        # Read the CSV files and check that the fields match the expected fields.
        meta_rows, meta_fields = read_csv(meta_dir / filename)
        if not fields_match(meta_fields, common_fields | meta_only_fields):
            logger.error(f"Meta fields for {filename} do not match expected fields")
            return False

        props_rows, props_fields = read_csv(props_dir / filename)
        if not fields_match(props_fields, common_fields | props_only_fields):
            logger.error(f"Props fields for {filename} do not match expected fields")
            return False

        meta_rows = type_convert_meta(meta_rows)
        props_rows = type_convert_props(props_rows)

        if meta_rows is None or props_rows is None:
            return False

        # Construct a mapping from ObjectCode to row for both meta and props.
        meta_dict = get_object_mapping(meta_rows)
        if meta_dict is None:
            logger.error(f"Duplicate ObjectCodes found in meta data for {filename}")
            return False

        props_dict = get_object_mapping(props_rows)
        if props_dict is None:
            logger.error(f"Duplicate ObjectCodes found in props data for {filename}")
            return False

        # Check that the ObjectCodes in meta and props match.
        if set(meta_dict.keys()) != set(props_dict.keys()):
            logger.error(
                f"ObjectCodes in {filename} do not match between meta and props"
            )
            return False

        # Check the data integrity properties between meta and props.
        for id in meta_dict.keys():
            meta = meta_dict[id]
            props = props_dict[id]

            # Ensure no missing values in meta and props.
            for key in meta:
                if meta[key] is None:
                    if not skip_missing:
                        logger.error(f"meta[{id}][{key}] is missing")
                        success = False
                    else:
                        logger.warning(
                            f"meta[{id}][{key}] is missing (skipping this record)"
                        )

            for key in props:
                if props[key] is None:
                    if not skip_missing:
                        logger.error(f"props[{id}][{key}] is missing")
                        success = False
                    else:
                        logger.warning(
                            f"props[{id}][{key}] is missing (skipping this record)"
                        )

            # Check that the [X|Y]min values match.
            if meta["Identifier.Xmin"] != props["Identifier.Xmin"]:
                logger.warning(f"meta[{id}][Xmin] and props[{id}][Xmin] do not match")
                success = False
            if meta["Identifier.Ymin"] != props["Identifier.Ymin"]:
                logger.warning(f"meta[{id}][Ymin] and props[{id}][Ymin] do not match")
                success = False

            # Check that the [X|Y]max values are off-by-one.
            if meta["Identifier.Xmax"] != props["Identifier.Xmax"] - 1:
                logger.warning(
                    f"meta[{id}][Xmax] and props[{id}][Xmax] are not off by one"
                )
                success = False
            if meta["Identifier.Ymax"] != props["Identifier.Ymax"] - 1:
                logger.warning(
                    f"meta[{id}][Ymax] and props[{id}][Ymax] are not off by one"
                )
                success = False

            # Check for properly rounded centroid values.
            if meta["Identifier.CentroidX"] != math.floor(
                props["Identifier.CentroidX"]
            ):
                logger.warning(
                    f"meta[{id}][Identifier.CentroidX] is not the floor of props[{id}][Identifier.CentroidX]"
                )
                success = False

            if meta["Identifier.CentroidY"] != math.floor(
                props["Identifier.CentroidY"]
            ):
                logger.warning(
                    f"meta[{id}][Identifier.CentroidY] is not the floor of props[{id}][Identifier.CentroidY]"
                )
                success = False

        formatter.dedent()

    if success:
        logger.info("Data directory is valid")
    else:
        logger.error("Data directory is invalid")
    return success
