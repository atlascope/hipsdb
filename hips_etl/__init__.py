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

    # Capture one set of just the common file basenames.
    filenames = {x.name for x in meta_files}

    # Check that each filename matches the correct pattern.
    for filename in filenames:
        match = csv_filename_pattern.match(filename)
        if not match:
            raise ValueError(f"Filename {filename} does not match the pattern.")

        # Check that the case name matches the directory name.
        if match.group('case_name') != data_dir.name:
            raise ValueError(f"Case name for {filename} does not match directory name {data_dir.name}.")
