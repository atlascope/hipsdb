from typing import List, Optional
from django.forms import model_to_dict
from ninja import ModelSchema, NinjaAPI, Query, Schema
from ninja.pagination import paginate
from pydantic import ConfigDict, create_model

from hipsdb.models import ROI, Image, Nucleus


api = NinjaAPI(
    title="HiPS API",
    version="0.1.0",
    description="API for HiPS database",
)


class ErrorSchema(Schema):
    detail: str


class ImageSchema(ModelSchema):
    class Meta:
        model = Image
        fields = "__all__"


@api.get("/images", response=List[ImageSchema])
def get_images(request):
    images = Image.objects.all()
    return images


@api.get("/images/{image_id}", response={200: ImageSchema, 404: ErrorSchema})
def get_image(request, image_id: int):
    try:
        image = Image.objects.get(pk=image_id)
    except Image.DoesNotExist:
        return 404, {"detail": f"Image {image_id} not found"}

    return image


class ROISchema(ModelSchema):
    class Meta:
        model = ROI
        exclude = ["image"]


@api.get("/images/{image_id}/rois", response=List[ROISchema])
@paginate
def get_image_rois(request, image_id: int):
    try:
        image = Image.objects.get(pk=image_id)
    except Image.DoesNotExist:
        return 404, {"detail": f"Image {image_id} not found"}

    return image.rois.all()


class NucleusSchema(ModelSchema):
    class Meta:
        model = Nucleus
        exclude = ["id", "roi"]


def make_optional_schema(schema: ModelSchema):
    annotations = {field: (Optional[annotation], None) for field, annotation in schema.__annotations__.items()}
    OptionalSchema = create_model(
        f"Optional{schema.__name__}",
        __base__=schema,
        #__module__=__name__,
        **annotations,
    )

    return OptionalSchema

OptionalNucleusSchema = make_optional_schema(NucleusSchema)


@api.get("/images/{image_id}/rois/{roi_id}/nuclei", response={200: List[OptionalNucleusSchema], 404: ErrorSchema}, exclude_none=True)
@paginate
def get_roi_nuclei(request, image_id: int, roi_id: int, fields: Optional[List[str]] = Query(None)):
    try:
        image = Image.objects.get(pk=image_id)
    except Image.DoesNotExist:
        return 404, {"detail": f"Image {image_id} not found"}

    try:
        roi = image.rois.get(pk=roi_id)
    except ROI.DoesNotExist:
        return 404, {"detail": f"ROI {roi_id} not found"}

    if roi.image != image:
        return 404, {"detail": f"ROI {roi_id} does not belong to Image {image_id}"}

    nucleus_fields = NucleusSchema.model_fields.keys()
    if fields:
        selected = [f for f in fields if f in nucleus_fields]
    else:
        selected = nucleus_fields

    return roi.nuclei.values(*selected)
