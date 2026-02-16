import mysql.connector
from mysql.connector import pooling
import os
import logging
from dotenv import load_dotenv

load_dotenv()

# Database Configuration
# KOYEB CLOUD: STRICTLY HARDCODED (No Env Vars)
import urllib.parse as urlparse

# NEW CREDENTIALS (EU REGION) - FORCED
db_host = "ep-gentle-hat-agcpn3l9.c-2.eu-central-1.pg.koyeb.app"
db_user = "koyeb-adm"
db_pass = "npg_g8MvPfqjw1lO"
db_port = 5432
db_name = "koyebdb"

# Force configuration - Allow NO overrides
db_config = {
    "host": db_host,
    "user": db_user,
    "password": db_pass,
    "port": int(db_port)
    # sslmode is handled in connection logic
}

# PRO TIP: Postgres uses 'sslmode', MySQL uses 'ssl_mode'
if db_config["host"] != "localhost":
    # Make a copy for MySQL to avoid polluting global config if mixed usage
    # But for now, we just set it. 
    # ERROR FIX: Only add sslmode if we are SURE it's Postgres? 
    # No, we can't contextually change global config easily.
    # Instead, we will handle this in get_connection logic.
    pass 

db_name = os.getenv("DATABASE_NAME", os.getenv("DB_NAME", "koyebdb"))

# Global Pool Variable
db_pool = None

def init_pool():
    global db_pool
    try:
        # Prevent MySQL Pool from crashing with Postgres args
        safe_config = db_config.copy()
        if "sslmode" in safe_config: del safe_config["sslmode"]
        
        db_pool = pooling.MySQLConnectionPool(
            pool_name="pro_pool",
            pool_size=10,
            database=db_name,
            **safe_config
        )
        print("Database Connection Pool initialized.")
    except Exception as e:
        print(f"Pool Init Error: {e}")

# Global checks
last_error = None
try:
    import psycopg2
    from psycopg2 import pool
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
        # 1. PRIORITY: Check for PostgreSQL (Koyeb/Cloud)
        if "pg.koyeb.app" in db_config["host"]:
             # POSTGRES SYNC
            logger.info("--- POSTGRES SCHEMA SYNC ---")
            
            # Ensure psycopg2 is available
            if not psycopg2:
                logger.error("PSYGOPG2 MISSING during init_db")
                return

            conn = psycopg2.connect(
                host=db_config["host"],
                database=db_name,
                user=db_config["user"],
                password=db_config["password"],
                port=db_config["port"],
                sslmode='require'
            )
            cursor = conn.cursor()
            
            # Create schema from file
            if os.path.exists("schema_pg.sql"):
                with open("schema_pg.sql", "r") as f:
                    cursor.execute(f.read())
                conn.commit()
                logger.info("POSTGRES DB READY")
            else:
                logger.warning("schema_pg.sql NOT FOUND - Skipping schema sync")
                
            cursor.close()
            conn.close()
            return

        # 2. Check for AIVEN/Remote MySQL (Non-Localhost)
        if db_config["host"] != "localhost":
            logger.info(f"CLOUD MODE (MySQL): Using existing database '{db_name}'")
            # Just verify connection, don't create DB
            conn = mysql.connector.connect(database=db_name, **db_config)
            conn.close()
        
        # 3. Localhost MySQL (Create DB if missing)
        else:
            try:
                conn = mysql.connector.connect(database=db_name, **db_config)
                conn.close()
            except:
                logger.info(f"Database {db_name} not found. Attempting creation...")
                conn = mysql.connector.connect(**db_config)
                cursor = conn.cursor()
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
                conn.commit()
                cursor.close()
                conn.close()

        # 4. Run Schema (MySQL Only)
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
