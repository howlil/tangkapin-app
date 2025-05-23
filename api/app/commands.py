# Run this migration script to add missing columns
# migrate.py

import os
import sys
import traceback

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from flask import Flask
from app.models import db
from sqlalchemy import text
from config import Config

def run_migration(app):
    """Add missing columns to users table"""
    with app.app_context():
        try:
            # Check if columns exist, if not add them
            with db.engine.connect() as conn:
                # Check if longitude column exists
                result = conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='users' AND column_name='longitude'
                """))
                
                if not result.fetchone():
                    print("Adding longitude column...")
                    conn.execute(text("ALTER TABLE users ADD COLUMN longitude VARCHAR(20)"))
                    conn.commit()
                
                # Check if latitude column exists
                result = conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='users' AND column_name='latitude'
                """))
                
                if not result.fetchone():
                    print("Adding latitude column...")
                    conn.execute(text("ALTER TABLE users ADD COLUMN latitude VARCHAR(20)"))
                    conn.commit()
                
                print("✅ Migration completed successfully!")
                
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            traceback.print_exc()
            
if __name__ == "__main__":
    from app import create_app
    app = create_app()
    run_migration(app)