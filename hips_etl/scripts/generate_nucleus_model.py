import sys

from generate_nucleus_fields import read_json


def choices(values: list[str]) -> list[tuple[str, str]]:
    return [(x, x) for x in values]


def main():
    fields = read_json('../fields/nucleus_fields.json')

    # Print a Django model using the nucleus fields.
    print('from django.db import models')
    print()
    print()
    print('class Nucleus(models.Model):')
    print("    roi: ROI = models.ForeignKey(ROI, on_delete=models.CASCADE, related_name='nuclei')")
    print()

    for f in fields:
        field_name = f['django_name']
        db_name = f['db_name']
        field_type = f['type']

        if field_type in ['int', 'intfloat']:
            print(f'    {field_name} = models.IntegerField(db_column="{db_name}")')
        elif field_type == 'float':
            print(f'    {field_name} = models.FloatField(db_column="{db_name}")')
        elif type(field_type) is list:
            print(f'    {field_name} = models.CharField(max_length={max(len(choice) for choice in field_type)}, choices={choices(field_type)}, db_column="{db_name}")')
        else:
            raise ValueError(f'Unknown field type for {f}: {field_type}')


if __name__ == '__main__':
    sys.exit(main())
