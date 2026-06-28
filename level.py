import sqlite3
import random
import time

# ==========================
# CONFIGURAÇÕES
# ==========================

XP_MIN = 15
XP_MAX = 25

COOLDOWN = 5

BOOSTER_MULTIPLIER = 2

# ==========================

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS levels(
    user_id INTEGER PRIMARY KEY,
    xp INTEGER NOT NULL DEFAULT 0,
    level INTEGER NOT NULL DEFAULT 0
)
""")

conn.commit()

cooldowns = {}


def xp_needed(level):
    return 5 * (level ** 2) + 50 * level + 100


def get_user(user_id):

    cursor.execute(
        "SELECT xp, level FROM levels WHERE user_id=?",
        (user_id,)
    )

    data = cursor.fetchone()

    if data is None:

        cursor.execute(
            "INSERT INTO levels(user_id,xp,level) VALUES(?,?,?)",
            (user_id, 0, 0)
        )

        conn.commit()

        return 0, 0

    return data


async def add_xp(member):

    agora = time.time()

    if member.id in cooldowns:
        if agora - cooldowns[member.id] < COOLDOWN:
            return False

    cooldowns[member.id] = agora

    xp, level = get_user(member.id)

    print(f"{member} | XP: {xp} | LEVEL: {level}")

    ganho = random.randint(XP_MIN, XP_MAX)

    # Booster ganha 2x XP
    if member.premium_since:
        ganho = int(ganho * BOOSTER_MULTIPLIER)

    xp += ganho

    upou = False

    while xp >= xp_needed(level):

        xp -= xp_needed(level)

        level += 1

        upou = True

    cursor.execute(
        "UPDATE levels SET xp=?, level=? WHERE user_id=?",
        (xp, level, member.id)
    )

    conn.commit()

    print(f"RETORNANDO -> upou={upou}, level={level}, xp={xp}")

    return upou, level, xp
