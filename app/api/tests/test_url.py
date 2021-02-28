import pytest
from django.core.cache import cache

from ..apps import ApiConfig
from ..models import CollisionLog, Url


class TestURLWithoutDB:
    def test_get_random_url_token(self):
        """ Test _get_random_url_token"""
        token = Url.objects._get_random_url_token()
        assert len(token) == ApiConfig.TOKEN_LENGTH_STR


@pytest.mark.django_db
class TestURLWithDB:
    schema_url = "https://www.google.com"
    test_token = "test"  # nosec

    def setup_method(self, method):
        ApiConfig.USE_CACHE = "cache" in method.__name__

    def test_create_url(self):
        Url.objects.create_short_url(self.schema_url)

    def test_cache_life_cycle(self):
        # First create and check if cache exists
        url = Url.objects.create_short_url(self.schema_url)
        token = url.token
        assert cache.get(token) == url.long_url

        # Change long_url and see if cache was updated
        new_url = "www.new.com"
        url.long_url = new_url
        url.save()
        assert cache.get(token) == new_url

        # Delete and check if cache was deleted too
        url.delete()
        assert not cache.get(token)

    def test_no_cash3_created(self):
        """ See `setup_method` """
        url = Url.objects.create_short_url(self.schema_url)
        assert not cache.get(url.token)

    def test_token_collision(self):
        url = Url.objects.create_short_url(self.schema_url, token=self.test_token)
        url2 = Url.objects.create_short_url(self.schema_url, token=self.test_token)
        assert not url.token == url2.token

        collision_log = CollisionLog.objects.get(token=self.test_token)
        assert collision_log.token == self.test_token

    def test_collisions_are_rare(self):
        for _ in range(1000):
            Url.objects.create_short_url(self.schema_url)
        assert CollisionLog.objects.all().count() <= 3

    def test_token_no_collsion_log(self):
        ApiConfig.LOG_COLLISIONS = False
        url = Url.objects.create_short_url(self.schema_url, token=self.test_token)
        url2 = Url.objects.create_short_url(self.schema_url, token=self.test_token)
        with pytest.raises(CollisionLog.DoesNotExist):
            CollisionLog.objects.get(token=self.test_token)

    def test_get_url_using_cache(self, django_assert_num_queries):
        url = Url.objects.create_short_url(self.schema_url, token=self.test_token)
        with django_assert_num_queries(0):
            assert Url.objects.get_long_url(url.token) == url.long_url

    def test_get_url_using_db(self, django_assert_num_queries):
        url = Url.objects.create_short_url(self.schema_url, token=self.test_token)
        with django_assert_num_queries(1):
            assert Url.objects.get_long_url(url.token) == url.long_url
