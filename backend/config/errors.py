import logging

from rest_framework.response import Response
from rest_framework.views import exception_handler

log = logging.getLogger(__name__)


def handler(exc, ctx):
    resp = exception_handler(exc, ctx)
    if resp is None:
        log.exception("Unhandled error")
        return Response({"error": "Internal server error"}, status=500)
    resp.data = {"error": resp.data}
    return resp