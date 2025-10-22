from .database import get_db_connection
from datetime import datetime

def add_account(name, company=None, email=None, phone=None, address=None, notes=None, referred_by=None, user_role="", classification="Lead", status="Por contactar"):
    if user_role != "Comercial":
        raise PermissionError("Solo los usuarios con rol 'Comercial' pueden añadir cuentas.")

    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute(
        "INSERT INTO accounts (name, company, email, phone, address, notes, referred_by, classification, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (name, company, email, phone, address, notes, referred_by, classification, status, now, now)
    )
    conn.commit()
    account_id = cursor.lastrowid
    conn.close()
    return account_id

def get_all_accounts(include_deleted=False):
    conn = get_db_connection()
    if include_deleted:
        accounts = conn.execute("SELECT * FROM accounts ORDER BY name").fetchall()
    else:
        accounts = conn.execute("SELECT * FROM accounts WHERE is_deleted = 0 ORDER BY name").fetchall()
    conn.close()
    return accounts

def get_deleted_accounts():
    conn = get_db_connection()
    accounts = conn.execute("SELECT * FROM accounts WHERE is_deleted = 1 ORDER BY name").fetchall()
    conn.close()
    return accounts

def get_account_by_id(account_id, include_deleted=False):
    conn = get_db_connection()
    if include_deleted:
        account = conn.execute("SELECT * FROM accounts WHERE id = ?", (account_id,)).fetchone()
    else:
        account = conn.execute("SELECT * FROM accounts WHERE id = ? AND is_deleted = 0", (account_id,)).fetchone()
    conn.close()
    return account

def update_account(account_id, name, company=None, email=None, phone=None, address=None, notes=None, referred_by=None, classification=None, status=None, user_role=""): # Added user_role
    if user_role != "Comercial":
        raise PermissionError("Solo los usuarios con rol 'Comercial' pueden editar cuentas.")

    conn = get_db_connection()
    now = datetime.now().isoformat()
    conn.execute(
        "UPDATE accounts SET name = ?, company = ?, email = ?, phone = ?, address = ?, notes = ?, referred_by = ?, classification = ?, status = ?, updated_at = ? WHERE id = ?",
        (name, company, email, phone, address, notes, referred_by, classification, status, now, account_id)
    )
    conn.commit()
    conn.close()

def delete_account(account_id, deleted_by_user_id=1, user_role=""): # Added user_role
    if user_role != "Comercial":
        raise PermissionError("Solo los usuarios con rol 'Comercial' pueden eliminar cuentas.")

    conn = get_db_connection()
    now = datetime.now().isoformat()
    conn.execute(
        "UPDATE accounts SET is_deleted = 1, deleted_at = ?, deleted_by = ? WHERE id = ?",
        (now, deleted_by_user_id, account_id)
    )
    conn.commit()
    conn.close()

def restore_account(account_id, user_role=""): # Added user_role
    if user_role != "Comercial":
        raise PermissionError("Solo los usuarios con rol 'Comercial' pueden restaurar cuentas.")

    conn = get_db_connection()
    conn.execute(
        "UPDATE accounts SET is_deleted = 0, deleted_at = NULL, deleted_by = NULL WHERE id = ?",
        (account_id,)
    )
    conn.commit()
    conn.close()
