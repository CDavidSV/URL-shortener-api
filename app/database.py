import sqlite3

# Handle database requests
def execute_query(database_name, query, params=None, commit=False):
    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()

    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
    
    rows = cursor.fetchall()

    if commit:
        conn.commit()

    cursor.close()
    conn.close()

    return rows # Returns the response data from db