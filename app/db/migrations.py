"""
Database migration utilities.
"""
import os
import json
import aiosqlite
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from app.utils.logger import setup_logger
from app.utils.config import settings

logger = setup_logger("migrations")

MIGRATIONS_DIR = Path(__file__).parent / 'migrations'

async def run_migrations():
    """Run pending migrations from the migrations directory."""
    # Create migrations directory if it doesn't exist
    os.makedirs(MIGRATIONS_DIR, exist_ok=True)
    
    # Get DB path from settings
    db_path = settings.DATABASE_URL.replace("sqlite:///", "")
    
    async with aiosqlite.connect(db_path) as db:
        # Create migrations table if it doesn't exist
        await db.execute('''
        CREATE TABLE IF NOT EXISTS migrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT UNIQUE NOT NULL,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        await db.commit()
        
        # Get applied migrations
        cursor = await db.execute("SELECT filename FROM migrations")
        applied = {row[0] for row in await cursor.fetchall()}
        
        # Get available migration files
        migration_files = sorted([f for f in os.listdir(MIGRATIONS_DIR) 
                                if f.endswith('.sql') and f not in applied])
        
        if not migration_files:
            logger.info("No pending migrations.")
            return
        
        logger.info(f"Found {len(migration_files)} pending migrations.")
        
        # Apply migrations
        for filename in migration_files:
            logger.info(f"Applying migration: {filename}")
            filepath = os.path.join(MIGRATIONS_DIR, filename)
            
            try:
                # Read migration SQL
                with open(filepath, 'r') as f:
                    sql = f.read()
                
                # Execute migration
                await db.executescript(sql)
                
                # Record migration as applied
                await db.execute(
                    "INSERT INTO migrations (filename) VALUES (?)",
                    (filename,)
                )
                await db.commit()
                
                logger.info(f"Successfully applied migration: {filename}")
            except Exception as e:
                logger.error(f"Error applying migration {filename}: {str(e)}")
                await db.rollback()
                raise

async def create_migration(name: str) -> str:
    """
    Create a new migration file.
    
    Args:
        name: Migration name (will be added to filename)
        
    Returns:
        Path to the created migration file
    """
    os.makedirs(MIGRATIONS_DIR, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{timestamp}_{name}.sql"
    filepath = os.path.join(MIGRATIONS_DIR, filename)
    
    # Create empty migration file with header comment
    with open(filepath, 'w') as f:
        f.write(f"-- Migration: {name}\n")
        f.write(f"-- Created at: {datetime.now().isoformat()}\n\n")
        f.write("-- Write your migration SQL here\n\n")
    
    logger.info(f"Created new migration: {filename}")
    return filepath

async def get_migration_status() -> Dict[str, Any]:
    """
    Get the current migration status.
    
    Returns:
        Dictionary with migration status information
    """
    # Create migrations directory if it doesn't exist
    os.makedirs(MIGRATIONS_DIR, exist_ok=True)
    
    # Get DB path from settings
    db_path = settings.DATABASE_URL.replace("sqlite:///", "")
    
    async with aiosqlite.connect(db_path) as db:
        # Create migrations table if it doesn't exist
        await db.execute('''
        CREATE TABLE IF NOT EXISTS migrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT UNIQUE NOT NULL,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        await db.commit()
        
        # Get applied migrations
        cursor = await db.execute(
            "SELECT filename, applied_at FROM migrations ORDER BY applied_at"
        )
        rows = await cursor.fetchall()
        applied = [{"filename": row[0], "applied_at": row[1]} for row in rows]
        applied_filenames = {row[0] for row in rows}
        
        # Get available migration files
        available = sorted([f for f in os.listdir(MIGRATIONS_DIR) if f.endswith('.sql')])
        pending = [f for f in available if f not in applied_filenames]
        
        return {
            "applied": applied,
            "pending": pending,
            "total": len(available),
            "applied_count": len(applied),
            "pending_count": len(pending)
        }