"""
Tests for db/courses.py — get_all_courses() function.
"""

import logging
import os
import sys
import unittest
from unittest.mock import patch

import mysql.connector

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db import get_all_courses


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
        """Test that ValueError is raised when credentials are missing."""
        with patch.dict(os.environ, {"DB_USER": ""}):
            with self.assertRaises(ValueError):
                get_all_courses()


if __name__ == "__main__":
    unittest.main()