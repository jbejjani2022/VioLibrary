import sqlite3
import os
import csv

def convert_db_to_csv(db, table_name):
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
        print("db converted to fresh csv")

    # Close the cursor and connection
    cursor.close()
    conn.close()
    
    
# current_directory = os.path.dirname(os.path.abspath(__file__))
# # Construct the path to api.db
# db_path = os.path.join(current_directory, '..', 'api.db')
# # Transfer most up to date favorites data to .csv
# convert_db_to_csv(db_path, 'favorites')