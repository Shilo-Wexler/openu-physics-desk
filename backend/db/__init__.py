"""
Database package for openu-physics-desk.

Exposes all public database functions for use by the application.
"""

from db.connection import get_connection
from db.courses import get_all_courses, VALID_CATEGORIES
from db.inquiries import create_inquiry, get_inquiries