from db import get_conn, pack, unpack

def get_releases(variation_id):
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT * FROM RELEASES WHERE Var_ID = ?
            ORDER BY Release_Date
        """, (variation_id,)).fetchall()
        return [dict(row) for row in rows]
    
def delete_release(release_id):
    with get_conn() as conn:
        conn.execute("DELETE FROM RELEASES WHERE ID = ?", (release_id,))