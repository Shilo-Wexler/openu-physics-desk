"""
Tests for database.py — get_connection() function.
"""

import os
import unittest
from unittest.mock import patch

import mysql.connector

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import get_connection


class TestGetConnection(unittest.TestCase):

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


if __name__ == "__main__":
    unittest.main()