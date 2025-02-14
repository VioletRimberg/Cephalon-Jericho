from src.warframe import WarframeAPI


def test_is_constructable():
    api = WarframeAPI()
    assert api is not None
