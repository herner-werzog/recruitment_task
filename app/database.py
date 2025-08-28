import os
import psycopg
from fastapi import Depends

DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    with psycopg.connect(DATABASE_URL) as conn:
        yield conn


DB = Depends(get_connection)
