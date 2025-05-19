# Authentication System

This project uses JSON Web Tokens (JWT) to protect API endpoints. Tokens are
issued when a user logs in and include the username and role information. Each
token has an expiration time and must be presented in the `Authorization`
header when accessing protected routes.

## Token Blacklist

When a user logs out or a token needs to be invalidated, the token is added to a
blacklist stored in Redis. The service hashes the token and stores it with a TTL
matching the token's remaining lifetime. Each request checks Redis for the
hashed token; if a match is found the JWT is considered revoked and the request
is rejected.
