import sys
import sqlite3
import sympy as sp
import time

sys.path.append('.')
from tools.compare_solutions_suite import run_database_case, generate_markdown_report

def main():
    # Setup Sympy symbols
    x_sym, y_sym = sp.symbols('x y', real=True)
    
    # 1. Connect to benchmark results DB
    conn_res = sqlite3.connect("benchmark_results.db")
    cursor_res = conn_res.cursor()
    
    # 2. Connect to curves DB
    conn_db = sqlite3.connect("curves.db")
    cursor_db = conn_db.cursor()
    
    target_rows = [185, 294]
    
    for row_id in target_rows:
        print(f"Running database case for rowid {row_id}...")
        cursor_db.execute("""
            SELECT rowid, curve_a_id, curve_b_id, intersections, relation_type
            FROM intersections
            WHERE rowid = ?
        """, (row_id,))
        row = cursor_db.fetchone()
        if not row:
            print(f"Row {row_id} not found in curves.db")
            continue
            
        res = run_database_case(row, cursor_db, x_sym, y_sym)
        print(f"Result for rowid {row_id}:")
        print(f"  Expected count: {res['expected_count']}, Analytical: {res['analytical_count']} (Pass: {res['analytical_pass']}, Msg: {res['analytical_msg']})")
        print(f"  Graphics: {res['graphics_count']} (Pass: {res['graphics_pass']}, Msg: {res['graphics_msg']})")
        
        # Save to persistent database
        cursor_res.execute("""
            INSERT OR REPLACE INTO benchmark_progress (rowid, curve_a_id, curve_b_id, expected_count, analytical_count,
                                                       analytical_time, analytical_pass, analytical_msg,
                                                       graphics_count, graphics_time, graphics_pass, graphics_msg)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (res['rowid'], res['curve_a_id'], res['curve_b_id'], res['expected_count'], res['analytical_count'],
              res['analytical_time'], res['analytical_pass'], res['analytical_msg'],
              res['graphics_count'], res['graphics_time'], res['graphics_pass'], res['graphics_msg']))
        conn_res.commit()
        
    print("Regenerating markdown report...")
    generate_markdown_report(conn_res)
    
    conn_db.close()
    conn_res.close()
    print("Done!")

if __name__ == "__main__":
    main()
