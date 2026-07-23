
import uuid
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from datetime import datetime


# ------------------------------------------------------
# Backup Provider Interface
# ------------------------------------------------------
class BackupProvider(ABC):
    """Abstract base class for backup providers (database, file, cloud)."""

    @abstractmethod
    async def create_backup(
        self,
        business_id: uuid.UUID,
        backup_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a new backup. Returns backup metadata."""
        pass

    @abstractmethod
    async def restore_backup(
        self,
        backup_id: str,
        business_id: uuid.UUID
    ) -> bool:
        """Restore from a backup. Returns True if successful."""
        pass

    @abstractmethod
    async def list_backups(
        self,
        business_id: uuid.UUID,
        limit: int = 50
    ) -> list[Dict[str, Any]]:
        """List all backups for a business."""
        pass

    @abstractmethod
    async def delete_backup(
        self,
        backup_id: str,
        business_id: uuid.UUID
    ) -> bool:
        """Delete a backup. Returns True if successful."""
        pass


# ------------------------------------------------------
# Database Backup Provider (Interface)
# ------------------------------------------------------
class DatabaseBackupProvider(BackupProvider, ABC):
    """Abstract base class for database-specific backup providers."""
    pass


# ------------------------------------------------------
# File Backup Provider (Interface)
# ------------------------------------------------------
class FileBackupProvider(BackupProvider, ABC):
    """Abstract base class for file-specific backup providers."""
    pass


# ------------------------------------------------------
# Cloud Backup Provider (Interface)
# ------------------------------------------------------
class CloudBackupProvider(BackupProvider, ABC):
    """Abstract base class for cloud-specific backup providers."""
    pass


# ------------------------------------------------------
# Backup Manager
# ------------------------------------------------------
class BackupManager:
    """Manager for handling backup providers and backup operations."""

    def __init__(self):
        self.database_provider: Optional[DatabaseBackupProvider] = None
        self.file_provider: Optional[FileBackupProvider] = None
        self.cloud_provider: Optional[CloudBackupProvider] = None

    def register_database_provider(self, provider: DatabaseBackupProvider) -> None:
        """Register a database backup provider."""
        self.database_provider = provider

    def register_file_provider(self, provider: FileBackupProvider) -> None:
        """Register a file backup provider."""
        self.file_provider = provider

    def register_cloud_provider(self, provider: CloudBackupProvider) -> None:
        """Register a cloud backup provider."""
        self.cloud_provider = provider

    async def create_full_backup(
        self,
        business_id: uuid.UUID,
        backup_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a full backup using all registered providers."""
        backup_results: Dict[str, Any] = {
            "business_id": str(business_id),
            "created_at": datetime.now().isoformat(),
            "name": backup_name,
            "metadata": metadata or {},
            "providers": {}
        }

        if self.database_provider:
            backup_results["providers"]["database"] = await self.database_provider.create_backup(
                business_id, backup_name, metadata
            )

        if self.file_provider:
            backup_results["providers"]["file"] = await self.file_provider.create_backup(
                business_id, backup_name, metadata
            )

        if self.cloud_provider:
            backup_results["providers"]["cloud"] = await self.cloud_provider.create_backup(
                business_id, backup_name, metadata
            )

        return backup_results

