-- Release type enum reference (stored as INTEGER):
-- 0: Album, 1: EP, 2: Single, 3: Demo, 4: Compilation,
-- 5: Live, 6: Soundtrack, 7: Bootleg, 8: Other

-- File/Item type enum reference:
-- 0: Music, 1: Video, 2: Scan, 3: Physical, 4: Document, 5: Other

-- User class enum reference:
-- 0: User, 5: Member, 10: Contributor, 20: PowerUser,
-- 30: Elite, 50: Moderator, 99: Admin

PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE ARTISTS (
    ID          INTEGER PRIMARY KEY AUTOINCREMENT,
    Name        TEXT NOT NULL,                  -- Romanized name (assumed RNZ)
    Orig_Name   TEXT,                           -- Name in original script
    ON_Lang     TEXT CHECK(length(ON_Lang) = 3),-- ISO 639-3 language of Orig_Name
    Alt_Names   TEXT DEFAULT '[]',              -- JSON array of strings
    AN_Lang     TEXT DEFAULT '[]',              -- JSON array of 3-char lang codes
    Description TEXT,
    Country     TEXT CHECK(length(Country) = 3) -- ISO 3166-1 alpha-3
);

CREATE TABLE RLS_GROUPS (
    ID           INTEGER PRIMARY KEY AUTOINCREMENT,
    A_ID         TEXT NOT NULL DEFAULT '[]',    -- JSON array of ARTISTS.ID
    A_Alias      TEXT NOT NULL DEFAULT '[]',    -- JSON array of alias indices (-1 = no alias)
    Title        TEXT NOT NULL,
    Release_Type INTEGER NOT NULL DEFAULT 8,    -- enum, see above
    Description  TEXT,
    Release_Date TEXT                           -- fuzzy: "1992.01.xx", "[1998-2001]", etc.
);

CREATE TABLE VARIATIONS (
    ID          INTEGER PRIMARY KEY AUTOINCREMENT,
    RG_ID       INTEGER NOT NULL REFERENCES RLS_GROUPS(ID),
    Title       TEXT,                           -- NULL if no distinct variation name
    Description TEXT
);

CREATE TABLE RELEASES (
    ID           INTEGER PRIMARY KEY AUTOINCREMENT,
    Var_ID       INTEGER NOT NULL REFERENCES VARIATIONS(ID),
    A_Alias      TEXT NOT NULL DEFAULT '[]',    -- JSON array of alias indices
    Title        TEXT,                          -- NULL if same as release group title
    Label        TEXT,
    Cat_No       TEXT,
    Release_Date TEXT,                          -- fuzzy date
    Country      TEXT CHECK(length(Country) = 3),
    Description  TEXT
);

CREATE TABLE ITEMS (
    ID      INTEGER PRIMARY KEY AUTOINCREMENT,
    Rls_ID  INTEGER NOT NULL REFERENCES RELEASES(ID),
    Medium  TEXT NOT NULL,                      -- "12\" Vinyl", "CD", "Cassette", etc.
    Type    INTEGER NOT NULL DEFAULT 0,         -- enum: 0=Music, 1=Video, 2=Physical
    Disc    INTEGER DEFAULT 1,
    Side    TEXT,                               -- Side of physical medium
    Details TEXT
);

CREATE TABLE SONG (
    ID         INTEGER PRIMARY KEY AUTOINCREMENT,
    Title      TEXT NOT NULL,
    Language   TEXT CHECK(length(Language) = 3),-- ISO 639-3
    Associated TEXT DEFAULT '[]'                -- JSON array of SONG.IDs
);

CREATE TABLE FILE (
    ID       INTEGER PRIMARY KEY AUTOINCREMENT,
    Item_ID  INTEGER NOT NULL REFERENCES ITEMS(ID),
    Song_ID  INTEGER REFERENCES SONG(ID),       -- NULL for non-music files
    No       INTEGER,                           -- track/page number
    Title    TEXT,                              -- can differ from SONG.Title (e.g. live title)
    Artists  TEXT NOT NULL DEFAULT '[]',        -- JSON array of ARTISTS.IDs
    A_Alias  TEXT NOT NULL DEFAULT '[]',        -- JSON array of alias indices
    Format   TEXT,                              -- "FLAC", "MP3", "JPG", "LOG", etc.
    Bitrate  TEXT,                              -- "lossless", "320kbps", "24bit/96kHz", etc.
    Quality  TEXT,                              -- free text rip quality notes
    Type     INTEGER NOT NULL DEFAULT 0,        -- enum: 0=Music, 1=Video, 2=Scan, etc.
    Location TEXT                               -- relative file path from storage root
);

CREATE TABLE USER (
    ID          INTEGER PRIMARY KEY AUTOINCREMENT,
    dname       TEXT NOT NULL UNIQUE CHECK(length(dname) <= 40), -- Display name
    uname       TEXT NOT NULL UNIQUE CHECK(                      -- Username
                    length(uname) <= 20 AND
                    uname GLOB '*[^a-zA-Z0-9_-]*' = 0
                ),
    class       INT NOT NULL DEFAULT 0,                          -- User class (enum)
    pw_hash     TEXT,                                            -- Password (hashed)
    created     TEXT,                                            -- Account creation date
    pw_date     TEXT,                                            -- Latest Password date
    SESS_ID     TEXT,                                            -- Session ID
    SESS_Expiry TEXT,                                            -- Session Expiry
    dummy_pw    BOOLEAN NOT NULL DEFAULT 1,                      -- The password is not initialized by the user yet
    -- Add more preferences
    theme       TEXT NOT NULL DEFAULT 'default'
);

INSERT INTO USER (ID, dname, uname, class) VALUES (0, 'CIPHER 【零】', 'cipher', 99);
