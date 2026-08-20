# GensouDB
A Python-based webserver with an underlying SQLite3 database.

## Install on Windows
1. Install the latest version of [Python](https://www.python.org/downloads/)
2. Run `setup_win.bat`

## Install on Arch
1. Run setup_arch.sh

## Install on other Linux distributions
1. Methods may vary. You need SQLite3, Python, and the Python packages `aiohttp` and `argon2-cffi`.
2. Inside the `db` folder, run `sqlite3 gensou.db < schema.sql`

## Initialize database
1. The admin user is "cipher" with ID 0. It does not yet have a password.
