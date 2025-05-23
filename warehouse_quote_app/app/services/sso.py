class SSOProvider:
    """Placeholder service for verifying SSO tokens."""

    def verify_token(self, provider: str, token: str) -> dict:
        """Verify a token with the given provider and return user info.

        This is a simplified placeholder implementation. Real SSO integration
        should validate the token using the provider's SDK or API.
        """
        # TODO: Implement real SSO verification
        if not token:
            raise ValueError("Invalid SSO token")
        # For demo purposes, just return a fake user payload
        return {"email": token, "provider": provider}
