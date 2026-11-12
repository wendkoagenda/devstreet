from rest_framework.throttling import AnonRateThrottle, SimpleRateThrottle


class PublicProjectThrottle(AnonRateThrottle):
    scope = "chantier_public"
    rate = "60/minute"


class GiteaWebhookThrottle(SimpleRateThrottle):
    scope = "chantier_webhook"
    rate = "120/minute"

    def get_cache_key(self, request, view):
        return self.cache_format % {
            "scope": self.scope,
            "ident": self.get_ident(request),
        }
