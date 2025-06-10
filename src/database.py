from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Define the database URL for SQLite.
# The database will be created in the same directory as the main script.
SQLALCHEMY_DATABASE_URL = "sqlite:///./burn_after_reading.db"

# Create the SQLAlchemy engine.
# The `connect_args` is needed only for SQLite to allow multi-threaded interaction.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Create a SessionLocal class. Each instance of this class will be a database session.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a Base class. Our ORM models will inherit from this class.
Base = declarative_base() 