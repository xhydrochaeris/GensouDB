:: Must have python and pip installed and in the path
python -m pip install aiohttp argon2-cffi

preinclude_sqlite3_win\sqlite3.exe db\gensou.db < schema\00_schema.sql
