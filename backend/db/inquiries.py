"""
Inquiries database module.

Provides functions for creating and retrieving student inquiries.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import mysql.connector
from datetime import datetime

from db.connection import get_connection
from db.courses import VALID_CATEGORIES
from logger import get_logger


logger = get_logger(__name__)


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
        raise ValueError("Invalid category: %s" % category)

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


def get_inquiries(
    month: int | None = None,
    year: int | None = None,
    category: str | None = None
) -> list[dict]:
    """
    Fetches inquiries from the database with optional filters.
    Defaults to current month and year if not specified.

    Args:
        month: month number (1-12). Defaults to current month.
        year: full year (e.g. 2026). Defaults to current year.
        category: one of 'books', 'exams', 'lecturers', 'other'. Optional.

    Returns:
        A list of dicts with inquiry data including course name.

    Raises:
        ValueError: if category is invalid or month/year are out of range.
        mysql.connector.Error: if the database query fails.
    """
    now = datetime.now()
    month = month if month is not None else now.month
    year = year if year is not None else now.year

    if not (1 <= month <= 12):
        logger.warning("get_inquiries called with invalid month: %s", month)
        raise ValueError("month must be between 1 and 12.")

    if year < 2000 or year > 2100:
        logger.warning("get_inquiries called with invalid year: %s", year)
        raise ValueError("year is out of valid range.")

    if category and category not in VALID_CATEGORIES:
        logger.warning("get_inquiries called with invalid category: %s", category)
        raise ValueError("Invalid category: %s" % category)

    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT
                c.id,
                c.category,
                c.message,
                c.email,
                c.phone,
                c.created_at,
                co.course_num,
                co.course_name
            FROM contacts c
            LEFT JOIN courses co ON c.course_id = co.id
            WHERE MONTH(c.created_at) = %s
            AND YEAR(c.created_at) = %s
        """
        params = [month, year]

        if category:
            query += " AND c.category = %s"
            params.append(category)

        query += " ORDER BY c.created_at DESC"

        cursor.execute(query, params)
        inquiries = cursor.fetchall()
        logger.debug("Fetched %s inquiries for %s/%s", len(inquiries), month, year)
        return inquiries
    except mysql.connector.Error as e:
        logger.error("Failed to fetch inquiries: %s", e)
        raise
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()