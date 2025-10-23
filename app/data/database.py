import sqlite3
import os
from pathlib import Path

def get_app_data_dir():
    """Gets the application data directory and creates it if it doesn't exist."""
    app_data_dir = Path(os.getenv('APPDATA')) / 'InfoMensajes-Power'
    app_data_dir.mkdir(parents=True, exist_ok=True)
    return app_data_dir

# Define the path for the database in the app data directory
DB_FILE = get_app_data_dir() / "crm.db"

def get_db_connection():
    """Creates a database connection."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    # Enable WAL mode for better concurrency
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn

def create_schema():
    """Creates the database schema if it doesn't exist."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Table for services
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS services (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        url TEXT NOT NULL,
        icon TEXT,
        profile_path TEXT NOT NULL UNIQUE,
        is_active BOOLEAN DEFAULT 1,
        is_internal BOOLEAN DEFAULT 0
    );
    """)

    # Table for accounts
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS accounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        company TEXT,
        email TEXT,
        phone TEXT,
        address TEXT,
        notes TEXT,
        classification TEXT,
        status TEXT,
        created_at TEXT,
        updated_at TEXT,
        is_deleted INTEGER DEFAULT 0,
        deleted_at TEXT,
        deleted_by INTEGER
    );
    """)

    # Table for contacts
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS contacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        company TEXT,
        email TEXT,
        phone TEXT,
        notes TEXT,
        referred_by TEXT,
        created_at TEXT,
        updated_at TEXT,
        is_deleted INTEGER DEFAULT 0,
        deleted_at TEXT,
        deleted_by INTEGER
    );
    """)

    # Add new columns to contacts if they don't exist
    cursor.execute("PRAGMA table_info(contacts);")
    columns = [col[1] for col in cursor.fetchall()]
    if 'confirmed' not in columns:
        cursor.execute("ALTER TABLE contacts ADD COLUMN confirmed INTEGER DEFAULT 0;")

    # Table for contact-account relationships (many-to-many)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS contact_accounts (
        contact_id INTEGER NOT NULL,
        account_id INTEGER NOT NULL,
        PRIMARY KEY (contact_id, account_id),
        FOREIGN KEY (contact_id) REFERENCES contacts (id) ON DELETE CASCADE,
        FOREIGN KEY (account_id) REFERENCES accounts (id) ON DELETE CASCADE
    );
    """)

    # Add new columns to accounts if they don't exist
    cursor.execute("PRAGMA table_info(accounts);")
    columns = [col[1] for col in cursor.fetchall()]
    if 'is_deleted' not in columns:
        cursor.execute("ALTER TABLE accounts ADD COLUMN is_deleted INTEGER DEFAULT 0;")
    if 'deleted_at' not in columns:
        cursor.execute("ALTER TABLE accounts ADD COLUMN deleted_at TEXT;")
    if 'deleted_by' not in columns:
        cursor.execute("ALTER TABLE accounts ADD COLUMN deleted_by INTEGER;")
    if 'classification' not in columns:
        cursor.execute("ALTER TABLE accounts ADD COLUMN classification TEXT;")
    if 'status' not in columns:
        cursor.execute("ALTER TABLE accounts ADD COLUMN status TEXT;")
    if 'referred_by' not in columns:
        cursor.execute("ALTER TABLE accounts ADD COLUMN referred_by TEXT;")

    # Add new columns to services if they don't exist
    cursor.execute("PRAGMA table_info(services);")
    columns = [col[1] for col in cursor.fetchall()]
    if 'is_internal' not in columns:
        cursor.execute("ALTER TABLE services ADD COLUMN is_internal BOOLEAN DEFAULT 0;")

    # Table for notes
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT NOT NULL,
        created_at TEXT,
        updated_at TEXT
    );
    """)

    # Tables for Kanban board
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS kanban_columns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        position INTEGER NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS kanban_cards (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        column_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        created_at TEXT,
        started_at TEXT,
        finished_at TEXT,
        assignee TEXT,
        due_date TEXT,
        start_date TEXT,
        end_date TEXT,
        FOREIGN KEY (column_id) REFERENCES kanban_columns (id)
    );
    """)

    # FTS table for notes
    cursor.execute("CREATE VIRTUAL TABLE IF NOT EXISTS notes_fts USING fts5(content, tokenize = 'porter unicode61');")

    # Triggers to keep notes_fts synchronized
    cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS notes_after_insert AFTER INSERT ON notes BEGIN
            INSERT INTO notes_fts(rowid, content) VALUES (new.id, COALESCE(new.content, ''));
        END;
    """)

    cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS notes_after_delete AFTER DELETE ON notes BEGIN
            DELETE FROM notes_fts WHERE rowid = old.id;
        END;
    """)

    cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS notes_after_delete AFTER DELETE ON notes BEGIN
            DELETE FROM notes_fts WHERE rowid = old.id;
        END;
    """)

    cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS notes_after_delete AFTER DELETE ON notes BEGIN
            DELETE FROM notes_fts WHERE rowid = old.id;
        END;
    """)

    cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS notes_after_update AFTER UPDATE ON notes BEGIN
            DELETE FROM notes_fts WHERE rowid = old.id;
            INSERT INTO notes_fts(rowid, content) VALUES(new.id, COALESCE(new.content, ''));
        END;
    """)



    # FTS table for kanban cards
    cursor.execute("CREATE VIRTUAL TABLE IF NOT EXISTS kanban_cards_fts USING fts5(title, description, tokenize = 'porter unicode61');")

    # Triggers to keep kanban_cards_fts synchronized
    cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS kanban_cards_after_insert AFTER INSERT ON kanban_cards BEGIN
            INSERT INTO kanban_cards_fts(rowid, title, description) VALUES (new.id, COALESCE(new.title, ''), COALESCE(new.description, ''));
        END;
    """)




    # Add new columns to kanban_cards if they don't exist
    cursor.execute("PRAGMA table_info(kanban_cards);")
    columns = [col[1] for col in cursor.fetchall()]
    if 'assignee' not in columns:
        cursor.execute("ALTER TABLE kanban_cards ADD COLUMN assignee TEXT;")
    if 'due_date' not in columns:
        cursor.execute("ALTER TABLE kanban_cards ADD COLUMN due_date TEXT;")
    if 'start_date' not in columns:
        cursor.execute("ALTER TABLE kanban_cards ADD COLUMN start_date TEXT;")
    if 'end_date' not in columns:
        cursor.execute("ALTER TABLE kanban_cards ADD COLUMN end_date TEXT;")

    # FTS5 virtual table for message indexing
    cursor.execute("""
    CREATE VIRTUAL TABLE IF NOT EXISTS messages_index USING fts5(
        source, 
        thread_id, 
        author, 
        snippet, 
        content, 
        created_at
    );
    """)

    # Table for encrypted credentials (vault)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS credentials (
        id TEXT PRIMARY KEY,
        enc_blob BLOB NOT NULL,
        nonce BLOB NOT NULL,
        salt BLOB NOT NULL
    );
    """)

    # Table for usage metrics
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usage_metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        service_id INTEGER NOT NULL,
        milliseconds INTEGER NOT NULL,
        day TEXT NOT NULL, -- YYYY-MM-DD
        FOREIGN KEY (service_id) REFERENCES services (id)
    );
    """)

    # Table for application settings
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL
    );
    """)

    # Tables for checklists
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS checklists (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        kanban_card_id INTEGER,
        FOREIGN KEY (kanban_card_id) REFERENCES kanban_cards (id) ON DELETE SET NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS checklist_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        checklist_id INTEGER NOT NULL,
        text TEXT NOT NULL,
        is_checked INTEGER NOT NULL DEFAULT 0,
        due_at TEXT,
        is_notified INTEGER NOT NULL DEFAULT 0,
        pre_notified_at TEXT,
        FOREIGN KEY (checklist_id) REFERENCES checklists (id) ON DELETE CASCADE
    );
    """)

    # Add due_at column to checklist_items if it doesn't exist
    cursor.execute("PRAGMA table_info(checklist_items);")
    columns = [col[1] for col in cursor.fetchall()]
    if 'pre_notified_at' not in columns:
        cursor.execute("ALTER TABLE checklist_items ADD COLUMN pre_notified_at TEXT;")

    # Table for reminders
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reminders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text TEXT NOT NULL,
        due_at TEXT NOT NULL,
        is_completed INTEGER NOT NULL DEFAULT 0,
        is_notified INTEGER NOT NULL DEFAULT 0,
        pre_notified_at TEXT
    );
    """)

    # Add is_notified column to reminders if it doesn't exist
    cursor.execute("PRAGMA table_info(reminders);")
    columns = [col[1] for col in cursor.fetchall()]
    if 'pre_notified_at' not in columns:
        cursor.execute("ALTER TABLE reminders ADD COLUMN pre_notified_at TEXT;")

    # Table for RSS feeds
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS rss_feeds (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        url TEXT NOT NULL UNIQUE
    );
    """)

    conn.commit()
    conn.close()
    print("Database schema created successfully.")

if __name__ == '__main__':
    create_schema()
