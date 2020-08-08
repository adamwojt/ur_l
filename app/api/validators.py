from django.core.validators import URLValidator


class OptionalSchemeURLValidator(URLValidator):
    """Credit : https://stackoverflow.com/questions/49983328"""

    def __call__(self, value):
        if "://" not in value:
            # Validate as if it was http://
            value = "http://" + value
        super(OptionalSchemeURLValidator, self).__call__(value)
