import sys
import djclick as click

from hipsdb.models import Image


@click.command()
@click.argument("image_id", type=int, nargs=-1)
@click.option(
    "--all",
    is_flag=True,
    default=False,
    help="Delete all images and their associated ROIs and nuclei.",
)
def delete(image_id: tuple[int, ...], all: bool):
    """Delete images and their associated ROIs and nuclei.

    Supply one or more IMAGE_IDs to delete specific images, or use --all
    to delete all images.
    """
    if not image_id and not all:
        click.echo("Please provide at least one image ID or use --all to delete all images.")
        sys.exit(1)

    if all:
        images = Image.objects.all()
    else:
        images = Image.objects.filter(id__in=image_id)

    if not images.exists():
        if all:
            click.echo("No images found to delete.")
        else:
            click.echo(f"No images found with IDs: {', '.join(map(str, image_id))}")
        sys.exit(1)

    click.echo("Found images to delete:")
    for image in images:
        click.echo(f"    {image.name} (ID {image.id})")

    if click.confirm("Are you sure you want to delete these images and all associated data?"):
        images.delete()
        click.echo("Images deleted successfully.")
    else:
        click.echo("Deletion cancelled.")
    sys.exit(0)
