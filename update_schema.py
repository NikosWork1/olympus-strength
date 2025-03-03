# update_schema.py
from database import engine
import models

# Run this to update your database schema
if __name__ == "__main__":
    print("Updating database schema...")
    models.Base.metadata.create_all(bind=engine)
    print("Schema updated successfully!")