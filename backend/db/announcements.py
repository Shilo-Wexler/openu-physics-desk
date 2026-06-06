"""
Announcements database module.

Provides functions for creating and retrieving announcements.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import mysql.connector

from db.connection import get_connection
from logger import get_logger


logger = get_logger(__name__)


def create_announcement(title: str, content: str) -> int:
    """
    Inserts a new announcement into the database.

    Args:
        title: the announcement title.
        content: the announcement content.

    Returns:
        The id of the newly created announcement.

    Raises:
        ValueError: if title or content are empty or whitespace only.
        mysql.connector.Error: if the database query fails.
    """
    if not title or not title.strip():
        logger.warning("create_announcement called with empty title")
        raise ValueError("title is a required field.")

    if not content or not content.strip():
        logger.warning("create_announcement called with empty content")
        raise ValueError("content is a required field.")
    
    if len(title.strip()) > 100:
        logger.warning("create_announcement called with title exceeding limit")
        raise ValueError("title exceeds maximum length of 150 characters.")

    if len(content.strip()) > 2250:
        logger.warning("create_announcement called with content exceeding limit")
        raise ValueError("content exceeds maximum length of 1000 characters.")

    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO announcements (title, content)
            VALUES (%s, %s)
            """,
            (title, content)
        )
        connection.commit()
        new_id = cursor.lastrowid
        logger.debug("New announcement created with id: %s", new_id)
        return new_id
    except mysql.connector.Error as e:
        logger.error("Failed to insert announcement: %s", e)
        raise
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def get_announcements(limit: int | None = None) -> list[dict]:
    """
    Fetches announcements from the database ordered by most recent.

    Args:
        limit: maximum number of announcements to return.
               Defaults to 1 (most recent only).

    Returns:
        A list of dicts with keys: id, title, content, created_at.

    Raises:
        ValueError: if limit is not a positive integer.
        mysql.connector.Error: if the database query fails.
    """
    if limit is None:
        limit = 1

    if not isinstance(limit, int) or limit < 1:
        logger.warning("get_announcements called with invalid limit: %s", limit)
        raise ValueError("limit must be a positive integer.")

    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT id, title, content, created_at
            FROM announcements
            ORDER BY created_at DESC
            LIMIT %s
            """,
            (limit,)
        )
        announcements = cursor.fetchall()
        logger.debug("Fetched %s announcements", len(announcements))
        return announcements
    except mysql.connector.Error as e:
        logger.error("Failed to fetch announcements: %s", e)
        raise
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()