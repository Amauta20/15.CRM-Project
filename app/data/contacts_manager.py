import sqlite3
from datetime import datetime
from app.data.database import get_db_connection
from app.data import accounts_manager

def add_contact(name, email, phone, notes, referred_by, confirmed, account_id=None, user_role="Comercial"):
    if user_role != "Comercial":
        raise PermissionError("Solo los usuarios comerciales pueden añadir contactos.")
    conn = get_db_connection()
    cursor = conn.cursor()
    created_at = datetime.now().isoformat()
    cursor.execute("""
        INSERT INTO contacts (name, email, phone, notes, referred_by, confirmed, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (name, email, phone, notes, referred_by, confirmed, created_at, created_at))
    contact_id = cursor.lastrowid
    if account_id:
        add_contact_to_account(contact_id, account_id, conn)
    conn.commit()
    conn.close()
    return contact_id

def get_all_contacts(include_deleted=False):
    conn = get_db_connection()
    cursor = conn.cursor()
    if include_deleted:
        cursor.execute("SELECT id, name, email, phone, notes, referred_by, confirmed, created_at, updated_at, is_deleted, deleted_at, deleted_by FROM contacts")
    else:
        cursor.execute("SELECT id, name, email, phone, notes, referred_by, confirmed, created_at, updated_at, is_deleted, deleted_at, deleted_by FROM contacts WHERE is_deleted = 0")
    contacts = cursor.fetchall()
    conn.close()
    return [dict(contact) for contact in contacts]

def get_contact_by_id(contact_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, phone, notes, referred_by, confirmed, created_at, updated_at, is_deleted, deleted_at, deleted_by FROM contacts WHERE id = ?", (contact_id,))
    contact = cursor.fetchone()
    conn.close()
    return dict(contact) if contact else None

def update_contact(contact_id, name, email, phone, notes, referred_by, confirmed, user_role="Comercial"):
    if user_role != "Comercial":
        raise PermissionError("Solo los usuarios comerciales pueden actualizar contactos.")
    conn = get_db_connection()
    cursor = conn.cursor()
    updated_at = datetime.now().isoformat()
    cursor.execute("""
        UPDATE contacts
        SET name = ?, email = ?, phone = ?, notes = ?, referred_by = ?, confirmed = ?, updated_at = ?
        WHERE id = ?
    """, (name, email, phone, notes, referred_by, confirmed, updated_at, contact_id))
    conn.commit()
    conn.close()

def delete_contact(contact_id, deleted_by_user_id, user_role="Comercial"):
    if user_role != "Comercial":
        raise PermissionError("Solo los usuarios comerciales pueden eliminar contactos.")
    conn = get_db_connection()
    cursor = conn.cursor()
    deleted_at = datetime.now().isoformat()
    cursor.execute("""
        UPDATE contacts
        SET is_deleted = 1, deleted_at = ?, deleted_by = ?
        WHERE id = ?
    """, (deleted_at, deleted_by_user_id, contact_id))
    conn.commit()
    conn.close()

def get_deleted_contacts():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM contacts WHERE is_deleted = 1")
    contacts = cursor.fetchall()
    conn.close()
    return [dict(contact) for contact in contacts]

def restore_contact(contact_id, user_role="Comercial"):
    if user_role != "Comercial":
        raise PermissionError("Solo los usuarios comerciales pueden restaurar contactos.")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE contacts
        SET is_deleted = 0, deleted_at = NULL, deleted_by = NULL
        WHERE id = ?
    """, (contact_id,))
    conn.commit()
    conn.close()

def add_contact_to_account(contact_id, account_id, conn):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO contact_accounts (contact_id, account_id) VALUES (?, ?)", (contact_id, account_id))

def remove_contact_from_account(contact_id, account_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM contact_accounts WHERE contact_id = ? AND account_id = ?", (contact_id, account_id))
    conn.commit()
    conn.close()

def get_accounts_for_contact(contact_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.id, a.name
        FROM accounts a
        JOIN contact_accounts ca ON a.id = ca.account_id
        WHERE ca.contact_id = ?
    """, (contact_id,))
    accounts = cursor.fetchall()
    conn.close()
    return [dict(account) for account in accounts]

def get_contacts_for_account(account_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.id, c.name, c.email
        FROM contacts c
        JOIN contact_accounts ca ON c.id = ca.contact_id
        WHERE ca.account_id = ?
    """, (account_id,))
    contacts = cursor.fetchall()
    conn.close()
    return [dict(contact) for contact in contacts]