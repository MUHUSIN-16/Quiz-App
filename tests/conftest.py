"""Shared test configuration.

Unit tests replace database collections with fakes, so they must never require
the developer's Atlas credentials or a reachable MongoDB server during import.
"""
import os


os.environ["MONGO_URL"] = "mongodb://localhost:27017"
os.environ["MONGO_DBNAME"] = "quiz_app_test"
