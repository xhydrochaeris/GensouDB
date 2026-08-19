sudo pacman -S sqlite3 python-aiohttp python-argon2-cffi

cd db
sqlite3 gensou.db < ../schema/00_schema.sql
