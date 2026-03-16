import sqlite3

def check_db():
    conn = sqlite3.connect('ultraxpert.db')
    cursor = conn.cursor()
    
    # Check if downloads table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='downloads';")
    table_exists = cursor.fetchone()
    print(f"Table 'downloads' exists: {bool(table_exists)}")
    
    if table_exists:
        cursor.execute("SELECT COUNT(*) FROM downloads;")
        count = cursor.fetchone()[0]
        print(f"Number of records in 'downloads': {count}")
        
        cursor.execute("SELECT * FROM downloads;")
        rows = cursor.fetchall()
        for row in rows:
            print(row)
    
    conn.close()

if __name__ == "__main__":
    check_db()
