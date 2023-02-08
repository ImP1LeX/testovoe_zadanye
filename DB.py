import sqlite3 as sq

async def db_start():
    global db, cur

    db = sq.connect('bot.db')
    cur = db.cursor()

    cur.execute("CREATE TABLE IF NOT EXISTS banned_users(user_id TEXT PRIMARY KEY, ban_time TEXT)")
    db.commit()
    cur.execute("""CREATE TABLE IF NOT EXISTS users_info(
    user_id TEXT PRIMARY KEY, 
    full_name TEXT, 
    msg_count INTEGER, 
    msg_time INTEGER,
    kb_text TEXT)""")
    db.commit()

async def create_user(user_id, full_name):
    user = cur.execute("SELECT 1 FROM users_info WHERE user_id == '{id}'".format(id=user_id)).fetchone()
    if not user:
        cur.execute("INSERT INTO users_info VALUES(?, ?, ?, ?, ?)", (user_id, full_name, 0, 0, 'Доллары Евро'))
        db.commit()

async def update_msg_count(user_id, msg_count):
    cur.execute("UPDATE users_info SET msg_count = '{}' WHERE user_id == '{}'".format(msg_count, user_id))
    db.commit()

async def update_msg_time(user_id, msg_time):
    cur.execute("UPDATE users_info SET msg_time = '{}' WHERE user_id == '{}'".format(msg_time, user_id))
    db.commit()

async def update_kb_text(user_id, text):
    cur.execute("UPDATE users_info SET kb_text = '{}' WHERE user_id == '{}'".format(text, user_id))
    db.commit()

async def user_select(user_id):
    cur.execute("SELECT * FROM users_info WHERE user_id == '{}'".format(user_id))
    return cur.fetchall()

async def kb_select(user_id):
    cur.execute("SELECT kb_text FROM users_info WHERE user_id == '{}'".format(user_id))
    return cur.fetchall()

async def ban_user(user_id, date):
    user = cur.execute("SELECT 1 FROM banned_users WHERE user_id == '{id}'".format(id=user_id)).fetchone()
    if not user:
        cur.execute("INSERT INTO banned_users VALUES(?, ?)", (user_id, date))
        db.commit()

async def unban_user(user_id):
    cur.execute("DELETE FROM banned_users WHERE user_id == '{}'".format(user_id))
    db.commit()

async def select_ban_user():
    cur.execute("SELECT * FROM banned_users")
    return cur.fetchall()