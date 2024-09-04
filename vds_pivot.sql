import pyodbc
from datetime import datetime, timedelta
import pandas as pd

# Dremio connection details
conn = pyodbc.connect(
    "Driver={Dremio ODBC Driver 64-bit};"
    "ConnectionType=Direct;"
    "HOST=your_host;"
    "PORT=31010;"
    "AuthenticationType=Plain;"
    "UID=your_username;"
    "PWD=your_personal_access_token;"
    "SSL=1;"
    "SSLTrustStorePath=path_to_truststore;"
)

cursor = conn.cursor()

# Define the date range
start_date = datetime(2023, 1, 1)
end_date = datetime(2023, 1, 10)
date_range = [start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1)]

# Retrieve the list of table names
cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'your_schema'")
table_names = [row.table_name for row in cursor.fetchall()]

# Initialize a DataFrame to store the results
results_df = pd.DataFrame(columns=['Table', 'Date', 'RowCount'])

# Iterate over each table name and date
for table in table_names:
    for date in date_range:
        query = f"""
        SELECT COUNT(*) FROM your_schema.{table}
        WHERE DATE(column_name) = '{date.strftime('%Y-%m-%d')}'
        """
        cursor.execute(query)
        row_count = cursor.fetchone()[0]
        results_df = results_df.append({'Table': table, 'Date': date.strftime('%Y-%m-%d'), 'RowCount': row_count}, ignore_index=True)

# Close the cursor and connection
cursor.close()
conn.close()

# Display the combined results
print(results_df)
