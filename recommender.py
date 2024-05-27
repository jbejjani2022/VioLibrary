import sqlite3
import csv
import os

def convert_db_to_csv(db, csv_file, table_name):
    # Connect to the SQLite database
    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    # Execute a query to select all data from the specified table
    cursor.execute(f"SELECT * FROM {table_name}")

    # Fetch all results
    rows = cursor.fetchall()

    # Get column names
    column_names = [description[0] for description in cursor.description]

    data_folder = 'data'
    
    # Create the data folder if it doesn't exist
    if not os.path.exists(data_folder):
        os.makedirs(data_folder)
        
    # Specify the CSV file path
    csv_file = os.path.join(data_folder, f'{table_name}.csv')

    # Write data to CSV file
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        # Write header
        writer.writerow(column_names)
        # Write rows
        writer.writerows(rows)

    # Close the cursor and connection
    cursor.close()
    conn.close()

convert_db_to_csv('api.db', 'data/works.csv', 'works')
convert_db_to_csv('api.db', 'data/composers.csv', 'composers')
convert_db_to_csv('api.db', 'data/composers.csv', 'favorites')
convert_db_to_csv('api.db', 'data/composers.csv', 'libraries')