import re
from urllib.parse import quote

from django.core.exceptions import ValidationError


def is_valid_url(url):
    encoded_url = quote(url, safe=':/?=&,')
    if not re.match(r'^https?://', encoded_url):
        raise ValidationError('Invalid URL')
    return encoded_url


def is_valid_domain(domain):
    if not re.match(r'^([a-zA-Z0-9-]+\.)*[a-zA-Z0-9-]+\.[a-z]{2,}$', domain):
        raise ValidationError('Invalid Domain')
    return domain
