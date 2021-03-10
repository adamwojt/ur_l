import os

from django.apps import AppConfig
from django.conf import settings

class ApiConfig(AppConfig):
    name = "api"

    # Higher -> Less collisions, Lower -> Prettier
    # NOTE: migration needed when changing length.
    # TOKEN_LENGTH_STR ~= TOKEN_LENGTH_BYTES * 1.3
    # More here https://docs.python.org/3/library/secrets.html#secrets.token_urlsafe

    TOKEN_LENGTH_BYTES = 5
    TOKEN_LENGTH_STR = 7
    TOKEN_REGEX_MATCH = rf"(?P<token>[A-Za-z0-9+_-]{{{TOKEN_LENGTH_STR}}})"

    SHORT_URL_PATH = rf"^{TOKEN_REGEX_MATCH}\/?$"
    SHORT_URL_EXAMINE_PATH = rf"^{TOKEN_REGEX_MATCH}\/examine\/?$"
    API_ROOT_PATH = "api/"
    API_URL_PATH = f"{API_ROOT_PATH[:-1]}/urls/"
    API_TOKEN_PATH = rf"^{API_URL_PATH[:-1]}/{TOKEN_REGEX_MATCH}/"
    API_DOCS_PATH = f"{API_ROOT_PATH[:-1]}/docs/"
    API_DOCS_TITLE = "Oor.lu Url Shortener Api"

    # Determines how long token will stay in cache after creation
    # Default : 15 min
    CACHE_TIMEOUT_CREATE = int(os.environ.get("CACHE_TIMEOUT_CREATE"))

    # Determines how long token will stay in cache after read
    # NOTE: Cache timeout will refresh each time is being read
    # Default : 15 min
    CACHE_TIMEOUT_READ = int(os.environ.get("CACHE_TIMEOUT_READ"))

    # Log token collisions for metrics
    LOG_COLLISIONS = os.environ.get("LOG_TOKEN_COLLISION") == "1"
    BANNED_NETLOCS = frozenset(line.strip() for line in open(settings.BASE_DIR / 'banned_netlocs'))
