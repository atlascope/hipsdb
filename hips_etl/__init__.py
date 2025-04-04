import importlib.resources
import json
import math
from pathlib import Path
import re
import sys

from hips_etl.utils import (
    dir_exists,
    check_same_filenames,
    read_csv,
    fields_match,
    get_object_mapping,
)
from hips_etl.utils.types import (
    type_convert_meta,
    type_convert_props,
)
from hips_etl.utils.logging import initialize_logging

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
