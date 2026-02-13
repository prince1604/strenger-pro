from database import get_db_connection

def test_cloud_db():
    print("Testing Aiven Cloud DB Connection...")
    conn = get_db_connection()
    if conn:
        print("✅ SUCCESS: Successfully connected to Aiven Cloud MySQL!")
        conn.close()
    else:
        print("❌ FAILED: Could not connect to Aiven Cloud. Check your VPN or IP Whitelist on Aiven.")

if __name__ == "__main__":
    test_cloud_db()
