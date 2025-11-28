import json
import os
from functools import wraps

import jwt
from jwt import PyJWKClient
from flask import request, g, jsonify

SUPABASE_URL = os.environ.get("SUPABASE_URL")

assert SUPABASE_URL is not None

SUPABASE_URL = SUPABASE_URL.rstrip("/")

ISSUER = f"{SUPABASE_URL}/auth/v1"
JWKS_URL = f"{ISSUER}/.well-known/jwks.json"

jwks_client = PyJWKClient(JWKS_URL)


def verify_supabase_jwt(token: str) -> dict:
    """
    Verify a Supabase access token and return its claims
    """
    signing_key = jwks_client.get_signing_key_from_jwt(token)
    return jwt.decode(
        token,
        signing_key.key,
        algorithms=["HS256", "RS256", "ES256"],
        audience="authenticated",
        issuer=ISSUER,
    )


def require_supabase_user(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing bearer token"}), 401

        token = auth_header.split(" ", 1)[1].strip()
        try:
            claims = verify_supabase_jwt(token)
        except Exception as _:
            return jsonify({"error": "Invalid or expired token"}), 401

        # Make user info available to view functions
        g.jwt_claims = claims
        g.user_id = claims.get("sub")

        return fn(*args, **kwargs)

    return wrapper
