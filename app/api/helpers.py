def check_and_update_url_schema(url):
    """Credit : https://stackoverflow.com/questions/49983328
    I realize this is quite cheap.
    """
    if "://" not in url:
        url = "http://" + url
    return url
