from django.shortcuts import redirect
from django.urls import path, re_path
from django.views.decorators.cache import never_cache
from rest_framework.documentation import include_docs_urls

from . import api_views, views
from .apps import ApiConfig as conf


def _redirect_to_url_api_list_view(_):
    return redirect("/" + conf.API_URL_PATH, permanent=False)


urlpatterns = [
    path("", _redirect_to_url_api_list_view),
    re_path(conf.SHORT_URL_PATH, never_cache(views.short_url)),
    path(conf.API_URL_PATH, api_views.UrlList.as_view()),
    re_path(conf.API_TOKEN_PATH, api_views.UrlDetail.as_view()),
    path(conf.API_ROOT_PATH, _redirect_to_url_api_list_view),
    path(conf.API_DOCS_PATH, include_docs_urls(title=conf.API_DOCS_TITLE)),
]
