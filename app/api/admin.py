from django.contrib import admin
from django.db.models import Count

from .models import ClickLog, CollisionLog, Url


class ClickLogInline(admin.TabularInline):
    model = ClickLog
    extra = 1
    max_num = 3


@admin.register(Url)
class UrlAdmin(admin.ModelAdmin):
    _url_lenght = 30
    inlines = [
        ClickLogInline,
    ]
    list_display = ("token", "short_long_url", "create_date", "click_count")
    fields = ("token", "long_url", "create_date", "click_count")
    date_hierarchy = "create_date"
    list_filter = ("create_date",)
    search_fields = ("token", "long_url")

    def short_long_url(self, obj):
        """ Short url"""
        suffix = "..." if len(obj.long_url) > self._url_lenght - 3 else ""
        return obj.long_url[: self._url_lenght] + suffix

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
