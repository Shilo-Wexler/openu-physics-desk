import os

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
            password=db_password
        )
        logger.debug("Database connection established successfully")
        return connection
    except mysql.connector.Error as e:
        logger.error(f"Failed to connect to database: {e}")
        raise


def get_all_courses() -> list[dict]:
    """
    Fetches all courses from the database.

    Returns:
        A list of dicts with keys: id, course_num, course_name.

    Raises:
        mysql.connector.Error: if the database query fails.
    """
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT id, course_num, course_name FROM courses")
        courses = cursor.fetchall()
        logger.debug(f"Fetched {len(courses)} courses from database")
        return courses
    except mysql.connector.Error as e:
        logger.error(f"Failed to fetch courses: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()