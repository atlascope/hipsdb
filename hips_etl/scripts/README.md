# hips_etl/scripts

Some useful scripts for generating and maintaining code in the `hips_etl`
package.

## `generate_nucleus_fields.py`

This script generates a JSON array of objects encoding the database fields
needed for each `Nucleus` object in the raw data files. The objects look like
this:

```json
{
    "db_name": <original CSV column name>,
    "django_name": <legal django field name>,
    "type": <type specifier>
}
```

The `db_name` is the original field name from the data files, which are
generally period-separated compound names describing a general kind of field
plus a specifier (e.g., `Cytoplasm.Intesity.Mean`).

Since these names are not legal field names for a Django model, they have been
converted to the `django_name` by replacing all periods with underscores. For
ease of use, the names are not further "Pythonized" (e.g. by converting to all
lowercase, etc.).

The `type` is either a string--`int` or `intfloat` for integer values, and
`float` for floating point values--or a list of strings representing a choice of
those strings.

The script is here as a paper trail explaining how the
`hips_etl/fields/nucleus_fields.json` was created. It is not meant for running
generally, although you can run it to compare its output to that file if you
like.

## `generate_nucleus_model.py`

This script reads in the output of `generate_nucleus_fields.py` and uses it to
generate code for a `Nucleus` Django model. The `django_name` serves as the
Python field name, while `db_name` is used to set the `db_column` property of
each field, and `type` is used to select the field type to use.

As with `generate_nucleus_fields.py`, this script is not meant for general
running, but rather to show how the model was created. To recreate the output
used in the codebase, run this script through `ruff format`.
