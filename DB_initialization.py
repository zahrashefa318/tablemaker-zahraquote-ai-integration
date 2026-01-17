
from sqlalchemy import create_engine,text
import datetime
from app.db.tableModels import Idempotency_key_storage
from app.db.session import Base

MYSQL_SERVER_URL="mysql+pymysql://zahraAPI:123@127.0.0.1:3306/"
def intitialize_DB(DbName:str="ZDB"):
    engine=create_engine(MYSQL_SERVER_URL,echo=True)
    with engine.connect() as conn:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {DbName}"))

    DB_URL=f"{MYSQL_SERVER_URL}{DbName}"
    engine2=create_engine(DB_URL, echo=True)
    Base.metadata.create_all(bind=engine2)

if __name__=="__main__": # { we restrict that the script should run in the same module if somebody imports the file so the script should not run}to allow standalone execution of this script not for import only.
    intitialize_DB()

