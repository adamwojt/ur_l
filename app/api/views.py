from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse
from rest_framework import status

from .api_views import UrlList
from .helpers import check_and_update_url_schema
from .models import ClickLog, Url


def get_client_ip(request):
    # Credit: https://stackoverflow.com/a/4581997
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if x_forwarded_for:
        try:
            return x_forwarded_for.split(",")[0]
        except IndexError:
            return ""
    return request.META.get("REMOTE_ADDR", "")


def short_url(request, token):
    long_url = Url.objects.get_long_url(token)

    if not long_url:
        return render(request, "404.html", {"token": token}, status=404)

    click_log_data = {
        "ip_address": get_client_ip(request),
        "http_referer": request.headers.get("Referer", ""),
        "url_id": token,
    }
    ClickLog.objects.create(**click_log_data)

    return redirect(check_and_update_url_schema(long_url))

def short_url_examine(request, token):
    long_url = Url.objects.get_long_url(token)

    if not long_url:
        return render(request, "404.html", {"token": token}, status=404)

    return HttpResponse(f"Token {token} redirects to <b>{long_url}</b>")
    

@require_http_methods(["GET"])
def shorten_url(request):
    return render(request, "index.html")
