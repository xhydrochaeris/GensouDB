from db.db import get_conn, pack, unpack

def add(artist_ids, artist_aliases, title,
                      release_type=8, description=None, release_date=None):
    with get_conn() as conn:
        cursor = conn.execute("""
            INSERT INTO RLS_GROUPS
                (A_ID, A_Alias, Title, Release_Type, Description, Release_Date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            pack(artist_ids),
            pack(artist_aliases),
            title,
            release_type,
            description,
            release_date
        ))
        return cursor.lastrowid
    
def get_by_artist(artist_id):
    # Find all release groups an artist is part of
    with get_conn() as conn:
        # json_each lets us query into the JSON array
        rows = conn.execute("""
            SELECT RLS_GROUPS.* FROM RLS_GROUPS, json_each(RLS_GROUPS.A_ID)
            WHERE json_each.value = ?
            ORDER BY Release_Date
        """, (artist_id,)).fetchall()
        return [dict(row) for row in rows]
