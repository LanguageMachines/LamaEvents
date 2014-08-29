from django.conf import settings

class MobileTemplatesMiddleware(object):
    """Determines which set of templates to use for a mobile site"""

    ORIG_TEMPLATE_DIRS = settings.TEMPLATE_DIRS

    def process_request(self, request):
        # sets are used here, you can use other logic if you have an older version of Python
        MOBILE_SUBDOMAINS = set(['m', 'mobile'])
        domain = set(request.META.get('HTTP_HOST', '').split('.'))

        if len(MOBILE_SUBDOMAINS & domain):
            settings.TEMPLATE_DIRS = settings.MOBILE_TEMPLATE_DIRS + self.ORIG_TEMPLATE_DIRS
        else:
            settings.TEMPLATE_DIRS = settings.DESKTOP_TEMPLATE_DIRS + self.ORIG_TEMPLATE_DIRS
