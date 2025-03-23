from pathlib import Path
import sys

from hips_etl import validate_hips_data_dir


def main():
    if len(sys.argv) != 2:
        print("Usage: python -m hips_etl <data_dir>", file=sys.stderr)
        return 1

    data_dir = Path(sys.argv[1])
    try:
        success = validate_hips_data_dir(data_dir)
        return 0 if success else 1
    except RuntimeError as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
