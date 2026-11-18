from decimal import Decimal

from django.conf import settings

from .models import AIUsage
from .services import LAST_USAGE


def record_usage(user, feature: str) -> None:
    usage = LAST_USAGE.get()
    if not usage:
        return
    LAST_USAGE.set(None)
    p, c = usage
    cost = (Decimal(p) * Decimal(settings.AI_PRICE_IN) + Decimal(c) * Decimal(settings.AI_PRICE_OUT)) / 1_000_000
    AIUsage.objects.create(user=user, feature=feature, model_name=settings.AI_MODEL,
                           prompt_tokens=p, completion_tokens=c, est_cost_usd=cost)