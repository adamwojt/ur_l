import os

from django.apps import AppConfig


class ApiConfig(AppConfig):
    name = "api"

    # Higher -> Less collisions, Lower -> Prettier
    # NOTE: migration needed when changing lenght.
    # TOKEN_LENGHT_STR ~= TOKEN_LENGHT_BYTES * 1.3
    # More here https://docs.python.org/3/library/secrets.html#secrets.token_urlsafe

    TOKEN_LENGHT_BYTES = 5
    TOKEN_LENGHT_STR = 7

    # Determines how long token will stay in cache after creation
    # Default : 15 min
    CACHE_TIMEOUT_CREATE = os.environ.get("CACHE_TIMEOUT_CREATE", 900)

    # Determines how long token will stay in cache after read
    # NOTE: Cache timeout will refresh each time is being read
    # Default : 15 min
    CACHE_TIMEOUT_READ = os.environ.get("CACHE_TIMEOUT_CREATE", 900)
