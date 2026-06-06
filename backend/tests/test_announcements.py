"""
Tests for db/announcements.py — create_announcement() and get_announcements() functions.
"""

import logging
import os
import sys
import unittest
from unittest.mock import patch

import mysql.connector

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db import get_connection, create_announcement, get_announcements


class TestCreateAnnouncement(unittest.TestCase):

    def setUp(self):
        logging.disable(logging.CRITICAL)
        self.created_ids = []

    def tearDown(self):
        logging.disable(logging.NOTSET)
        if self.created_ids:
            connection = None
            cursor = None
            try:
                connection = get_connection()
                cursor = connection.cursor()
                for record_id in self.created_ids:
                    cursor.execute(
                        "DELETE FROM announcements WHERE id = %s", (record_id,)
                    )
                connection.commit()
            finally:
                if cursor:
                    cursor.close()
                if connection:
                    connection.close()

    def test_successful_creation(self):
        """Test that a valid announcement returns a positive integer id."""
        new_id = create_announcement(
            title="Test Title",
            content="Test content for announcement."
        )
        self.created_ids.append(new_id)
        self.assertIsInstance(new_id, int)
        self.assertGreater(new_id, 0)

    def test_empty_title_raises_value_error(self):
        """Test that empty title raises ValueError."""
        with self.assertRaises(ValueError):
            create_announcement(title="", content="Some content.")

    def test_whitespace_title_raises_value_error(self):
        """Test that whitespace-only title raises ValueError."""
        with self.assertRaises(ValueError):
            create_announcement(title="   ", content="Some content.")

    def test_empty_content_raises_value_error(self):
        """Test that empty content raises ValueError."""
        with self.assertRaises(ValueError):
            create_announcement(title="Test Title", content="")

    def test_whitespace_content_raises_value_error(self):
        """Test that whitespace-only content raises ValueError."""
        with self.assertRaises(ValueError):
            create_announcement(title="Test Title", content="   ")

    def test_title_too_long_raises_value_error(self):
        """Test that title exceeding 100 characters raises ValueError."""
        with self.assertRaises(ValueError):
            create_announcement(title="א" * 101, content="Some content.")

    def test_content_too_long_raises_value_error(self):
        """Test that content exceeding 2250 characters raises ValueError."""
        with self.assertRaises(ValueError):
            create_announcement(title="Test Title", content="א" * 2251)

    def test_raises_on_db_failure(self):
        """Test that mysql.connector.Error is raised on database failure."""
        with patch.dict(os.environ, {"DB_NAME": "nonexistent_db"}):
            with self.assertRaises(mysql.connector.Error):
                create_announcement(title="Test", content="Test content.")


class TestGetAnnouncements(unittest.TestCase):

    def setUp(self):
        logging.disable(logging.CRITICAL)
        self.created_ids = []

    def tearDown(self):
        logging.disable(logging.NOTSET)
        if self.created_ids:
            connection = None
            cursor = None
            try:
                connection = get_connection()
                cursor = connection.cursor()
                for record_id in self.created_ids:
                    cursor.execute(
                        "DELETE FROM announcements WHERE id = %s", (record_id,)
                    )
                connection.commit()
            finally:
                if cursor:
                    cursor.close()
                if connection:
                    connection.close()

    def test_returns_list(self):
        """Test that get_announcements returns a list."""
        result = get_announcements()
        self.assertIsInstance(result, list)

    def test_default_limit_is_one(self):
        """Test that default limit returns at most 1 announcement."""
        new_id = create_announcement(title="Test", content="Test content.")
        self.created_ids.append(new_id)
        result = get_announcements()
        self.assertLessEqual(len(result), 1)

    def test_custom_limit(self):
        """Test that custom limit is respected."""
        for i in range(3):
            new_id = create_announcement(title=f"Test {i}", content="Content.")
            self.created_ids.append(new_id)
        result = get_announcements(limit=3)
        self.assertLessEqual(len(result), 3)

    def test_announcement_structure(self):
        """Test that each announcement has the required keys."""
        new_id = create_announcement(title="Test", content="Test content.")
        self.created_ids.append(new_id)
        result = get_announcements()
        if result:
            announcement = result[0]
            self.assertIn("id", announcement)
            self.assertIn("title", announcement)
            self.assertIn("content", announcement)
            self.assertIn("created_at", announcement)

    def test_invalid_limit_raises_value_error(self):
        """Test that limit=0 raises ValueError."""
        with self.assertRaises(ValueError):
            get_announcements(limit=0)

    def test_negative_limit_raises_value_error(self):
        """Test that negative limit raises ValueError."""
        with self.assertRaises(ValueError):
            get_announcements(limit=-1)

    def test_raises_on_db_failure(self):
        """Test that mysql.connector.Error is raised on database failure."""
        with patch.dict(os.environ, {"DB_NAME": "nonexistent_db"}):
            with self.assertRaises(mysql.connector.Error):
                get_announcements()


if __name__ == "__main__":
    unittest.main()