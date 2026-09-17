import sqlite3


connection = sqlite3.connect("monitoring.db")

cursor = connection.cursor()


columns = cursor.execute(
    "PRAGMA table_info(monitor)"
).fetchall()

column_names = [
    column[1]
    for column in columns
]


if "user_id" not in column_names:

    cursor.execute(
        "ALTER TABLE monitor ADD COLUMN user_id INTEGER"
    )

    print("user_id column added successfully!")


if "check_interval_seconds" not in column_names:

    cursor.execute(
        """
        ALTER TABLE monitor
        ADD COLUMN check_interval_seconds INTEGER
        DEFAULT 60
        """
    )

    print(
        "check_interval_seconds column "
        "added successfully!"
    )
if "last_checked_at" not in column_names:

    cursor.execute(
        """
        ALTER TABLE monitor
        ADD COLUMN last_checked_at DATETIME
        """
    )

    print("last_checked_at column added!")


if "last_status_code" not in column_names:

    cursor.execute(
        """
        ALTER TABLE monitor
        ADD COLUMN last_status_code INTEGER
        """
    )

    print("last_status_code column added!")


if "last_response_time_ms" not in column_names:

    cursor.execute(
        """
        ALTER TABLE monitor
        ADD COLUMN last_response_time_ms FLOAT
        """
    )

    print("last_response_time_ms column added!")

if "last_is_success" not in column_names:

    cursor.execute(
        """
        ALTER TABLE monitor
        ADD COLUMN last_is_success BOOLEAN
        """
    )

    print("last_is_success column added!")

connection.commit()

connection.close()

print("Migration completed!")