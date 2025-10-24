from app.data.database import get_db_connection
from datetime import datetime

def add_opportunity(user_role, title, requirement=None, conditions=None, amount=None, currency=None, status=None, phase=None, owner_user_id=None, account_id=None, contact_id=None, delivery_date=None, success_probability=None):
    if user_role != "Comercial":
        raise PermissionError("Solo los usuarios con rol 'Comercial' pueden añadir oportunidades.")

    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute(
        "INSERT INTO opportunities (title, requirement, conditions, amount, currency, status, phase, owner_user_id, account_id, contact_id, delivery_date, success_probability, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (title, requirement, conditions, amount, currency, status, phase, owner_user_id, account_id, contact_id, delivery_date, success_probability, now, now)
    )
    conn.commit()
    opportunity_id = cursor.lastrowid
    conn.close()
    return opportunity_id

def get_all_opportunities(include_deleted=False):
    conn = get_db_connection()
    if include_deleted:
        opportunities = conn.execute("SELECT * FROM opportunities ORDER BY title").fetchall()
    else:
        opportunities = conn.execute("SELECT * FROM opportunities WHERE is_deleted = 0 ORDER BY title").fetchall()
    conn.close()
    return opportunities

def get_opportunity_by_id(opportunity_id, include_deleted=False):
    conn = get_db_connection()
    if include_deleted:
        opportunity = conn.execute("SELECT *, contact_id FROM opportunities WHERE id = ?", (opportunity_id,)).fetchone()
    else:
        opportunity = conn.execute("SELECT *, contact_id FROM opportunities WHERE id = ? AND is_deleted = 0", (opportunity_id,)).fetchone()
    conn.close()
    return opportunity

def update_opportunity(user_role, opportunity_id, title, requirement=None, conditions=None, amount=None, currency=None, status=None, phase=None, owner_user_id=None, account_id=None, contact_id=None, delivery_date=None, success_probability=None):
    if user_role != "Comercial":
        raise PermissionError("Solo los usuarios con rol 'Comercial' pueden editar oportunidades.")

    conn = get_db_connection()
    now = datetime.now().isoformat()
    conn.execute(
        "UPDATE opportunities SET title = ?, requirement = ?, conditions = ?, amount = ?, currency = ?, status = ?, phase = ?, owner_user_id = ?, account_id = ?, contact_id = ?, delivery_date = ?, success_probability = ?, updated_at = ? WHERE id = ?",
        (title, requirement, conditions, amount, currency, status, phase, owner_user_id, account_id, contact_id, delivery_date, success_probability, now, opportunity_id)
    )
    conn.commit()
    conn.close()

def delete_opportunity(user_role, opportunity_id, deleted_by_user_id=1):
    if user_role != "Comercial":
        raise PermissionError("Solo los usuarios con rol 'Comercial' pueden eliminar oportunidades.")

    conn = get_db_connection()
    now = datetime.now().isoformat()
    conn.execute(
        "UPDATE opportunities SET is_deleted = 1, deleted_at = ?, deleted_by = ? WHERE id = ?",
        (now, deleted_by_user_id, opportunity_id)
    )
    conn.commit()
    conn.close()

def restore_opportunity(user_role, opportunity_id):
    if user_role != "Comercial":
        raise PermissionError("Solo los usuarios con rol 'Comercial' pueden restaurar oportunidades.")

    conn = get_db_connection()
    conn.execute(
        "UPDATE opportunities SET is_deleted = 0, deleted_at = NULL, deleted_by = NULL WHERE id = ?",
        (opportunity_id,)
    )
    conn.commit()
    conn.close()

def update_opportunity_proposal_path(opportunity_id, proposal_path, drive_folder_id):
    conn = get_db_connection()
    now = datetime.now().isoformat()
    conn.execute(
        "UPDATE opportunities SET proposal_path = ?, drive_folder_id = ?, updated_at = ? WHERE id = ?",
        (proposal_path, drive_folder_id, now, opportunity_id)
    )
    conn.commit()
    conn.close()
