import os
import sys
import json
import sqlite3

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "curves.db")

def print_statistics(conn):
    cursor = conn.cursor()
    
    print("=" * 60)
    print("                CURVES DATABASE STATISTICS")
    print("=" * 60)
    
    # Total curves
    cursor.execute("SELECT COUNT(*) FROM curves;")
    total_curves = cursor.fetchone()[0]
    print(f"Total Curves: {total_curves:,}")
    
    # Curves by type
    print("\nCurves by Type:")
    cursor.execute("SELECT type, COUNT(*) FROM curves GROUP BY type ORDER BY COUNT(*) DESC;")
    for row in cursor.fetchall():
        print(f"  - {row[0]:<20}: {row[1]:,}")
        
    # Total intersecting pairs
    cursor.execute("SELECT COUNT(*) FROM intersections;")
    total_intersections = cursor.fetchone()[0]
    print(f"\nTotal Recorded Intersecting Pairs (Sparse Matrix): {total_intersections:,}")
    
    # Intersections by relation type
    print("\nIntersections by Relationship Type:")
    cursor.execute("SELECT relation_type, COUNT(*) FROM intersections GROUP BY relation_type ORDER BY COUNT(*) DESC;")
    for row in cursor.fetchall():
        print(f"  - {row[0]:<20}: {row[1]:,}")
        
    # Total points of intersection across all pairs
    cursor.execute("SELECT intersections FROM intersections;")
    total_points = sum(len(json.loads(row[0])) for row in cursor.fetchall())
    print(f"Total Intersection Points Resolved: {total_points:,}")
    print("=" * 60)

def query_group(conn, group_id):
    cursor = conn.cursor()
    print(f"\n--- Details for Spatial Group #{group_id} ---")
    
    # Fetch curves
    cursor.execute("SELECT id, type, equation, endpoints FROM curves WHERE group_id = ?;", (group_id,))
    curves = cursor.fetchall()
    
    print("\nCurves:")
    for c in curves:
        eps = json.loads(c[3])
        print(f"  ID {c[0]:<5} | Type: {c[1]:<12} | Equation: {c[2]}")
        if eps:
            print(f"    Endpoints: {eps}")
            
    # Fetch intersections
    curve_ids = [c[0] for c in curves]
    if not curve_ids:
        print("No curves in this group.")
        return
        
    placeholders = ",".join("?" for _ in curve_ids)
    query = f"""
    SELECT curve_a_id, curve_b_id, intersections, relation_type
    FROM intersections
    WHERE curve_a_id IN ({placeholders}) AND curve_b_id IN ({placeholders});
    """
    
    cursor.execute(query, curve_ids + curve_ids)
    intersections = cursor.fetchall()
    
    print("\nIntersections:")
    if not intersections:
        print("  No intersections in this group.")
    for inter in intersections:
        pts = json.loads(inter[2])
        print(f"  Curves {inter[0]} intersect {inter[1]} | Type: {inter[3]} | Intersections found: {len(pts)}")
        for i, pt in enumerate(pts):
            print(f"    Point #{i+1}: ({pt[0]:.6f}, {pt[1]:.6f})")

def main():
    if not os.path.exists(DB_PATH):
        print(f"Error: curves.db does not exist at '{DB_PATH}'. Please run tools/generate_curve_dataset.py first.")
        sys.exit(1)
        
    conn = sqlite3.connect(DB_PATH)
    
    # Print general stats
    print_statistics(conn)
    
    # Query sample groups targeting different edge cases
    # Group 1: Radicals/Semicircles (Endpoint stress-test)
    # Group 2: Tangents/Touches
    # Group 3: Near-misses
    for sample_group in [1, 2, 3]:
        query_group(conn, sample_group)
        
    conn.close()

if __name__ == "__main__":
    main()
