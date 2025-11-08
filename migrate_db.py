"""
Database migration script.
Run this to update the database schema with the new user_profiles table.
"""
from pathlib import Path
from src.database.user_db import init_db, engine, Base


def migrate():
    """Run database migration."""
    print("=" * 60)
    print("Database Migration")
    print("=" * 60)
    
    # Create user_images directory if it doesn't exist
    images_dir = Path("data/user_images")
    images_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n✓ Created images directory: {images_dir}")
    
    # Initialize database (creates all tables)
    print("\n✓ Initializing database tables...")
    init_db()
    
    # Verify tables exist
    print("\n✓ Verifying tables...")
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    print(f"\nExisting tables:")
    for table in tables:
        columns = inspector.get_columns(table)
        print(f"  - {table} ({len(columns)} columns)")
        for col in columns:
            print(f"    • {col['name']}: {col['type']}")
    
    print("\n" + "=" * 60)
    print("Migration completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    migrate()

