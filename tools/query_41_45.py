import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "curves.db")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("--- Intersections for 41 & 45 ---")
cursor.execute("SELECT curve_a_id, curve_b_id, intersections, relation_type FROM intersections WHERE curve_a_id = 41 OR curve_b_id = 41 OR curve_a_id = 45 OR curve_b_id = 45")
for row in cursor.fetchall():
    print(f"Pair {row[0]} intersect {row[1]}: relation={row[3]}")
    print(f"  Intersections: {row[2]}")

print("\n--- Group IDs ---")
cursor.execute("SELECT id, group_id, type, equation FROM curves WHERE id IN (41, 45)")
for row in cursor.fetchall():
    print(f"ID {row[0]} (Group {row[1]}): type={row[2]} equation={row[3]}")

conn.close()
