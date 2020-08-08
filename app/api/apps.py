import os

from django.apps import AppConfig


class ApiConfig(AppConfig):
    name = "api"

    # Higher -> Less collisions, Lower -> Prettier
    # NOTE: migration needed when changing length.
    # TOKEN_LENGTH_STR ~= TOKEN_LENGTH_BYTES * 1.3
    # More here https://docs.python.org/3/library/secrets.html#secrets.token_urlsafe

    TOKEN_LENGTH_BYTES = 5
    TOKEN_LENGTH_STR = 7

    USE_CACHE = os.environ.get("URL_USE_CACHE") == "1"
    # Determines how long token will stay in cache after creation
    # Default : 15 min
    CACHE_TIMEOUT_CREATE = int(os.environ.get("CACHE_TIMEOUT_CREATE"))

    # Determines how long token will stay in cache after read
    # NOTE: Cache timeout will refresh each time is being read
    # Default : 15 min
    CACHE_TIMEOUT_READ = int(os.environ.get("CACHE_TIMEOUT_READ"))

    # Log token collisions for metrics
    LOG_COLLISIONS = os.environ.get("LOG_TOKEN_COLLISION") == "1"
