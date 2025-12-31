#!/usr/bin/env python3
"""
Database initialization script for deployment.
This script ensures the database exists, is migrated, and is seeded with default data.
Safe to run multiple times (idempotent).
"""

import sys
import os

# Add the current directory to the path so we can import models
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import init_db

def main():
    """Initialize the database"""
    try:
        print("Initializing database...")
        init_db()
        print("✅ Database initialization complete")
        return 0
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
