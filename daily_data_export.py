import sqlite3
import pandas as pd
from datetime import datetime

def export_data():
    conn = sqlite3.connect('fraud_detection.db')

    for table in ['users', 'reports', 'feedback']:
        df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
        filename = f'backup/{table}_backup_{datetime.now().strftime("%Y%m%d")}.csv'
        df.to_csv(filename, index=False)
    
    conn.close()
    print("✅ Backup completed.")

if __name__ == '__main__':
    export_data()
