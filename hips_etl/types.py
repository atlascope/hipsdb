import importlib.resources
import json
import math
from typing import Literal

from .logging import logger

with open(importlib.resources.files(__package__) / "fields" / "types.json") as f:
    types = json.load(f)


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
