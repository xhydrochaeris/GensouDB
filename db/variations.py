from db.db import get_conn, pack, unpack

def get_variations(release_group_id):
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT * FROM VARIATIONS WHERE RG_ID = ?
        """, (release_group_id,)).fetchall()
        return [dict(row) for row in rows]
