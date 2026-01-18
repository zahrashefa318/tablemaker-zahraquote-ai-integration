import pytest
from app.db.session import engine, Base

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """
    Automatically create all tables for the test database.
    Runs once per test session.
    """
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
