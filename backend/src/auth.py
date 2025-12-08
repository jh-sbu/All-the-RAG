import os
from functools import wraps

from dotenv import load_dotenv
import jwt
from jwt import PyJWKClient
from flask import request, g

from atr_logger import get_logger
from models.auth_context import AuthContext, Claims

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")

assert SUPABASE_URL is not None

SUPABASE_URL = SUPABASE_URL.rstrip("/")

ISSUER = f"{SUPABASE_URL}/auth/v1"
JWKS_URL = f"{ISSUER}/.well-known/jwks.json"

logger = get_logger()
jwks_client = PyJWKClient(JWKS_URL)

logger.debug(f"jwks_client: {jwks_client}")


def verify_supabase_jwt(token: str) -> dict[str, str]:
    """
    Verify a Supabase access token and return its claims
    """
    signing_key = jwks_client.get_signing_key_from_jwt(token)
    return jwt.decode(
        token,
        signing_key.key,
        algorithms=["ES256"],
        audience="authenticated",
        issuer=ISSUER,
    )


def auth_supabase_user(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            logger.info("No bearer token found")
            g.auth = AuthContext(_protected_claims=None)

        else:
            token = auth_header.split(" ", 1)[1].strip()

            try:
                claims = verify_supabase_jwt(token)
                # Make user info available to view functions
                iss = claims.get("iss", None)
                sub = claims.get("sub", None)

                if iss is not None and sub is not None:
                    g.auth = AuthContext(
                        _protected_claims=Claims(
                            iss=iss,
                            sub=sub,
                        )
                    )
                else:
                    g.auth = AuthContext(_protected_claims=None)

            except Exception as e:
                logger.error(f"Failed to verify Supabase JWT: {e}")

        return fn(*args, **kwargs)

    return wrapper
