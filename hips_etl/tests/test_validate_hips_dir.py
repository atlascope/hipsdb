import importlib
import math

from hypothesis import given, strategies as st
import hips_etl

test_data_dir = importlib.resources.files("hips_etl") / "test_data"


def test_missing_hips_dir(caplog):
    success = hips_etl.validate_hips_dir(test_data_dir / "nonexisting")
    assert not success
    assert "No such directory" in caplog.text


def test_good_hips_dir(caplog):
    success = hips_etl.validate_hips_dir(test_data_dir / "good")
    assert success
    assert "Data directory is valid" in caplog.text


def test_missing_meta_dir(caplog):
    success = hips_etl.validate_hips_dir(test_data_dir / "missing_meta")
    assert not success
    assert "Subdirectories nucleiMeta and nucleiProps must both exist" in caplog.text


def test_nonmatching_files(caplog):
    success = hips_etl.validate_hips_dir(test_data_dir / "nonmatching_files")
    assert not success
    assert "Files in nucleiMeta and nucleiProps do not match" in caplog.text


def test_file_regex_mismatch(caplog):
    success = hips_etl.validate_hips_dir(test_data_dir / "regex_mismatch")
    assert not success
    assert "Filename regex_mismatch.csv does not match the pattern" in caplog.text


def test_mismatched_name(caplog):
    success = hips_etl.validate_hips_dir(test_data_dir / "mismatched_name")
    assert not success
    assert (
        "Image name for wrong_name_roi-5_left-18001_top-45779_right-20049_bottom-47827.csv does not match directory name mismatched_name"
        in caplog.text
    )


def test_missing_fields(caplog):
    success = hips_etl.validate_hips_dir(test_data_dir / "missing_meta_fields")
    assert not success
    filename = (
        "missing_meta_fields_roi-5_left-18001_top-45779_right-20049_bottom-47827.csv"
    )
    assert f"Meta fields for {filename} do not match expected fields" in caplog.text

    success = hips_etl.validate_hips_dir(test_data_dir / "missing_props_fields")
    assert not success
    filename = (
        "missing_props_fields_roi-5_left-18001_top-45779_right-20049_bottom-47827.csv"
    )
    assert f"Props fields for {filename} do not match expected fields" in caplog.text


def test_get_object_mapping():
    good_data = [
        {
            "Identifier.ObjectCode": 0,
            "name": "zero",
        },
        {
            "Identifier.ObjectCode": 1,
            "name": "one",
        },
        {
            "Identifier.ObjectCode": 2,
            "name": "two",
        },
    ]
    good_mapping = hips_etl.get_object_mapping(good_data)
    assert good_mapping == {i: good_data[i] for i in range(len(good_data))}

    bad_data = [
        {
            "Identifier.ObjectCode": 0,
            "name": "zero",
        },
        {
            "Identifier.ObjectCode": 0,
            "name": "one",
        },
        {
            "Identifier.ObjectCode": 2,
            "name": "two",
        },
        {
            "Identifier.ObjectCode": 3,
            "name": "three",
        },
    ]
    bad_mapping = hips_etl.get_object_mapping(bad_data)
    assert bad_mapping is None


def test_duplicate_meta_objectcodes(caplog):
    success = hips_etl.validate_hips_dir(test_data_dir / "duplicate_objectcodes_meta")
    assert not success
    filename = "duplicate_objectcodes_meta_roi-5_left-18001_top-45779_right-20049_bottom-47827.csv"
    assert f"Duplicate ObjectCodes found in meta data for {filename}" in caplog.text


def test_duplicate_props_objectcodes(caplog):
    success = hips_etl.validate_hips_dir(test_data_dir / "duplicate_objectcodes_props")
    assert not success
    filename = "duplicate_objectcodes_props_roi-5_left-18001_top-45779_right-20049_bottom-47827.csv"
    assert f"Duplicate ObjectCodes found in props data for {filename}" in caplog.text


def test_mismatched_objectcodes(caplog):
    success = hips_etl.validate_hips_dir(test_data_dir / "mismatched_objectcodes")
    assert not success
    filename = (
        "mismatched_objectcodes_roi-5_left-18001_top-45779_right-20049_bottom-47827.csv"
    )
    assert (
        f"ObjectCodes in {filename} do not match between meta and props" in caplog.text
    )


def test_broken_checks(caplog):
    success = hips_etl.validate_hips_dir(test_data_dir / "broken_checks")
    assert not success

    assert (
        "meta[1][Unconstrained.SuperClassifProbab.StromalSuperclass] is missing"
        in caplog.text
    )
    assert "props[1][Nucleus.Haralick.IMC1.Range] is missing" in caplog.text
    assert "meta[1][Xmin] and props[1][Xmin] do not match" in caplog.text
    assert "meta[1][Ymin] and props[1][Ymin] do not match" in caplog.text
    assert "meta[1][Xmax] and props[1][Xmax] are not off by one" in caplog.text
    assert "meta[1][Ymax] and props[1][Ymax] are not off by one" in caplog.text
    assert (
        "meta[2][Identifier.CentroidX] is not the floor of props[2][Identifier.CentroidX]"
        in caplog.text
    )
    assert (
        "meta[2][Identifier.CentroidY] is not the floor of props[2][Identifier.CentroidY]"
        in caplog.text
    )


def test_missing_data(caplog):
    success = hips_etl.validate_hips_dir(test_data_dir / "missing_data")
    assert not success

    assert "meta[4][ClassifProbab.NormalEpithelium] is missing" in caplog.text
    assert "props[1][Nucleus.Haralick.IMC1.Range] is missing" in caplog.text


def test_skip_missing(caplog):
    success = hips_etl.validate_hips_dir(
        test_data_dir / "missing_data", skip_missing=True
    )
    assert success

    assert (
        "meta[4][ClassifProbab.NormalEpithelium] is missing (skipping this record)"
        in caplog.text
    )
    assert (
        "props[1][Nucleus.Haralick.IMC1.Range] is missing (skipping this record)"
        in caplog.text
    )


@given(st.integers())
def test_convert_int_good_inputs(n: int):
    assert hips_etl.convert_int(str(n)) == n


@given(st.text().filter(lambda s: not s.lstrip("-").isnumeric()))
def test_convert_int_bad_inputs(s: str):
    assert hips_etl.convert_int(s) is None


@given(st.floats())
def test_convert_float_good_inputs(x: float):
    converted = hips_etl.convert_float(str(x), [])
    if math.isnan(x):
        assert math.isnan(converted)
    else:
        assert converted == x


@given(
    st.text().filter(
        lambda s: not s.lstrip("-").lstrip("+").replace(".", "").isnumeric()
        and s.lower() not in ["inf", "-inf", "nan", "infinity", "-infinity"]
    )
)
def test_convert_float_bad_inputs(s: str):
    assert hips_etl.convert_float(s, []) is None


@given(st.floats(allow_infinity=False, allow_nan=False).map(math.floor))
def test_convert_intfloat_good_inputs(x: float):
    assert hips_etl.convert_intfloat(str(x)) == x


@given(st.floats().filter(lambda x: not x.is_integer()))
def test_convert_intfloat_bad_inputs(x: float):
    assert hips_etl.convert_intfloat(str(x)) is None
