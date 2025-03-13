from pathlib import Path
import sys

from hips_etl import validate_hips_data_dir


def main():
    if len(sys.argv) != 2:
        print("Usage: python -m hips_etl <data_dir>", file=sys.stderr)
        sys.exit(1)

    data_dir = Path(sys.argv[1])
    try:
        validate_hips_data_dir(data_dir)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
    else:
        print("Data directory is valid.")


if __name__ == "__main__":
    main()
