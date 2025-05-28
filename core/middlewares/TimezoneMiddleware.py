import pytz
from django.utils import timezone


class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tzname = request.headers.get("X-Timezone")
        if tzname in pytz.all_timezones:
            timezone.activate(pytz.timezone(tzname))
        else:
            timezone.deactivate()

        response = self.get_response(request)
        return response
