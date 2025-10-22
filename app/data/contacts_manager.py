import sqlite3
from datetime import datetime
from app.data.database import get_db_connection

def add_contact(name, company, email, phone, address, notes, referred_by, classification, status, user_role="Comercial"):
    if user_role != "Comercial":
        raise PermissionError("Solo los usuarios comerciales pueden añadir contactos.")
    conn = get_db_connection()
    cursor = conn.cursor()
    created_at = datetime.now().isoformat()
    cursor.execute("""
        INSERT INTO contacts (name, company, email, phone, address, notes, referred_by, classification, status, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (name, company, email, phone, address, notes, referred_by, classification, status, created_at, created_at))
    conn.commit()
    conn.close()

def get_all_contacts(include_deleted=False):
    conn = get_db_connection()
    cursor = conn.cursor()
    if include_deleted:
        cursor.execute("SELECT * FROM contacts")
    else:
        cursor.execute("SELECT * FROM contacts WHERE is_deleted = 0")
    contacts = cursor.fetchall()
    conn.close()
    return [dict(contact) for contact in contacts]

def get_contact_by_id(contact_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,))
    contact = cursor.fetchone()
    conn.close()
    return dict(contact) if contact else None

def update_contact(contact_id, name, company, email, phone, address, notes, referred_by, classification, status, user_role="Comercial"):
    if user_role != "Comercial":
        raise PermissionError("Solo los usuarios comerciales pueden actualizar contactos.")
    conn = get_db_connection()
    cursor = conn.cursor()
    updated_at = datetime.now().isoformat()
    cursor.execute("""
        UPDATE contacts
        SET name = ?, company = ?, email = ?, phone = ?, address = ?, notes = ?, referred_by = ?, classification = ?, status = ?, updated_at = ?
        WHERE id = ?
    """, (name, company, email, phone, address, notes, referred_by, classification, status, updated_at, contact_id))
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