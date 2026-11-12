from rest_framework.exceptions import APIException


class ExternalUnavailable(APIException):
    status_code = 503
    default_detail = "Service externe indisponible ou non configuré."
    default_code = "external_unavailable"


class Conflict(APIException):
    status_code = 409
    default_detail = "Cette transition est impossible dans l’état actuel."


class QuotaExceeded(APIException):
    status_code = 429
    default_detail = "Quota quotidien atteint."
