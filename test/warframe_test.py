import pytest
from src.warframe import WarframeAPI, Platform


def test_is_constructable():
    api = WarframeAPI()
    assert api is not None


@pytest.mark.parametrize(
    "username, platform",
    [
        ("LLukas22", Platform.PC),
        ("ScaledValkyrie", Platform.PS4),
    ],
)
@pytest.mark.asyncio
async def test_can_get_profile(username: str, platform: Platform):
    api = WarframeAPI()
    warframe_profile = await api.get_profile(username, platform)
    assert warframe_profile is not None
    assert warframe_profile.username == username


@pytest.mark.parametrize(
    "username, expected_platform",
    [
        ("LLukas22", Platform.PC),
        ("ScaledValkyrie", Platform.PS4),
    ],
)
@pytest.mark.asyncio
async def test_can_get_profile_from_all_platforms(
    username: str, expected_platform: Platform
):
    api = WarframeAPI()
    warframe_profile, platform = await api.get_profile_all_platforms(username)
    assert warframe_profile is not None
    assert platform == expected_platform
    assert warframe_profile.username == username


@pytest.mark.asyncio
async def test_doesnt_retrieve_non_existing_profile():
    api = WarframeAPI()
    warframe_profile = await api.get_profile("DefinetlyNotLLukas22", Platform.PC)
    assert warframe_profile is None
