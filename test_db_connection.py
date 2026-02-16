"""
🔧 Koyeb Database Connection Tester
This script will help you verify your database connection
"""
import os
import sys
from dotenv import load_dotenv

# Import psycopg2 early to check if it's available
try:
    import psycopg2
except ImportError:
    print("\n❌ psycopg2 not installed!")
    print("💡 Run: pip install psycopg2-binary")
    sys.exit(1)

print("=" * 60)
print("🔍 KOYEB DATABASE CONNECTION TESTER")
print("=" * 60)

# Load environment variables
load_dotenv()

# Get database configuration
db_config = {
    "host": os.getenv("DATABASE_HOST", os.getenv("DB_HOST")),
    "user": os.getenv("DATABASE_USER", os.getenv("DB_USER")),
    "password": os.getenv("DATABASE_PASSWORD", os.getenv("DB_PASSWORD")),
    "port": os.getenv("DATABASE_PORT", os.getenv("DB_PORT", "5432")),
    "database": os.getenv("DATABASE_NAME", os.getenv("DB_NAME")),
}

print("\n📋 Current Configuration:")
print(f"   Host: {db_config['host']}")
print(f"   Port: {db_config['port']}")
print(f"   User: {db_config['user']}")
print(f"   Password: {'*' * len(db_config['password']) if db_config['password'] else 'NOT SET'}")
print(f"   Database: {db_config['database']}")

# Check if all required variables are set
missing = []
for key, value in db_config.items():
    if not value:
        missing.append(key)

if missing:
    print(f"\n❌ MISSING CONFIGURATION: {', '.join(missing)}")
    print("\n💡 Fix: Add these to your .env file or Koyeb environment variables")
    sys.exit(1)

print("\n✅ All configuration variables are set!")

# Try to connect
print("\n🔌 Attempting connection...")
try:
    import psycopg2
    
    conn = psycopg2.connect(
        host=db_config["host"],
        port=int(db_config["port"]),
        user=db_config["user"],
        password=db_config["password"],
        database=db_config["database"],
        sslmode='require'
    )
    
    print("✅ CONNECTION SUCCESSFUL!")
    
    # Test query
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()[0]
    print(f"\n📊 PostgreSQL Version:")
    print(f"   {version}")
    
    # Check if tables exist
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
    """)
    tables = cursor.fetchall()
    
    if tables:
        print(f"\n📁 Existing Tables ({len(tables)}):")
        for table in tables:
            print(f"   ✓ {table[0]}")
    else:
        print("\n⚠️  No tables found. Run schema_pg.sql to create them.")
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 60)
    print("🎉 DATABASE IS READY TO USE!")
    print("=" * 60)
    
except psycopg2.OperationalError as e:
    error_msg = str(e)
    print(f"\n❌ CONNECTION FAILED!")
    print(f"\nError Details: {error_msg}")
    
    print("\n🔧 Troubleshooting:")
    if "password authentication failed" in error_msg:
        print("   • Double-check your password is COMPLETE and CORRECT")
        print("   • Copy the password directly from Koyeb database page")
    elif "could not connect" in error_msg or "timeout" in error_msg:
        print("   • Verify the host address is correct")
        print("   • Check if your IP is allowed (Koyeb usually allows all)")
    elif "SSL" in error_msg or "ssl" in error_msg:
        print("   • SSL connection issue - already handled in code")
    else:
        print("   • Check all credentials again")
        print("   • Verify database exists in Koyeb")
    
    print(f"\n📝 Your current password length: {len(db_config['password'])} characters")
    print("   Koyeb passwords are typically 16-20+ characters")
    if len(db_config['password']) < 16:
        print("   ⚠️  Your password looks too short! Get the full password from Koyeb")
    
    sys.exit(1)
    
except ImportError:
    print("\n❌ psycopg2 not installed!")
    print("💡 Run: pip install psycopg2-binary")
    sys.exit(1)
    
except Exception as e:
    print(f"\n❌ UNEXPECTED ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
