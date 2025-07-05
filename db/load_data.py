import os
import json
import psycopg2

DATA_DIR = "../data"

conn = psycopg2.connect(
    dbname="tuxemon",
    user="your_user",
    password="your_password",
    host="localhost",
    port="5432"
)
cursor = conn.cursor()

def get_or_create(table, name):
    cursor.execute(f"INSERT INTO {table} (name) VALUES (%s) ON CONFLICT (name) DO NOTHING", (name,))
    cursor.execute(f"SELECT id FROM {table} WHERE name = %s", (name,))
    return cursor.fetchone()[0]

def insert_monster(data):
    cursor.execute("""
        INSERT INTO monsters (slug, category, shape, stage, height, weight, catch_rate, lower_catch_resistance, upper_catch_resistance)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    """, (
        data["slug"], data["category"], data["shape"], data["stage"],
        data["height"], data["weight"], data["catch_rate"],
        data["lower_catch_resistance"], data["upper_catch_resistance"]
    ))
    return cursor.fetchone()[0]

def insert_many_to_many(table, monster_id, items):
    for item in items:
        item_id = get_or_create(table[:-1] + "s", item)
        cursor.execute(f"""
            INSERT INTO {table} (monster_id, {table[:-1]}_id)
            VALUES (%s, %s) ON CONFLICT DO NOTHING
        """, (monster_id, item_id))

def insert_moveset(monster_id, moveset):
    for move in moveset:
        cursor.execute("""
            INSERT INTO movesets (monster_id, level_learned, technique)
            VALUES (%s, %s, %s)
        """, (monster_id, move["level_learned"], move["technique"]))

def insert_evolutions(monster_id, evolutions):
    for evo in evolutions:
        cursor.execute("""
            INSERT INTO evolutions (monster_id, at_level, evolves_to_slug)
            VALUES (%s, %s, %s)
        """, (monster_id, evo["at_level"], evo["monster_slug"]))

def insert_history(monster_id, history):
    for h in history:
        cursor.execute("""
            INSERT INTO history (monster_id, mon_slug, evo_stage)
            VALUES (%s, %s, %s)
        """, (monster_id, h["mon_slug"], h["evo_stage"]))

for file in os.listdir(DATA_DIR):
    if file.endswith(".json"):
        with open(os.path.join(DATA_DIR, file)) as f:
            data = json.load(f)
            monster_id = insert_monster(data)
            insert_many_to_many("monster_types", monster_id, data.get("types", []))
            insert_many_to_many("monster_tags", monster_id, data.get("tags", []))
            insert_many_to_many("monster_terrains", monster_id, data.get("terrains", []))
            insert_moveset(monster_id, data.get("moveset", []))
            insert_evolutions(monster_id, data.get("evolutions", []))
            insert_history(monster_id, data.get("history", []))

conn.commit()
cursor.close()
conn.close()
print("All monsters loaded successfully!")
