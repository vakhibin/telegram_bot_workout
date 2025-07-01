import time
from sqlalchemy import create_engine, text
from database.models import Base
from config import DATABASE_URL

sync_url = DATABASE_URL.replace('+asyncpg', '')
engine = create_engine(sync_url)
    
Base.metadata.create_all(engine)
print("Tables created:", list(Base.metadata.tables.keys()))
    
with engine.connect() as conn:
    result = conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname='public'"))
    print("Existing tables:", [row[0] for row in result])
    engine.dispose()