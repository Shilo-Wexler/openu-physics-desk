import os

import mysql.connector
from dotenv import load_dotenv

from logger import get_logger


load_dotenv()

logger = get_logger(__name__)

VALID_CATEGORIES = {"books", "exams", "lecturers", "other"}


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
        logger.error("Failed to connect to database: %s", e)
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
        logger.debug("Fetched %s courses from database", len(courses))
        return courses
    except mysql.connector.Error as e:
        logger.error("Failed to fetch courses: %s", e)
        raise
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def create_inquiry(
    category: str,
    message: str,
    course_id: int | None = None,
    email: str | None = None,
    phone: str | None = None
) -> int:
    """
    Inserts a new student inquiry into the database.

    Args:
        category: one of 'books', 'exams', 'lecturers', 'other'.
        message: the student's message content.
        course_id: optional reference to a course id.
        email: optional contact email.
        phone: optional contact phone number.

    Returns:
        The id of the newly created inquiry record.

    Raises:
        ValueError: if category/message are missing/empty, or if category is invalid.
        mysql.connector.Error: if the database query fails.
    """
    if not category or not category.strip() or not message or not message.strip():
        logger.warning("create_inquiry called with missing or whitespace-only required fields")
        raise ValueError("category and message are required fields.")

    if category not in VALID_CATEGORIES:
        logger.warning("create_inquiry called with invalid category: %s", category)
        raise ValueError(f"Invalid category: {category}")

    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO contacts (category, message, course_id, email, phone)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (category, message, course_id, email, phone)
        )
        connection.commit()
        new_id = cursor.lastrowid
        logger.debug("New inquiry created with id: %s", new_id)
        return new_id
    except mysql.connector.Error as e:
        logger.error("Failed to insert inquiry: %s", e)
        raise
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()