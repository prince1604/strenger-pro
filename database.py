import os
import logging
from dotenv import load_dotenv

load_dotenv()

# Import PostgreSQL (no MySQL)
try:
    import psycopg2
    from psycopg2 import pool
except ImportError:
    psycopg2 = None
    print("ERROR: psycopg2-binary not installed")

# Database Configuration (Neon Postgres - Global)
# User provided: postgresql://neondb_owner:npg_KFPlE17thcvk@.../neon
db_host = os.getenv("DATABASE_HOST", "ep-sparkling-paper-aegasdt0-pooler.c-2.us-east-2.aws.neon.tech")
db_user = os.getenv("DATABASE_USER", "neondb_owner")
db_pass = os.getenv("DATABASE_PASSWORD", "npg_KFPlE17thcvk") 
db_port = int(os.getenv("DATABASE_PORT", "5432"))
db_name = os.getenv("DATABASE_NAME", "neon")

db_config = {
    "host": db_host,
    "user": db_user,
    "password": db_pass,
    "port": db_port,
    "database": db_name,
    "sslmode": "require"
}

# Global connection pool
db_pool = None
last_error = None

def init_pool():
    """Initialize PostgreSQL connection pool"""
    global db_pool
    try:
        if not psycopg2:
            print("WARNING: psycopg2 not available, pool not initialized")
            return
            
        db_pool = psycopg2.pool.SimpleConnectionPool(
            1, 10,
            host=db_config["host"],
            database=db_config["database"],
            user=db_config["user"],
            password=db_config["password"],
            port=db_config["port"],
            sslmode='require',
            connect_timeout=10
        )
        print("✅ PostgreSQL Connection Pool initialized")
    except Exception as e:
        print(f"❌ Pool Init Error: {e}")

def get_db_connection():
    """Get PostgreSQL database connection"""
    global last_error
    try:
        if not psycopg2:
            raise ImportError("psycopg2 module not found")
        
        # Try to get from pool first
        if db_pool:
            try:
                return db_pool.getconn()
            except:
                pass
        
        # Fallback to direct connection
        conn = psycopg2.connect(
            host=db_config["host"],
            database=db_config["database"],
            user=db_config["user"],
            password=db_config["password"],
            port=db_config["port"],
            sslmode='require',
            connect_timeout=10
        )
        return conn
        
    except Exception as e:
        last_error = str(e)
        print(f"❌ DATABASE CONNECTION ERROR: {e}")
        return None

def init_db():
    """Initialize PostgreSQL database schema"""
    logger = logging.getLogger("StrengerPro")
    logger.info("--- PostgreSQL Database Sync ---")
    
    try:
        if not psycopg2:
            logger.error("❌ psycopg2-binary not installed")
            return
        
        # Connect to database
        conn = psycopg2.connect(
            host=db_config["host"],
            database=db_config["database"],
            user=db_config["user"],
            password=db_config["password"],
            port=db_config["port"],
            sslmode='require',
            connect_timeout=10
        )
        
        cursor = conn.cursor()
        
        # Load and execute schema
        schema_file = "schema_pg.sql"
        if os.path.exists(schema_file):
            logger.info(f"Loading schema from {schema_file}")
            with open(schema_file, "r") as f:
                schema = f.read()
                cursor.execute(schema)
            conn.commit()
            logger.info("✅ PostgreSQL schema initialized")
        else:
            logger.warning(f"⚠️ {schema_file} not found - skipping schema sync")
        
        cursor.close()
        conn.close()
        
        # Initialize connection pool
        init_pool()
        
        logger.info("✅ Database initialization complete")
        
    except Exception as e:
        logger.error(f"❌ CRITICAL DB INIT ERROR: {e}")
        print(f"❌ Database init failed: {e}")
