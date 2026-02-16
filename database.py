import mysql.connector
from mysql.connector import pooling
import psycopg2
from psycopg2 import pool
import os
import logging
from dotenv import load_dotenv

load_dotenv()

# Database Configuration
# KOYEB CLOUD: Prioritize DATABASE_URL or Postgres variables
import urllib.parse as urlparse

# HARDCODED FALLBACK FOR KOYEB POSTGRES
db_host = os.getenv("DATABASE_HOST", os.getenv("DB_HOST", "ep-gentle-hat-agcpn3l9.c-2.eu-central-1.pg.koyeb.app"))
db_user = os.getenv("DATABASE_USER", os.getenv("DB_USER", "koyeb-adm"))
db_pass = os.getenv("DATABASE_PASSWORD", os.getenv("DB_PASSWORD", "npg_g8MvPfqjw1lO"))
db_port = os.getenv("DATABASE_PORT", os.getenv("DB_PORT", "5432"))
db_name = os.getenv("DATABASE_NAME", os.getenv("DB_NAME", "koyebdb"))

db_config = {
    "host": db_host,
    "user": db_user,
    "password": db_pass,
    "port": int(db_port),
    "ssl_disabled": False 
}

# PRO TIP: Postgres uses 'sslmode', MySQL uses 'ssl_mode'
if db_config["host"] != "localhost":
    db_config["sslmode"] = "require"
    # Remove MySQL specific keys if present to avoid confusion
    if "ssl_disabled" in db_config: del db_config["ssl_disabled"]

db_name = os.getenv("DATABASE_NAME", os.getenv("DB_NAME", "koyebdb"))

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

# Global checks
last_error = None
try:
    import psycopg2
except ImportError:
    last_error = "psycopg2-binary not installed in environment"
    psycopg2 = None

def get_db_connection():
    global last_error
    try:
        # Postgres Logic (Cloud)
        if "pg.koyeb.app" in db_config["host"]:
             if not psycopg2:
                 raise ImportError("psycopg2 module not found")
                 
             return psycopg2.connect(
                host=db_config["host"],
                database=db_name,
                user=db_config["user"],
                password=db_config["password"],
                port=db_config["port"],
                sslmode='require',
                connect_timeout=10
            )
        
        # MySQL Logic (Local/TiDB)
        if db_pool:
            try:
                return db_pool.get_connection()
            except:
                return mysql.connector.connect(database=db_name, **db_config)
        return mysql.connector.connect(database=db_name, **db_config)
    except Exception as e:
        last_error = str(e)
        print(f"DATABASE CONNECTION ERROR: {e}")
        return None

def init_db():
    logger = logging.getLogger("StrengerPro")
    logger.info("--- Cloud-Ready Database Sync ---")
    try:
        # AIVEN CLOUD FIX: Do not try to create DB if on cloud
        if db_config["host"] != "localhost":
            logger.info(f"CLOUD MODE: Using existing database '{db_name}'")
            conn = mysql.connector.connect(database=db_name, **db_config)
        else:
            # Localhost logic (creates DB if missing)
            try:
                conn = mysql.connector.connect(database=db_name, **db_config)
            except:
                logger.info(f"Database {db_name} not found. Attempting creation...")
                conn = mysql.connector.connect(**db_config)
                cursor = conn.cursor()
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
                conn.commit()
                cursor.close()
                conn = mysql.connector.connect(database=db_name, **db_config)

        if "pg.koyeb.app" in db_config["host"]:
             # POSTGRES SYNC
            logger.info("--- POSTGRES SCHEMA SYNC ---")
            conn = psycopg2.connect(
                host=db_config["host"],
                database=db_name,
                user=db_config["user"],
                password=db_config["password"],
                port=db_config["port"],
                sslmode='require'
            )
            cursor = conn.cursor()
            with open("schema_pg.sql", "r") as f:
                cursor.execute(f.read())
            conn.commit()
            cursor.close()
            conn.close()
            logger.info("POSTGRES DB READY")
            return

        # 2. Run Schema (MySQL)
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
