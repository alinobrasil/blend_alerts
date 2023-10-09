import sqlite3

# Connect to the 'labs.db' database. It will create the file if it doesn't exist.
with sqlite3.connect('labs.sqlite') as conn:
    # Create a cursor object to interact with the database.
    cursor = conn.cursor()

    # Create the 'users' table with fields: userId, displayname, handle.
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        userId INTEGER PRIMARY KEY,
        displayname TEXT NOT NULL,
        handle TEXT NOT NULL UNIQUE
    )
    ''')

    # Create the 'subscription' table with fields: userId, address.
    cursor.execute('''
                   DROP TABLE IF EXISTS subscription;
                   ''')

    cursor.execute('''
    CREATE TABLE subscription (
        userId INTEGER NOT NULL,
        address TEXT NOT NULL,
        FOREIGN KEY(userId) REFERENCES users(userId),
        UNIQUE (userId, address)

    )
    ''')

# At this point, the tables have been created in 'labs.sqlite'.


# Connect to the 'labs.db' database.
with sqlite3.connect('labs.sqlite') as conn:
    # Create a cursor object to interact with the database.
    cursor = conn.cursor()

    # Insert a row into the 'users' table.
    user_data = (122356443123, 'John Doe', '@3424')
    cursor.execute(
        'INSERT INTO users (userId, displayname, handle) VALUES (?, ?, ?)', user_data)

    # Get the last inserted userId (useful when you have an auto-incremented primary key).
    last_user_id = cursor.lastrowid

    # Insert a row into the 'subscription' table using the last inserted userId.
    subscription_data = (last_user_id, '0x9823ab567b8888f88')
    cursor.execute(
        'INSERT INTO subscription (userId, address) VALUES (?, ?)', subscription_data)
