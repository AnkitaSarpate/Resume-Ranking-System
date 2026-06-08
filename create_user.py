import json
from werkzeug.security import generate_password_hash

# Try to load existing users.json, otherwise create empty dictionary
try:
    with open("users.json", "r") as f:
        users = json.load(f)
except FileNotFoundError:
    users = {}

# Ask for new user info
username = input("Enter username: ").strip()
password = input("Enter password: ").strip()

# Save with encrypted password
users[username] = generate_password_hash(password)

# Write back to users.json
with open("users.json", "w") as f:
    json.dump(users, f, indent=4)

print(f"✅ User '{username}' created successfully!")
