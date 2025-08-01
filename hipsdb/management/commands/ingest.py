import djclick as click


@click.command()
@click.argument("foo")
def ingest(foo: str):
    """
    Ingest data into the database.

    :param foo: A string argument for demonstration purposes.
    """
    click.echo(f"Ingesting data with argument: {foo}")
