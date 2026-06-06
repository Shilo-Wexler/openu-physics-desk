"""
Database connection module.

Provides a single function to establish a MySQL connection
using environment variables defined in .env.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import mysql.connector
from dotenv import load_dotenv

from logger import get_logger


load_dotenv()

logger = get_logger(__name__)


def get_connection() -> mysql.connector.MySQLConnection:
    """
    Opens and returns a new MySQL database connection using environment variables.

    Returns:
        A MySQL connection object.

    Raises:
        ValueError: if required environment variables are missing.
        mysql.connector.Error: if the connection fails.
    """
    db_host = os.getenv("DB_HOST", "127.0.0.1")
    db_port = int(os.getenv("DB_PORT", "3306"))
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_name = os.getenv("DB_NAME")
    db_charset = os.getenv("DB_CHARSET", "utf8mb4")

    if not db_user or not db_password or not db_name:
        logger.critical(
            "Server startup failed: Missing critical database "
            "credentials (.env is missing or incomplete)."
        )
        raise ValueError("Database credentials are not fully configured.")

    try:
        connection = mysql.connector.connect(
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_password,
            charset=db_charset
        )
        logger.debug("Database connection established successfully")
        return connection
    except mysql.connector.Error as e:
        logger.error("Failed to connect to database: %s", e)
        raise