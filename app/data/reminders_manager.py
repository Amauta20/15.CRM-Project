import sqlite3
from .database import get_db_connection

def get_reminders_due_between(start_date, end_date):
    """
    Retrieves all non-completed reminders due between two dates.

    Args:
        start_date (str): The start date in ISO format.
        end_date (str): The end date in ISO format.

    Returns:
        list: A list of reminders (as dicts) due within the specified range.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM reminders WHERE due_at >= ? AND due_at <= ? AND is_completed = 0",
        (start_date, end_date)
    )
    reminders = cursor.fetchall()
    conn.close()
    # Convert rows to dicts
    return [dict(row) for row in reminders]
