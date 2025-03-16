"""
Core functionality and configuration.

This package provides core functionality for the application:
1. Authentication and Authorization (auth)
2. Configuration Management (config)
3. Security Features (security)
4. Monitoring and Logging (monitoring)
5. Admin Functions (admin)
6. Background Tasks (tasks)
"""

# Import settings first as it's required by other modules
from .config import settings

# Import monitoring components
from .monitoring import (
    log_event,
    get_logger,
    log_error
)

# Import security components
from .security import (
    rate_limit,
    get_client_ip,
    verify_password,
    get_password_hash,
    generate_secure_token,
    validate_api_key,
    CustomHTTPBearer
)

# Import task components
from .tasks import celery_app, init_celery

# Import auth components
from .auth import (
    create_access_token,
    get_current_user,
    get_current_active_user,
    get_current_admin_user,
    TokenDep,
    UserDep,
    ActiveUserDep,
    AdminUserDep
)

# Import admin components
from .admin import (
    check_admin_permission,
    admin_required,
    get_admin_users,
    grant_admin,
    revoke_admin
)

__all__ = [
    # Config
    'settings',
    
    # Monitoring
    'log_event',
    'get_logger',
    'log_error',
    
    # Security
    'rate_limit',
    'get_client_ip',
    'verify_password',
    'get_password_hash',
    'generate_secure_token',
    'validate_api_key',
    'CustomHTTPBearer',
    
    # Tasks
    'celery_app',
    'init_celery',
    
    # Auth
    'create_access_token',
    'get_current_user',
    'get_current_active_user',
    'get_current_admin_user',
    'TokenDep',
    'UserDep',
    'ActiveUserDep',
    'AdminUserDep',
    
    # Admin
    'check_admin_permission',
    'admin_required',
    'get_admin_users',
    'grant_admin',
    'revoke_admin'
]
