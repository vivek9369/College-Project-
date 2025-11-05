"""Lightweight local Clerk stub used for development/testing.

This avoids depending on an external Clerk SDK for local runs. It provides a
minimal `Clerk` class with `verify_token` that returns a simple user dict for
non-empty tokens and raises for invalid tokens.

In production, replace this file with the official Clerk SDK usage.
"""

class Clerk:
    def __init__(self, api_key=None):
        self.api_key = api_key

    def verify_token(self, token: str):
        """Verify a token and return a user-like dict.

        This is intentionally permissive for local development: any non-empty
        string token will be accepted and a fake user id returned. If you need
        stricter checks, plug in your real verification logic here.
        """
        if not token or not isinstance(token, str):
            raise Exception("Invalid token")

        # Return a very small user object expected by `app.py`
        return {"id": token}
