import logging
from typing import Dict, Any, Optional

from app.core.config import settings

logger = logging.getLogger("app.core.sentry")


def _before_send_filter(event: Dict[str, Any], hint: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Sanitize Sentry events before dispatching to prevent accidental credential leakage.
    Strips sensitive HTTP headers and auth tokens.
    """
    if "request" in event and "headers" in event["request"]:
        headers = event["request"]["headers"]
        sensitive_keys = {"authorization", "cookie", "x-api-key", "clerk-secret-key"}
        
        if isinstance(headers, dict):
            for k in list(headers.keys()):
                if k.lower() in sensitive_keys:
                    headers[k] = "[REDACTED]"

    return event


def init_sentry() -> bool:
    """
    Initialize Sentry SDK for error monitoring if SENTRY_DSN is configured.
    Returns True if initialized, False otherwise.
    """
    if not settings.SENTRY_DSN:
        logger.info("Sentry DSN not configured; error reporting disabled.")
        return False

    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            environment=settings.ENV,
            traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
            before_send=_before_send_filter,
            integrations=[
                FastApiIntegration(),
                SqlalchemyIntegration(),
            ],
        )
        logger.info("Sentry SDK initialized successfully for environment: %s", settings.ENV)
        return True
    except ImportError:
        logger.warning("sentry-sdk package not installed; skipping Sentry initialization.")
        return False
    except Exception as exc:
        logger.error("Failed to initialize Sentry SDK: %s", exc)
        return False
