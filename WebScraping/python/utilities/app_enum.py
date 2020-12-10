
# importing enum for enumerations
from enum import Enum

# creating enumerations using class 
# HTTP response status codes
class EnumStatusCode(Enum):
    # Other status code
    AN_REQUEST_EXCEPTION_OCCURRED = 0
    # Informational responses (100–199)
    CONTINUE = 100
    SWITCHING_PROTOCOL = 101
    PROCESSING = 102
    EARLY_HINTS = 103
    # SUCCESSFUL RESPONSES (200–299)
    OK = 200
    CREATED = 201
    ACCEPTED = 202
    NON_AUTHORITATIVE_INFORMATION = 203
    NO_CONTENT = 204
    # REDIRECTS (300–399)
    # CLIENT ERROR RESPONSES (400–499)
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    PAYMENT_REQUIRED = 402
    FORBIDDEN = 403
    NOT_FOUND = 404
    REQUEST_TIMEOUT = 405
    URI_TOO_LONG = 414
    TOO_MANY_REQUESTS = 429
    # SERVER ERRORS (500–599)
    INTERNAL_SERVER_ERROR = 500
    NOT_IMPLEMENTED = 501
    BAD_GATEWAY = 502
    SERVICE_UNAVAILABLE = 503
    GATEWAY_TIMEOUT = 504
    HTTP_VERSION_NOT_SUPPORTED = 505

    @classmethod
    def _missing_(cls, value):  # if status code dont match, it will return AN_REQUEST_EXCEPTION_OCCURRED
        return EnumStatusCode.AN_REQUEST_EXCEPTION_OCCURRED


# creating enumerations using class 
# HTTP response status codes
class EnumMainOptions(Enum):
    SCRAPING_WITHOUT_SELENIUM = 1
    SCRAPING_WITH_SELENIUM = 2
