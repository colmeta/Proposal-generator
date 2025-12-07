"""Database migration runner and management"""
import os
import sys
from pathlib import Path
from typing import List, Optional
from sqlalchemy import create_engine, text, inspect
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic.runtime.migration import MigrationContext


class MigrationRunner:
    """Manages database migrations"""
    
    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url or os.getenv('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable is required")
        
        self.engine = create_engine(self.database_url)
        self.alembic_cfg = self._get_alembic_config()
    
    def _get_alembic_config(self) -> Config:
        """Get Alembic configuration"""
        # Look for alembic.ini in project root
        project_root = Path(__file__).parent.parent.parent
        alembic_ini = project_root / 'alembic.ini'
        
        if alembic_ini.exists():
            cfg = Config(str(alembic_ini))
        else:
            # Create minimal config
            cfg = Config()
            cfg.set_main_option('script_location', str(project_root / 'alembic'))
            cfg.set_main_option('sqlalchemy.url', self.database_url)
        
        return cfg
    
    def get_current_revision(self) -> Optional[str]:
        """Get current database revision"""
        try:
            with self.engine.connect() as connection:
                context = MigrationContext.configure(connection)
                return context.get_current_revision()
        except Exception:
            return None
    
    def get_head_revision(self) -> Optional[str]:
        """Get head revision from migration scripts"""
        try:
            script = ScriptDirectory.from_config(self.alembic_cfg)
            return script.get_current_head()
        except Exception:
            return None
    
    def upgrade(self, revision: str = 'head') -> bool:
        """Run migrations up to specified revision"""
        try:
            print(f"Upgrading database to revision: {revision}")
            command.upgrade(self.alembic_cfg, revision)
            print("Migration completed successfully")
            return True
        except Exception as e:
            print(f"Migration failed: {e}")
            return False
    
    def downgrade(self, revision: str) -> bool:
        """Rollback migrations to specified revision"""
        try:
            print(f"Downgrading database to revision: {revision}")
            command.downgrade(self.alembic_cfg, revision)
            print("Rollback completed successfully")
            return True
        except Exception as e:
            print(f"Rollback failed: {e}")
            return False
    
    def get_migration_history(self) -> List[dict]:
        """Get migration history"""
        try:
            script = ScriptDirectory.from_config(self.alembic_cfg)
            history = []
            
            for script_revision in script.walk_revisions():
                history.append({
                    'revision': script_revision.revision,
                    'down_revision': script_revision.down_revision,
                    'doc': script_revision.doc,
                    'branch_labels': script_revision.branch_labels,
                })
            
            return history
        except Exception as e:
            print(f"Failed to get migration history: {e}")
            return []
    
    def validate_migrations(self) -> bool:
        """Validate that migrations are in sync"""
        current = self.get_current_revision()
        head = self.get_head_revision()
        
        if current is None and head is None:
            print("No migrations found")
            return True
        
        if current != head:
            print(f"Database is not up to date. Current: {current}, Head: {head}")
            return False
        
        print("Database is up to date")
        return True
    
    def create_migration(self, message: str, autogenerate: bool = True) -> bool:
        """Create a new migration"""
        try:
            if autogenerate:
                command.revision(
                    self.alembic_cfg,
                    message=message,
                    autogenerate=True
                )
            else:
                command.revision(
                    self.alembic_cfg,
                    message=message
                )
            print(f"Migration created: {message}")
            return True
        except Exception as e:
            print(f"Failed to create migration: {e}")
            return False


def main():
    """CLI interface for migration runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Database migration runner')
    parser.add_argument('action', choices=['upgrade', 'downgrade', 'current', 'history', 'validate', 'create'],
                       help='Migration action to perform')
    parser.add_argument('--revision', '-r', help='Revision to upgrade/downgrade to')
    parser.add_argument('--message', '-m', help='Message for new migration')
    
    args = parser.parse_args()
    
    runner = MigrationRunner()
    
    if args.action == 'upgrade':
        revision = args.revision or 'head'
        success = runner.upgrade(revision)
        sys.exit(0 if success else 1)
    
    elif args.action == 'downgrade':
        if not args.revision:
            print("Error: --revision is required for downgrade")
            sys.exit(1)
        success = runner.downgrade(args.revision)
        sys.exit(0 if success else 1)
    
    elif args.action == 'current':
        current = runner.get_current_revision()
        print(f"Current revision: {current}")
    
    elif args.action == 'history':
        history = runner.get_migration_history()
        for mig in history:
            print(f"{mig['revision']}: {mig['doc']}")
    
    elif args.action == 'validate':
        valid = runner.validate_migrations()
        sys.exit(0 if valid else 1)
    
    elif args.action == 'create':
        if not args.message:
            print("Error: --message is required for create")
            sys.exit(1)
        success = runner.create_migration(args.message)
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()



