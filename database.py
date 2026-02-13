import mysql.connector
from mysql.connector import pooling
import os
import logging
from dotenv import load_dotenv

load_dotenv()

# Database Configuration
db_config = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "port": int(os.getenv("DB_PORT", 3306)),
}

# Add SSL for Cloud Providers (Aiven, AWS, etc.)
if db_config["host"] != "localhost":
    db_config["ssl_disabled"] = False
db_name = os.getenv("DB_NAME", "strengerchat_pro")

# Global Pool Variable
db_pool = None

def init_pool():
    global db_pool
    try:
        db_pool = pooling.MySQLConnectionPool(
            pool_name="pro_pool",
            pool_size=10,
            database=db_name,
            **db_config
        )
        print("Database Connection Pool initialized.")
    except Exception as e:
        print(f"Pool Init Error: {e}")

def get_db_connection():
    try:
        if db_pool:
            try:
                return db_pool.get_connection()
            except:
                return mysql.connector.connect(database=db_name, **db_config)
        return mysql.connector.connect(database=db_name, **db_config)
    except Exception as e:
        print(f"DATABASE CONNECTION ERROR: {e}")
        return None

def init_db():
    logger = logging.getLogger("StrengerPro")
    logger.info("--- Cloud-Ready Database Sync ---")
    try:
        # 1. Try connecting directly to the database first
        try:
            conn = mysql.connector.connect(database=db_name, **db_config)
            logger.info(f"Connected to existing database: {db_name}")
        except:
            # 2. If it doesn't exist, try creating it (works for local XAMPP)
            logger.info(f"Database {db_name} not found. Attempting creation...")
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
            conn.commit()
            cursor.close()
            conn.close()
            conn = mysql.connector.connect(database=db_name, **db_config)

        # 2. Run Schema
        conn = mysql.connector.connect(database=db_name, **db_config)
        cursor = conn.cursor()
        with open("schema.sql", "r") as f:
            schema = f.read()
            # Split and execute properly
            for stmt in schema.split(';'):
                if stmt.strip():
                    try:
                        cursor.execute(stmt)
                    except Exception as e:
                        print(f"Notice: Skip/Error on statement: {e}")
        conn.commit()
        cursor.close()
        conn.close()
        print("Database Schema Sync: DONE")
        
        # 3. Initialize Pool
        init_pool()
        
    except Exception as e:
        print(f"CRITICAL DB INIT ERROR: {e}")
