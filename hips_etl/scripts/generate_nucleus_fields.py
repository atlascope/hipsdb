import json
import sys

def django_field_name(field_name: str) -> str:
    """Convert a field name to a Django model field name."""
    return field_name.replace('.', '_')

def read_json(file_path: str):
    """Read a JSON file and return its content."""
    with open(file_path) as f:
        return json.load(f)


def main():
    common = read_json('../fields/common.json')
    meta = read_json('../fields/meta_only.json')
    props = read_json('../fields/props_only.json')
    types = read_json('../fields/types.json')

    excluded = [
        '',
        'slide',
        'roiname',
    ]

    fields = []
    for f in common:
        if f not in excluded:
            fields.append({
                'db_name': f,
                'django_name': django_field_name(f),
                'type': types['meta'].get(f, types['props'].get(f)),
            })
    for f in meta:
        if f not in excluded:
            fields.append({
                'db_name': f,
                'django_name': django_field_name(f),
                'type': types['enum_values']['meta'].get(f, types['meta'].get(f)),
            })
    for f in props:
        if f not in excluded:
            fields.append({
                'db_name': f,
                'django_name': django_field_name(f),
                'type': types['props'].get(f),
            })

    print(json.dumps(fields, indent=2))


if __name__ == '__main__':
    sys.exit(main())
