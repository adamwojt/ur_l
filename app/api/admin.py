from django import forms
from django.contrib import admin
from django.contrib.admin.views.main import ChangeList
from django.core.paginator import EmptyPage, InvalidPage, Paginator

from .helpers import check_and_update_url_schema
from .models import ClickLog, CollisionLog, Url


class InlineChangeList(object):
    can_show_all = True
    multi_page = True
    get_query_string = ChangeList.__dict__["get_query_string"]

    def __init__(self, request, page_num, paginator):
        self.show_all = "all" in request.GET
        self.page_num = page_num
        self.paginator = paginator
        self.result_count = paginator.count
        self.params = dict(request.GET.items())


class PaginationInline(admin.TabularInline):
    template = "admin/edit_inline/tabular_paginated.html"
    per_page = 10
    model = ClickLog

    def get_formset(self, request, obj=None, **kwargs):
        formset_class = super(PaginationInline, self).get_formset(
            request, obj, **kwargs
        )

        class PaginationFormSet(formset_class):
            def __init__(self, *args, **kwargs):
                super(PaginationFormSet, self).__init__(*args, **kwargs)

                qs = self.queryset
                paginator = Paginator(qs, self.per_page)
                try:
                    page_num = int(request.GET.get("p", "0"))
                except ValueError:
                    page_num = 0

                try:
                    page = paginator.page(page_num + 1)
                except (EmptyPage, InvalidPage):
                    page = paginator.page(paginator.num_pages)

                self.cl = InlineChangeList(request, page_num, paginator)
                self.paginator = paginator

                if self.cl.show_all:
                    self._queryset = qs
                else:
                    self._queryset = page.object_list

        PaginationFormSet.per_page = self.per_page
        return PaginationFormSet


class ClickLogInline(PaginationInline):
    model = ClickLog
    extra = 0


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
