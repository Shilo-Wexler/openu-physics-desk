"""
Courses database module.

Provides functions for retrieving course data from the database.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import mysql.connector

from db.connection import get_connection
from logger import get_logger


logger = get_logger(__name__)

VALID_CATEGORIES = {"books", "exams", "lecturers", "other"}


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