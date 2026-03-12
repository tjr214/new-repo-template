from python_app import __doc__


def test_python_lane_import_smoke() -> None:
    assert __doc__ is not None
