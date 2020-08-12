import logging
import secrets

from django.core.cache import cache
from django.core.validators import URLValidator
from django.db import models
from django.db.models.signals import post_delete, post_save
from django.dispatch.dispatcher import receiver

from .apps import ApiConfig as conf

_logger = logging.getLogger(__name__)


class CollisionLog(models.Model):
    token = models.CharField(max_length=conf.TOKEN_LENGTH_STR, db_index=True)
    collision_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.token


class ClickLog(models.Model):
    url = models.ForeignKey("Url", on_delete=models.CASCADE, related_name="clicks")
    click_date = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(default="0.0.0.0")
    http_referer = models.CharField(max_length=500, blank=True)

    def __str__(self):
        return self.url_id


@receiver(post_save, sender=ClickLog)
def _click_log_post_save(sender, instance, *args, **kwargs):
    """ Observe number of clicks and remove when limit is reached
    """
    limit = instance.url.click_limit
    if not kwargs.get("created") or not limit:
        return
    total_clicks = instance.url.clicks.count()
    if total_clicks >= limit:
        instance.url.delete()


class UrlManager(models.Manager):
    @staticmethod
    def _get_random_url_token():
        return secrets.token_urlsafe(conf.TOKEN_LENGTH_BYTES)

    @staticmethod
    def _on_token_collision(token):
        _logger.debug("Token collision : %s", token)
        if conf.LOG_COLLISIONS:
            CollisionLog.objects.create(token=token)

    def create_short_url(self, long_url, click_limit=None, token=None):
        """Create retrying on token collision

        Args:
            long_url (str)
            token (str, optional) - mostly for tests

        Returns:
            TYPE: bool
        """
        token = token or self._get_random_url_token()

        collision_free = False
        while not collision_free:
            try:
                self.get(pk=token)
            except self.model.DoesNotExist:
                collision_free = True
            else:
                self._on_token_collision(token)
                token = self._get_random_url_token()

        create_data = {"token": token, "long_url": long_url}

        if click_limit:
            create_data.update(click_limit=click_limit)

        return self.create(**create_data)

    def get_long_url(self, token):
        """Fetch long url using token

        Args:
            token (str)

        Returns:
            TYPE: str
        """
        long_url = ""

        if conf.USE_CACHE:
            long_url = cache.get(token)

        if not long_url:
            try:
                long_url = self.get(pk=token).long_url
            except self.model.DoesNotExist:
                pass
            else:
                _logger.debug("Token fetched from db : %s", token)
        else:
            _logger.debug("Token fetched from cache : %s", token)

        if long_url:
            if conf.USE_CACHE:
                cache.set(token, long_url, timeout=conf.CACHE_TIMEOUT_READ)

        return long_url


class Url(models.Model):
    token = models.CharField(
        max_length=conf.TOKEN_LENGTH_STR,
        primary_key=True,
        db_index=True,
        help_text="Type `random` or `r` to generate random token",
    )
    long_url = models.CharField(max_length=500, validators=[URLValidator()])
    create_date = models.DateTimeField(auto_now_add=True)
    click_limit = models.IntegerField(
        default=0, help_text="Remove url when this is reached"
    )
    objects = UrlManager()

    def __str__(self):
        return self.token


@receiver(post_delete, sender=Url)
def _url_post_delete(sender, instance, *args, **kwargs):
    """ Clear cache on delete """
    if conf.USE_CACHE:
        cache.delete(instance.token)


@receiver(post_save, sender=Url)
def _url_post_save(sender, instance, *args, **kwargs):
    """ Update cache on save preserving timeout
        Credit: https://stackoverflow.com/a/7934958
    """
    if conf.USE_CACHE:
        timeout = cache.ttl(instance.token)
        if timeout or kwargs.get("created"):
            cache.set(
                instance.token,
                instance.long_url,
                timeout=timeout or conf.CACHE_TIMEOUT_CREATE,
            )
