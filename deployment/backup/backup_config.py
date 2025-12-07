"""Backup configuration and scheduling"""
import os
from typing import Dict, Any, List
from dataclasses import dataclass
from enum import Enum


class BackupType(Enum):
    """Backup types"""
    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"


@dataclass
class BackupSchedule:
    """Backup schedule configuration"""
    name: str
    backup_type: BackupType
    schedule: str  # Cron expression
    retention_days: int
    enabled: bool = True


class BackupConfig:
    """Backup configuration manager"""
    
    def __init__(self):
        self.backup_dir = os.getenv('BACKUP_DIR', './deployment/backup')
        self.retention_days = int(os.getenv('BACKUP_RETENTION_DAYS', '30'))
        self.schedules: List[BackupSchedule] = []
        self._load_default_schedules()
    
    def _load_default_schedules(self):
        """Load default backup schedules"""
        self.schedules = [
            BackupSchedule(
                name='daily_full',
                backup_type=BackupType.FULL,
                schedule='0 2 * * *',  # 2 AM daily
                retention_days=30,
                enabled=True
            ),
            BackupSchedule(
                name='hourly_incremental',
                backup_type=BackupType.INCREMENTAL,
                schedule='0 * * * *',  # Every hour
                retention_days=7,
                enabled=True
            ),
        ]
    
    def get_schedules(self) -> List[BackupSchedule]:
        """Get all backup schedules"""
        return [s for s in self.schedules if s.enabled]
    
    def add_schedule(self, schedule: BackupSchedule):
        """Add a backup schedule"""
        self.schedules.append(schedule)
    
    def get_config(self) -> Dict[str, Any]:
        """Get backup configuration"""
        return {
            'backup_dir': self.backup_dir,
            'retention_days': self.retention_days,
            'schedules': [
                {
                    'name': s.name,
                    'type': s.backup_type.value,
                    'schedule': s.schedule,
                    'retention_days': s.retention_days,
                    'enabled': s.enabled
                }
                for s in self.schedules
            ]
        }



