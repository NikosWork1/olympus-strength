import os
from alembic.config import Config
from alembic import command

# Get the directory of the current script
dir_path = os.path.dirname(os.path.realpath(__file__))

# Create Alembic configuration
alembic_cfg = Config(os.path.join(dir_path, "alembic.ini"))

# Run the upgrade command to apply all migrations
command.upgrade(alembic_cfg, "head")

print("Migrations successfully applied!")