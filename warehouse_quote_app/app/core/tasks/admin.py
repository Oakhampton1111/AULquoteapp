"""
Admin-related background tasks.
"""

import os
from datetime import datetime
from pathlib import Path
import shutil
import gzip

from warehouse_quote_app.app.core.tasks.celery import celery_app
from warehouse_quote_app.app.core.config import settings

@celery_app.task
def backup_database() -> str:
    """Backup the database to a compressed file.
    
    Returns:
        str: Path to the backup file
    """
    # Create backup directory if it doesn't exist
    backup_dir = Path(settings.BACKUP_DIR)
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate backup filename with timestamp
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    backup_file = backup_dir / f"backup_{timestamp}.sql.gz"
    
    # Get database URL components
    db_url = settings.DATABASE_URL
    if db_url.startswith("sqlite:///"):
        db_path = db_url[10:]  # Remove sqlite:///
        
        # Create compressed backup
        with open(db_path, 'rb') as f_in:
            with gzip.open(str(backup_file), 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
    else:
        # For other databases, use pg_dump or mysqldump
        raise NotImplementedError(
            "Database backup only implemented for SQLite"
        )
    
    # Remove old backups (keep last 7 days)
    for old_backup in backup_dir.glob("backup_*.sql.gz"):
        if (datetime.utcnow() - datetime.fromtimestamp(old_backup.stat().st_mtime)).days > 7:
            old_backup.unlink()
    
    return str(backup_file)

__all__ = ['backup_database']
