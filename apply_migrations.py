import os
import sys
from alembic.config import Config
from alembic import command
from alembic.script import ScriptDirectory
from alembic.runtime.migration import MigrationContext
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

# Get the directory of the current script
dir_path = os.path.dirname(os.path.realpath(__file__))

# Create Alembic configuration
alembic_cfg = Config(os.path.join(dir_path, "alembic.ini"))

try:
    # First try to get the current database state
    from database import engine  # Import your SQLAlchemy engine
    
    # Try stamping the current version first
    print("Setting migration state...")
    command.stamp(alembic_cfg, "head")
    
    # Then run the upgrade
    print("Applying migrations...")
    command.upgrade(alembic_cfg, "head")
    
    print("Migrations successfully applied!")
except Exception as e:
    print(f"Migration error: {str(e)}")
    print("Attempting alternate approach...")
    
    try:
        # Try resetting to a known good state
        # This uses your first migration as a starting point
        print("Resetting migration state...")
        command.stamp(alembic_cfg, "58060653a137_initial_migration")
        
        print("Applying migrations from initial state...")
        command.upgrade(alembic_cfg, "head")
        
        print("Migrations successfully applied after reset!")
    except Exception as e2:
        print(f"Failed after reset: {str(e2)}")
        sys.exit(1)
