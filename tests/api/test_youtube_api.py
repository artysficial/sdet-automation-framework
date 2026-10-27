"""YouTube Data API v3. Tests skip when YOUTUBE_API_KEY is not configured.

A stable, well-known video is used so the assertions do not depend on volatile content.
"""

import pytest

from config.settings import settings
from framework.api import YouTubeClient
from framework.schemas import assert_matches_schema

pytestmark = pytest.mark.youtube

STABLE_VIDEO_ID = "dQw4w9WgXcQ"  # Rick Astley - Never Gonna Give You Up (long-standing, public)


@pytest.mark.smoke
@pytest.mark.contract
def test_search_returns_video_results(youtube):
    response = youtube.search("selenium webdriver tutorial", max_results=5)

    assert response.status_code == 200
    items = response.json()["items"]
    assert 1 <= len(items) <= 5
    for item in items:
        assert_matches_schema(item, "youtube_search_item")


@pytest.mark.regression
def test_video_details_include_statistics(youtube):
    response = youtube.video(STABLE_VIDEO_ID)

    assert response.status_code == 200
    items = response.json()["items"]
    assert len(items) == 1
    video = items[0]
    assert video["snippet"]["title"]
    assert int(video["statistics"]["viewCount"]) > 0
    assert video["contentDetails"]["duration"].startswith("PT")


@pytest.mark.regression
def test_channel_of_known_video_resolves(youtube):
    channel_id = youtube.video(STABLE_VIDEO_ID).json()["items"][0]["snippet"]["channelId"]
    response = youtube.channel(channel_id)

    assert response.status_code == 200
    items = response.json()["items"]
    assert len(items) == 1
    assert int(items[0]["statistics"]["subscriberCount"]) >= 0


@pytest.mark.negative
@pytest.mark.regression
def test_nonexistent_video_returns_no_items(youtube):
    response = youtube.video("this-id-does-not-exist")

    assert response.status_code == 200
    assert response.json()["items"] == []


@pytest.mark.negative
@pytest.mark.contract
def test_invalid_api_key_is_rejected(request):
    # does not need a real key, only internet access
    client = YouTubeClient(settings.youtube_api_base, "AIzaSy-invalid-key-for-testing", timeout=settings.api_timeout)
    response = client.search("test", max_results=1)

    assert response.status_code in (400, 403)
    assert response.json()["error"]["errors"][0]["reason"] in {"keyInvalid", "badRequest", "forbidden"}
