from rest_framework.exceptions import APIException


class ExternalUnavailable(APIException):
    status_code = 503
    default_detail = "Service IA indisponible ou non configuré."
    default_code = "external_unavailable"


class QuotaExceeded(APIException):
    status_code = 429
    default_detail = "Quota quotidien IA atteint."
    default_code = "ai_quota_exceeded"
