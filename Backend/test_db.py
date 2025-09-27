import asyncio
from databases import Database
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Boolean

DATABASE_URL = "sqlite:///./test.db"

# Define the database and metadata
database = Database(DATABASE_URL)
metadata = MetaData()

# Define a sample table
tasks = Table(
    "tasks",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String),
    Column("description", String),
    Column("completed", Boolean, default=False),
)

# Create the SQLite database and table
engine = create_engine(DATABASE_URL)
metadata.create_all(engine)

async def test_db():
    await database.connect()
    # Insert a test task
    query = tasks.insert().values(title="Test Task", description="This is a test.", completed=False)
    task_id = await database.execute(query)
    print(f"Inserted task with id: {task_id}")

    # Fetch tasks
    query = tasks.select()
    rows = await database.fetch_all(query)
    for row in rows:
        print(row)

    await database.disconnect()

if __name__ == "__main__":
    asyncio.run(test_db())
