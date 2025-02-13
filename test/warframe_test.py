import pytest
from src.warframe import WarframeAPI, Platform
import asyncio


def test_is_constructable():
    api = WarframeAPI()
    assert api is not None


@pytest.mark.skip(reason="Currently unsupported")
@pytest.mark.parametrize(
    "username, platform",
    [
        ("LLukas22", Platform.PC),
        ("ScaledValkyrie", Platform.PS4),
        (
            "GrantTheWish",
            Platform.PS4,
        ),  # This is a multi-platform user which has a different username on PC
        (
            "Victor_Z_1992",
            Platform.PS4,
        ),  # This is a multi-platform user which has the same username on PC
        ("LLukas44", Platform.SWITCH),
        ("scifilord2003", Platform.XBOX),
        (
            "LivewareProblem",
            Platform.PC,
        ),  # This account has an account with a similar name on the Switch
    ],
)
@pytest.mark.asyncio
async def test_can_get_profile(username: str, platform: Platform):
    api = WarframeAPI()
    warframe_profile = await api.get_profile(username, platform)
    assert warframe_profile is not None
    assert warframe_profile.platform_names[platform] == username


@pytest.mark.skip(reason="Currently unsupported")
@pytest.mark.parametrize(
    "username, platform",
    [("LivewareProblem", Platform.SWITCH), ("sayed3210", Platform.PC)],
)
@pytest.mark.asyncio
async def test_doesnt_retrieve_pre_merge_slave_accounts(
    username: str, platform: Platform
):
    api = WarframeAPI()
    warframe_profile = await api.get_profile(username, platform)
    assert warframe_profile is None


@pytest.mark.skip(reason="Currently unsupported")
@pytest.mark.parametrize(
    "username, platform, is_multi_platform",
    [
        ("LLukas22", Platform.PC, True),
        ("LivewareProblem", Platform.PC, False),
        ("Victor_Z_1992", Platform.PS4, True),
        ("ScaledValkyrie", Platform.PS4, False),
        ("scifilord2003", Platform.XBOX, False),
        ("LLukas44", Platform.SWITCH, True),
    ],
)
@pytest.mark.asyncio
async def test_can_get_profile_from_all_platforms(
    username: str, platform: Platform, is_multi_platform: bool
):
    api = WarframeAPI()
    warframe_profile = await api.get_profile_all_platforms(username)
    assert warframe_profile is not None
    assert warframe_profile.multi_platform == is_multi_platform
    assert warframe_profile.platform_names[platform] == username


@pytest.mark.skip(reason="Currently unsupported")
@pytest.mark.asyncio
async def test_doesnt_retrieve_non_existing_profile():
    api = WarframeAPI()
    warframe_profile = await api.get_profile_all_platforms("DefinetlyNotLLukas22")
    assert warframe_profile is None


@pytest.mark.skip(reason="Currently unsupported")
@pytest.mark.parametrize(
    "username",
    [
        ("Dazzle"),
    ],
)
@pytest.mark.asyncio
async def test_can_get_profile_without_clan(username: str):
    api = WarframeAPI()
    warframe_profile = await api.get_profile_all_platforms(username)
    assert warframe_profile is not None


@pytest.mark.skip(reason="Currently unsupported")
@pytest.mark.asyncio
async def test_can_make_bulk_requests():
    api = WarframeAPI()
    usernames = ["LLukas22", "LivewareProblem", "Victor_Z_1992"] * 5
    tasks = [api.get_profile_all_platforms(username) for username in usernames]
    profiles = await asyncio.gather(*tasks)

    for profile in profiles:
        assert profile is not None
