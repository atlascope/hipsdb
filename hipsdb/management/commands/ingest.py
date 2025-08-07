from django.db import transaction
import djclick as click
from pathlib import Path
import sys

from hipsdb.models import ROI, Nucleus, Image
from hips_etl.validation import validate_hips_dir


@click.command()
@click.argument(
    "data_dir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
)
@click.option(
    "--skip-missing",
    is_flag=True,
    default=False,
    help="Skip rows with missing data during validation.",
)
def ingest(data_dir, skip_missing):
    """
    Validate and ingest a HiPS data directory.

    :param data_dir: The path to the directory to validate/ingest.
    :param skip_missing: If set, skip rows with missing data during validation.
    """
    try:
        data = validate_hips_dir(data_dir, skip_missing=skip_missing)

        if data is not None:
            click.echo('Loading data into the database...')
            with transaction.atomic():
                image = Image.objects.create(name=data['image'])
                click.echo(f'Created Image: {image.name}')
                rois = []
                nuclei = []
                for roi_data in data['roi']:
                    click.echo(f'Processing ROI {roi_data["name"]} ({len(roi_data["nuclei"])} nuclei)...')

                    roi = ROI(
                        image=image,
                        name=roi_data['name'],
                        left=roi_data['left'],
                        top=roi_data['top'],
                        right=roi_data['right'],
                        bottom=roi_data['bottom'],
                    )
                    rois.append(roi)

                    for nucleus_data in roi_data['nuclei']:
                        nuclei.append(Nucleus(
                            roi=roi,
                            **nucleus_data,
                        ))

                        if nucleus_data['Identifier_WeightedCentroidX'] is None:
                            click.echo(f'Warning: Nucleus {nucleus_data["Identifier_ObjectCode"]} has missing centroid data, aborting.')
                            click.echo(roi_data['name'])
                            click.echo(nucleus_data['Identifier_ObjectCode'])
                            sys.exit(1)

                click.echo(f'Creating {len(rois)} ROIs and {len(nuclei)} nuclei...')
                ROI.objects.bulk_create(rois)
                Nucleus.objects.bulk_create(nuclei)

        sys.exit(0 if data else 1)
    except Exception as e:
        raise click.ClickException(f"Unexpected error: {e}")
