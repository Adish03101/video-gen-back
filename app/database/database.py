from sqlmodel import SQLModel, create_engine, Session

# This sets the file name. It will appear in your project root.
sqlite_file_name = "story_database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

# check_same_thread=False is required for SQLite when using FastAPI
connect_args = {"check_same_thread": False}

# The Engine is the connection factory
engine = create_engine(sqlite_url, connect_args=connect_args)

def create_db_and_tables():
    """Creates the tables if they don't exist yet."""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Dependency for FastAPI Routes to get a DB session."""
    with Session(engine) as session:
        yield session