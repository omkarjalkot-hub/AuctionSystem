import hashlib
import getpass
from database.connection import get_connection


print("===================================")
print("      SmartBid Admin Account")
print("===================================")

first_name = input("Admin first name: ").strip()
last_name = input("Admin last name: ").strip()
email = input("Admin email: ").strip()

password = getpass.getpass("Admin password: ")
confirm_password = getpass.getpass("Confirm password: ")


if not first_name or not last_name or not email or not password:
    print("❌ All fields are required.")
    exit()


if password != confirm_password:
    print("❌ Passwords do not match.")
    exit()


if len(password) < 6:
    print("❌ Password must contain at least 6 characters.")
    exit()


password_hash = hashlib.sha256(
    password.encode()
).hexdigest()


connection = get_connection()


if not connection:
    print("❌ Unable to connect to SmartBid database.")
    exit()


cursor = connection.cursor()


# Check whether email already exists
cursor.execute(
    "SELECT user_id, role FROM users WHERE email = %s",
    (email,)
)

existing_user = cursor.fetchone()


if existing_user:

    print(
        f"❌ An account with this email already exists "
        f"(User ID: {existing_user[0]}, Role: {existing_user[1]})."
    )

else:

    cursor.execute(
        """
        INSERT INTO users
        (first_name, last_name, email, password_hash, role)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (
            first_name,
            last_name,
            email,
            password_hash,
            "Admin"
        )
    )

    connection.commit()

    print()
    print("✅ Admin account created successfully!")
    print(f"Admin email: {email}")
    print("Role: Admin")


cursor.close()
connection.close()