from django import forms
from django.contrib import admin

from .helpers import check_and_update_url_schema
from .models import ClickLog, CollisionLog, Url


class ClickLogInline(admin.TabularInline):
    model = ClickLog
    extra = 1
    max_num = 3


class UrlAdminForm(forms.ModelForm):
    def clean_token(self):
        token = self.cleaned_data.get("token")
        if token in ("random", "r"):
            return Url.objects._get_random_url_token()
        return token

    def clean_long_url(self):
        return check_and_update_url_schema(self.cleaned_data["long_url"])


@admin.register(Url)
class UrlAdmin(admin.ModelAdmin):
    form = UrlAdminForm
    _url_length = 30
    inlines = [
        ClickLogInline,
    ]
    list_display = ("token", "short_long_url", "create_date", "click_count")
    fields = ("token", "long_url", "create_date", "click_count", "click_limit")
    date_hierarchy = "create_date"
    list_filter = ("create_date",)
    search_fields = ("token", "long_url")

    def short_long_url(self, obj):
        """ This is just to avoid long urls on list view"""
        suffix = "..." if len(obj.long_url) > self._url_length - 3 else ""
        return obj.long_url[: self._url_length] + suffix

    short_long_url.short_description = "long_url"  # IKR

    def click_count(self, obj):
        """ Click count """
        return obj.clicks.all().count()

    def get_readonly_fields(self, request, obj=None):
        base = ("create_date", "click_count")
        if obj:
            return base + ("token",)
        return base


@admin.register(CollisionLog)
class CollisionLogAdmin(admin.ModelAdmin):
    date_hierarchy = "collision_date"
    list_filter = ("collision_date",)
    search_fields = ("token",)
    list_display = ("token", "collision_date")
