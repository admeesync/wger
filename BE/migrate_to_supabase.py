import os
import sys
from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import sessionmaker

# Add the current directory to sys.path so we can import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.session import Base
from settings.settings import settings
import models  # This registers all models on Base

# Define connection URLs
SQLITE_URL = "sqlite:///wger.db"
POSTGRES_URL = settings.database_url

if POSTGRES_URL.startswith("postgres://"):
    POSTGRES_URL = POSTGRES_URL.replace("postgres://", "postgresql://", 1)

print(f"Connecting to SQLite: {SQLITE_URL}")
sqlite_engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
SQLiteSession = sessionmaker(bind=sqlite_engine)
sqlite_session = SQLiteSession()

print(f"Connecting to Supabase (Postgres): {POSTGRES_URL}")
postgres_engine = create_engine(POSTGRES_URL)
PostgresSession = sessionmaker(bind=postgres_engine)
postgres_session = PostgresSession()

def migrate():
    # 1. Create tables in Postgres
    print("Creating tables in Supabase Postgres...")
    Base.metadata.create_all(bind=postgres_engine)
    print("Tables created successfully.")

    # Disable constraints temporarily or migrate in dependency order
    # Base.metadata.sorted_tables gives them in dependency order (foreign keys last)
    tables = Base.metadata.sorted_tables
    print(f"Found {len(tables)} tables to migrate in dependency order:")
    for table in tables:
        print(f" - {table.name}")

    for table in tables:
        print(f"\nMigrating table: {table.name}...")
        
        # Get the corresponding model class
        model_class = None
        for mapper in Base.registry.mappers:
            if mapper.local_table == table:
                model_class = mapper.class_
                break
        
        if not model_class:
            print(f"No model class found for table {table.name}, skipping direct model migration.")
            continue
            
        # Get all records from SQLite
        records = sqlite_session.query(model_class).all()
        print(f"Found {len(records)} records in SQLite.")
        
        if not records:
            continue

        # Clear existing data in Postgres table to avoid duplicate primary key errors
        print(f"Clearing existing data in Postgres table '{table.name}'...")
        postgres_session.execute(text(f"TRUNCATE TABLE {table.name} RESTART IDENTITY CASCADE;"))
        postgres_session.commit()

        # Copy records
        for record in records:
            # Clone the record attributes
            attrs = {col.name: getattr(record, col.name) for col in table.columns}
            new_record = model_class(**attrs)
            postgres_session.add(new_record)
            
        try:
            postgres_session.commit()
            print(f"Successfully migrated {len(records)} records to '{table.name}'.")
        except Exception as e:
            postgres_session.rollback()
            print(f"Error migrating table {table.name}: {e}")
            
        # Reset serial sequence in Postgres if the table has an 'id' serial column
        if 'id' in [col.name for col in table.columns]:
            try:
                print(f"Resetting serial sequence for table '{table.name}'...")
                # pg_get_serial_sequence returns None or name of sequence
                seq_query = text(f"SELECT pg_get_serial_sequence('{table.name}', 'id');")
                seq_name = postgres_session.execute(seq_query).scalar()
                if seq_name:
                    reset_query = text(f"SELECT setval('{seq_name}', COALESCE((SELECT MAX(id) FROM {table.name}), 1));")
                    postgres_session.execute(reset_query)
                    postgres_session.commit()
                    print(f"Sequence reset for '{table.name}'.")
            except Exception as seq_err:
                postgres_session.rollback()
                print(f"Could not reset sequence for {table.name}: {seq_err}")

    print("\nMigration completed successfully!")

if __name__ == "__main__":
    migrate()
