from db import get_conn, pack, unpack

def add(name, orig_name=None, on_lang=None,
               alt_names=None, an_lang=None,
               description=None, country=None):
    with get_conn() as conn:
        cursor = conn.execute("""
            INSERT INTO ARTISTS
                (Name, Orig_Name, ON_Lang, Alt_Names, AN_Lang, Description, Country)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            name,
            orig_name,
            on_lang,
            pack(alt_names or []),
            pack(an_lang or []),
            description,
            country
        ))
        return cursor.lastrowid  # returns the new ID
    
def get(artist_id):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM ARTISTS WHERE ID = ?", (artist_id,)
        ).fetchone()
        if not row:
            return None
        result = dict(row)
        result['Alt_Names'] = unpack(result['Alt_Names'])
        result['AN_Lang']   = unpack(result['AN_Lang'])
        return result

def search(query):
    # Search by romanized name or original name
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT * FROM ARTISTS
            WHERE Name LIKE ? OR Orig_Name LIKE ?
            ORDER BY Name
        """, (f"%{query}%", f"%{query}%")).fetchall()
        return [dict(row) for row in rows]
    
def update_desc(artist_id, description):
    with get_conn() as conn:
        conn.execute("""
            UPDATE ARTISTS SET Description = ? WHERE ID = ?
        """, (description, artist_id))

def add_alt_name(artist_id, new_name, lang):
    # Append an alt name to an artist's Alt_Names array
    artist = get(artist_id)
    if not artist:
        raise ValueError(f"Artist {artist_id} not found")

    alt_names = artist['Alt_Names']
    an_lang   = artist['AN_Lang']
    alt_names.append(new_name)
    an_lang.append(lang)

    with get_conn() as conn:
        conn.execute("""
            UPDATE ARTISTS SET Alt_Names = ?, AN_Lang = ? WHERE ID = ?
        """, (pack(alt_names), pack(an_lang), artist_id))

def delete(artist_id):
    """
    Be careful — consider checking for references first.
    Foreign key enforcement will block deletion if artist
    is referenced elsewhere (when FK pragma is ON).
    """
    with get_conn() as conn:
        conn.execute("DELETE FROM ARTISTS WHERE ID = ?", (artist_id,))