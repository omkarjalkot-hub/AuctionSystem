from database.connection import get_connection

connection = get_connection()

if connection:
    print("✅ Connected to SmartBid database successfully!")
    connection.close()
else:
    print("❌ Connection failed.")