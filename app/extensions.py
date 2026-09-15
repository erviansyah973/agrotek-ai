"""
AGROTEK AI — Flask Extensions
=============================
Instance SQLAlchemy terpisah supaya bisa diimport dari
models.py tanpa circular import.
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()