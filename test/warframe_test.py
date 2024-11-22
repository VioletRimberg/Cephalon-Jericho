import pytest
from src.warframe import WarframeAPI

def test_is_constructable():
    api = WarframeAPI()
    assert api is not None

@pytest.mark.asyncio
async def test_can_get_profile():
    api = WarframeAPI()
    warframe_profile = await api.get_profile("llukas22")
    assert warframe_profile is not None
    assert warframe_profile.username == "LLukas22"

@pytest.mark.asyncio
async def test_doesnt_retrieve_non_existing_profile():
    api = WarframeAPI()
    warframe_profile = await api.get_profile("DefinetlyNotLLukas22")
    assert warframe_profile is None
