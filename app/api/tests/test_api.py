""" 
   isort:skip_file
   clashes with black
"""

import pytest
from django.core.cache import cache
from django.http import (
    HttpResponseNotFound,
    HttpResponsePermanentRedirect,
    HttpResponseRedirect,
)
from pytest_django.asserts import assertTemplateUsed
from rest_framework.status import (
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
)
from rest_framework.test import APIClient

from ..apps import ApiConfig as conf
from ..models import Url


@pytest.fixture
def api_client():
    client = APIClient()

    yield client


@pytest.mark.parametrize(
    "path, path_expected",
    [
        ("", f"/{conf.API_URL_PATH}"),
        (f"/{conf.API_ROOT_PATH}", f"/{conf.API_URL_PATH}"),
    ],
)
def test_redirect(path, path_expected, client):
    response = client.get(path)
    assert isinstance(response, HttpResponseRedirect)
    assert response.url == path_expected


@pytest.mark.django_db
@pytest.mark.parametrize("path", [("/not_found"), (f"/{conf.API_ROOT_PATH}/models"),])
def test_404(path, client):
    with assertTemplateUsed("404.html"):
        response = client.get(path)
        assert isinstance(response, HttpResponseNotFound)


@pytest.mark.django_db
def test_api_workflow(api_client, django_assert_num_queries):
    limit = 4
    urls_create = [
        {
            "data": {"long_url": "invalid",},
            "expected": {"long_url": ["Wrong url given"]},
            "status": HTTP_400_BAD_REQUEST,
        },
        {
            "data": {"long_url": "www.google.com",},
            "expected": {"long_url": "http://www.google.com", "click_limit": 0},
            "status": HTTP_201_CREATED,
        },
        {
            "data": {"long_url": "www.google.com",},
            "expected": {"long_url": "http://www.google.com", "click_limit": 0},
            "status": HTTP_201_CREATED,
        },
        {
            "data": {"long_url": "https://with.limit", "click_limit": limit},
            "expected": {"long_url": "https://with.limit", "click_limit": limit},
            "status": HTTP_201_CREATED,
            "with_limit": True,
        },
    ]
    created = []
    for url in urls_create:
        response = api_client.post(
            f"/{conf.API_URL_PATH}", data=url["data"], format="json"
        )

        data = response.json()

        assert response.status_code == url["status"]

        if url["status"] == HTTP_201_CREATED:
            assert data["token"] in data["short_url"]
            created.append(data)
            data_assert = data.copy()
            for key in ("token", "short_url"):  # This is random
                data_assert.pop(key)

        else:
            data_assert = data

        # Let's capture data with random token for later use
        if url.get("with_limit"):
            with_limit = data

        assert data_assert == url["expected"]

    # Let's make sure we get same in with GET

    for url in created:
        response = api_client.get(
            f"/{conf.API_URL_PATH}{url['token']}/?clicks=1",
            content_type="application/json",
            format="json",
        )
        url.update(click_count=0)
        assert response.json() == url

    # And List
    response = api_client.get(f"/{conf.API_URL_PATH}", content_type="application/json")
    assert len(response.json()) == len(created)

    # Let's see if cache works
    with django_assert_num_queries(0):
        for url in created:
            response = api_client.get(
                f"/{conf.API_URL_PATH}{url['token']}", content_type="application/json"
            )

    # Now let's click

    for url in created:
        response = api_client.get(f"/{url['token']}")
        assert isinstance(response, HttpResponsePermanentRedirect)
        assert response.url == url["long_url"]
        assert Url.objects.get(token=url["token"]).clicks.count() == 1

    limit = limit - 1

    # Let's see example with limit will be deleted

    for _ in range(limit):
        response = api_client.get(f"/{with_limit['token']}")
        assert isinstance(response, HttpResponsePermanentRedirect)
        assert response.url == with_limit["long_url"]

    # Now we should get 404 - even cache should be empty here

    response = api_client.get(f"/{with_limit['token']}")
    assert response.status_code == HTTP_404_NOT_FOUND

    # Now let's test PUT
    url = Url.objects.all()[0]
    new_url = "https://brand.new"
    response = api_client.put(
        f"/{conf.API_URL_PATH}{url.token}/", data={"long_url": new_url}, format="json"
    )

    # Now let's see click logs
    ip = "1.2.3.4"
    referer = "refer.er"
    response = api_client.get(
        f"/{url.token}", HTTP_X_FORWARDED_FOR=ip, HTTP_REFERER=referer
    )
    log = url.clicks.all()[1]
    assert log.http_referer == referer
    assert log.ip_address == ip

    # Let's make sure cache was updated too
    assert cache.get(url.token) == new_url
    # Requery
    url = Url.objects.get(token=url.token)
    assert url.long_url == new_url

    # Finally delete all

    for url in Url.objects.all():
        response = api_client.delete(f"/{conf.API_URL_PATH}{url.token}/")
        assert response.status_code == HTTP_204_NO_CONTENT

    assert not Url.objects.all()
