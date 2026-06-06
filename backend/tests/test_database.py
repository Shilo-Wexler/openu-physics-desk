"""
Tests for database.py — get_connection() function.
"""

import os
import logging
import unittest
from unittest.mock import patch

import mysql.connector

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import get_connection, get_all_courses, create_inquiry


class TestGetConnection(unittest.TestCase):

    def setUp(self):
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        logging.disable(logging.NOTSET)

    def test_successful_connection(self):
        """Test that a valid connection is returned with correct credentials."""
        connection = get_connection()
        self.assertIsNotNone(connection)
        self.assertTrue(connection.is_connected())
        connection.close()

    def test_missing_db_user(self):
        """Test that ValueError is raised when DB_USER is missing."""
        with patch.dict(os.environ, {"DB_USER": ""}):
            with self.assertRaises(ValueError):
                get_connection()

    def test_missing_db_password(self):
        """Test that ValueError is raised when DB_PASSWORD is missing."""
        with patch.dict(os.environ, {"DB_PASSWORD": ""}):
            with self.assertRaises(ValueError):
                get_connection()

    def test_missing_db_name(self):
        """Test that ValueError is raised when DB_NAME is missing."""
        with patch.dict(os.environ, {"DB_NAME": ""}):
            with self.assertRaises(ValueError):
                get_connection()

    def test_wrong_password(self):
        """Test that mysql.connector.Error is raised with wrong password."""
        with patch.dict(os.environ, {"DB_PASSWORD": "wrong_password"}):
            with self.assertRaises(mysql.connector.Error):
                get_connection()
    
    def test_invalid_db_port(self):
        """Test that ValueError is raised when DB_PORT is not a valid integer."""
        with patch.dict(os.environ, {"DB_PORT": "not_a_number"}):
            with self.assertRaises(ValueError):
                get_connection()


class TestGetAllCourses(unittest.TestCase):

    def setUp(self):
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        logging.disable(logging.NOTSET)

    def test_returns_list(self):
        """Test that get_all_courses returns a list."""
        courses = get_all_courses()
        self.assertIsInstance(courses, list)

    def test_returns_non_empty_list(self):
        """Test that get_all_courses returns at least one course."""
        courses = get_all_courses()
        self.assertGreater(len(courses), 0)

    def test_course_structure(self):
        """Test that each course has the required keys."""
        courses = get_all_courses()
        for course in courses:
            self.assertIn("id", course)
            self.assertIn("course_num", course)
            self.assertIn("course_name", course)

    def test_course_values_not_empty(self):
        """Test that course fields are not empty."""
        courses = get_all_courses()
        for course in courses:
            self.assertIsNotNone(course["id"])
            self.assertTrue(len(course["course_num"]) > 0)
            self.assertTrue(len(course["course_name"]) > 0)

    def test_raises_on_db_failure(self):
        """Test that mysql.connector.Error is raised on database failure."""
        with patch.dict(os.environ, {"DB_NAME": "nonexistent_db"}):
            with self.assertRaises(mysql.connector.Error):
                get_all_courses()
    
    def test_raises_value_error_on_missing_credentials(self):
        """Test that ValueError bubbles up when credentials are missing."""
        with patch.dict(os.environ, {"DB_USER": ""}):
            with self.assertRaises(ValueError):
                get_all_courses()


class TestCreateInquiry(unittest.TestCase):

    def setUp(self):
        logging.disable(logging.CRITICAL)
        self.created_id = None

    def tearDown(self):
        logging.disable(logging.NOTSET)
        if self.created_id:
            connection = get_connection()
            cursor = connection.cursor()
            cursor.execute("DELETE FROM contacts WHERE id = %s", (self.created_id,))
            connection.commit()
            cursor.close()
            connection.close()

    def test_successful_creation(self):
        """Test that a valid inquiry returns a positive integer id."""
        self.created_id = create_inquiry(
            category="exams",
            message="The exam schedule is unclear."
        )
        self.assertIsInstance(self.created_id, int)
        self.assertGreater(self.created_id, 0)

    def test_with_all_optional_fields(self):
        """Test that inquiry is created successfully with all optional fields."""
        self.created_id = create_inquiry(
            category="books",
            message="The book is missing chapters.",
            course_id=1,
            email="test@test.com",
            phone="0501234567"
        )
        self.assertIsInstance(self.created_id, int)
        self.assertGreater(self.created_id, 0)

    def test_with_none_optional_fields(self):
        """Test that inquiry is created successfully with None optional fields."""
        self.created_id = create_inquiry(
            category="other",
            message="General feedback.",
            course_id=None,
            email=None,
            phone=None
        )
        self.assertIsInstance(self.created_id, int)
        self.assertGreater(self.created_id, 0)

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

    def test_raises_on_db_failure(self):
        """Test that mysql.connector.Error is raised on database failure."""
        with patch.dict(os.environ, {"DB_NAME": "nonexistent_db"}):
            with self.assertRaises(mysql.connector.Error):
                create_inquiry(category="exams", message="Some message.")


if __name__ == "__main__":
    unittest.main()