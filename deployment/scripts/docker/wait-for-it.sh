#!/bin/sh
# wait-for-it.sh - Waits for dependent services to be ready

set -e

# Function to check if PostgreSQL is ready
check_postgres() {
    host="$1"
    >&2 echo "Checking PostgreSQL connection..."
    until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$host" -U "postgres" -c '\q'; do
        >&2 echo "PostgreSQL is unavailable - sleeping"
        sleep 1
    done
    >&2 echo "PostgreSQL is up!"
}

# Function to check if Redis is ready
check_redis() {
    host="$1"
    >&2 echo "Checking Redis connection..."
    until redis-cli -h "$host" ping > /dev/null 2>&1; do
        >&2 echo "Redis is unavailable - sleeping"
        sleep 1
    done
    >&2 echo "Redis is up!"
}

# Check PostgreSQL
if [ -n "$POSTGRES_HOST" ]; then
    check_postgres "$POSTGRES_HOST"
fi

# Check Redis
if [ -n "$REDIS_HOST" ]; then
    check_redis "$REDIS_HOST"
fi

>&2 echo "All services are up - executing command"
exec "$@"
