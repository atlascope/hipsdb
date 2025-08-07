from django.db.models import Count, OuterRef, Subquery
import djclick as click

from hipsdb.models import ROI, Image, Nucleus


@click.command()
def list():
    roi_count = ROI.objects.filter(image=OuterRef('pk')).values('image')\
        .annotate(count=Count('id'))\
        .values('count')
    nucleus_count = Nucleus.objects.filter(roi__image=OuterRef('pk'))\
        .values('roi__image')\
        .annotate(count=Count('id'))\
        .values('count')
    images = Image.objects.annotate(
        roi_count=Subquery(roi_count),
        nucleus_count=Subquery(nucleus_count)
    ).values('id', 'name', 'roi_count', 'nucleus_count')

    for image in images:
        click.echo(f"{image['name']} (ID {image['id']}, {image['roi_count']} ROIs, {image['nucleus_count']} nuclei)")
