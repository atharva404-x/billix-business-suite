import uuid
import pytest
from typing import Optional, Dict, Any
from app.services.backup import (
    BackupManager,
    DatabaseBackupProvider,
    FileBackupProvider,
    CloudBackupProvider,
)


class DummyDatabaseBackupProvider(DatabaseBackupProvider):
    async def create_backup(
        self,
        business_id: uuid.UUID,
        backup_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        return {"status": "success", "provider": "database", "name": backup_name}

    async def restore_backup(self, backup_id: str, business_id: uuid.UUID) -> bool:
        return True

    async def list_backups(self, business_id: uuid.UUID, limit: int = 50) -> list[Dict[str, Any]]:
        return []

    async def delete_backup(self, backup_id: str, business_id: uuid.UUID) -> bool:
        return True


class DummyFileBackupProvider(FileBackupProvider):
    async def create_backup(
        self,
        business_id: uuid.UUID,
        backup_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        return {"status": "success", "provider": "file", "name": backup_name}

    async def restore_backup(self, backup_id: str, business_id: uuid.UUID) -> bool:
        return True

    async def list_backups(self, business_id: uuid.UUID, limit: int = 50) -> list[Dict[str, Any]]:
        return []

    async def delete_backup(self, backup_id: str, business_id: uuid.UUID) -> bool:
        return True


class DummyCloudBackupProvider(CloudBackupProvider):
    async def create_backup(
        self,
        business_id: uuid.UUID,
        backup_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        return {"status": "success", "provider": "cloud", "name": backup_name}

    async def restore_backup(self, backup_id: str, business_id: uuid.UUID) -> bool:
        return True

    async def list_backups(self, business_id: uuid.UUID, limit: int = 50) -> list[Dict[str, Any]]:
        return []

    async def delete_backup(self, backup_id: str, business_id: uuid.UUID) -> bool:
        return True


@pytest.mark.asyncio
async def test_backup_manager_registration():
    manager = BackupManager()
    db_provider = DummyDatabaseBackupProvider()
    file_provider = DummyFileBackupProvider()
    cloud_provider = DummyCloudBackupProvider()

    manager.register_database_provider(db_provider)
    manager.register_file_provider(file_provider)
    manager.register_cloud_provider(cloud_provider)

    assert manager.database_provider == db_provider
    assert manager.file_provider == file_provider
    assert manager.cloud_provider == cloud_provider


@pytest.mark.asyncio
async def test_create_full_backup():
    manager = BackupManager()
    db_provider = DummyDatabaseBackupProvider()
    file_provider = DummyFileBackupProvider()
    cloud_provider = DummyCloudBackupProvider()

    manager.register_database_provider(db_provider)
    manager.register_file_provider(file_provider)
    manager.register_cloud_provider(cloud_provider)

    business_id = uuid.uuid4()
    backup_name = "monthly_backup"
    metadata = {"triggered_by": "system"}

    results = await manager.create_full_backup(
        business_id=business_id,
        backup_name=backup_name,
        metadata=metadata
    )

    assert results["business_id"] == str(business_id)
    assert results["name"] == backup_name
    assert results["metadata"] == metadata
    assert "database" in results["providers"]
    assert "file" in results["providers"]
    assert "cloud" in results["providers"]
    assert results["providers"]["database"]["status"] == "success"
    assert results["providers"]["file"]["status"] == "success"
    assert results["providers"]["cloud"]["status"] == "success"
