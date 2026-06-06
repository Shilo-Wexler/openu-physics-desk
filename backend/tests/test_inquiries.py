"""
Tests for db/inquiries.py — create_inquiry() and get_inquiries() functions.
"""

import logging
import os
import sys
import unittest
from unittest.mock import patch

import mysql.connector

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db import get_connection, create_inquiry, get_inquiries


class TestCreateInquiry(unittest.TestCase):

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
                    cursor.execute("DELETE FROM contacts WHERE id = %s", (record_id,))
                connection.commit()
            finally:
                if cursor:
                    cursor.close()
                if connection:
                    connection.close()

    def test_successful_creation(self):
        """Test that a valid inquiry returns a positive integer id."""
        new_id = create_inquiry(category="exams", message="The exam schedule is unclear.")
        self.created_ids.append(new_id)
        self.assertIsInstance(new_id, int)
        self.assertGreater(new_id, 0)

    def test_with_all_optional_fields(self):
        """Test that inquiry is created successfully with all optional fields."""
        new_id = create_inquiry(
            category="books",
            message="The book is missing chapters.",
            course_id=1,
            email="test@test.com",
            phone="0501234567"
        )
        self.created_ids.append(new_id)
        self.assertIsInstance(new_id, int)
        self.assertGreater(new_id, 0)

    def test_with_none_optional_fields(self):
        """Test that inquiry is created successfully with None optional fields."""
        new_id = create_inquiry(
            category="other",
            message="General feedback.",
            course_id=None,
            email=None,
            phone=None
        )
        self.created_ids.append(new_id)
        self.assertIsInstance(new_id, int)
        self.assertGreater(new_id, 0)

    def test_empty_category_raises_value_error(self):
        """Test that empty category raises ValueError."""
        with self.assertRaises(ValueError):
            create_inquiry(category="", message="Some message.")

    def test_empty_message_raises_value_error(self):
        """Test that empty message raises ValueError."""
        with self.assertRaises(ValueError):
            create_inquiry(category="exams", message="")

    def test_whitespace_category_raises_value_error(self):
        """Test that whitespace-only category raises ValueError."""
        with self.assertRaises(ValueError):
            create_inquiry(category="   ", message="Some message.")

    def test_whitespace_message_raises_value_error(self):
        """Test that whitespace-only message raises ValueError."""
        with self.assertRaises(ValueError):
            create_inquiry(category="exams", message="   ")

    def test_invalid_category_raises_value_error(self):
        """Test that invalid category raises ValueError."""
        with self.assertRaises(ValueError):
            create_inquiry(category="invalid", message="Some message.")

    def test_message_too_long_raises_value_error(self):
        """Test that message exceeding 1500 characters raises ValueError."""
        with self.assertRaises(ValueError):
            create_inquiry(category="exams", message="א" * 1501)

    def test_raises_on_db_failure(self):
        """Test that mysql.connector.Error is raised on database failure."""
        with patch.dict(os.environ, {"DB_NAME": "nonexistent_db"}):
            with self.assertRaises(mysql.connector.Error):
                create_inquiry(category="exams", message="Some message.")


class TestGetInquiries(unittest.TestCase):

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
                    cursor.execute("DELETE FROM contacts WHERE id = %s", (record_id,))
                connection.commit()
            finally:
                if cursor:
                    cursor.close()
                if connection:
                    connection.close()

    def test_returns_list(self):
        """Test that get_inquiries returns a list."""
        result = get_inquiries()
        self.assertIsInstance(result, list)

    def test_returns_empty_list_for_future_month(self):
        """Test that a past month with no data returns empty list."""
        result = get_inquiries(month=1, year=2025)
        self.assertEqual(result, [])

    def test_inquiry_structure(self):
        """Test that each inquiry has the required keys."""
        new_id = create_inquiry(category="exams", message="test message for structure check")
        self.created_ids.append(new_id)
        result = get_inquiries()
        if result:
            inquiry = result[0]
            self.assertIn("id", inquiry)
            self.assertIn("category", inquiry)
            self.assertIn("message", inquiry)
            self.assertIn("email", inquiry)
            self.assertIn("phone", inquiry)
            self.assertIn("created_at", inquiry)
            self.assertIn("course_num", inquiry)
            self.assertIn("course_name", inquiry)

    def test_filter_by_valid_category(self):
        """Test filtering by a valid category returns only matching inquiries."""
        new_id = create_inquiry(category="books", message="books test message")
        self.created_ids.append(new_id)
        result = get_inquiries(category="books")
        self.assertIsInstance(result, list)
        for inquiry in result:
            self.assertEqual(inquiry["category"], "books")

    def test_invalid_month_raises_value_error(self):
        """Test that invalid month raises ValueError."""
        with self.assertRaises(ValueError):
            get_inquiries(month=13)

    def test_zero_month_raises_value_error(self):
        """Test that month=0 raises ValueError."""
        with self.assertRaises(ValueError):
            get_inquiries(month=0)

    def test_invalid_year_raises_value_error(self):
        """Test that invalid year raises ValueError."""
        with self.assertRaises(ValueError):
            get_inquiries(year=1999)

    def test_invalid_category_raises_value_error(self):
        """Test that invalid category raises ValueError."""
        with self.assertRaises(ValueError):
            get_inquiries(category="invalid")

    def test_raises_on_db_failure(self):
        """Test that mysql.connector.Error is raised on database failure."""
        with patch.dict(os.environ, {"DB_NAME": "nonexistent_db"}):
            with self.assertRaises(mysql.connector.Error):
                get_inquiries()


if __name__ == "__main__":
    unittest.main()