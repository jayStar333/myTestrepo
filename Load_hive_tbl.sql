import requests
import pandas as pd
from datetime import datetime, timedelta

# Define the Dremio server and personal access token
dremio_server = 'https://your-dremio-server.com'
personal_access_token = 'your_personal_access_token'

# Disable SSL verification
requests.packages.urllib3.disable_warnings()

# Function to get the list of VDS
def get_vds_list():
    query = "SELECT table_name FROM information_schema.tables WHERE table_type = 'VIRTUAL'"
    response = requests.post(
        f"{dremio_server}/api/v3/sql",
        headers={'Authorization': f'_dremio{personal_access_token}'},
        json={'sql': query},
        verify=False
    )
    response.raise_for_status()
    return [row['table_name'] for row in response.json()['rows']]

# Function to get date counts for each VDS
def get_date_counts(vds, start_date, end_date):
    query = f"""
    SELECT CAST(date_column AS DATE) AS date, COUNT(*) AS count
    FROM {vds}
    WHERE date_column BETWEEN '{start_date}' AND '{end_date}'
    GROUP BY CAST(date_column AS DATE)
    """
    response = requests.post(
        f"{dremio_server}/api/v3/sql",
        headers={'Authorization': f'_dremio{personal_access_token}'},
        json={'sql': query},
        verify=False
    )
    response.raise_for_status()
    return response.json()['rows']

# Generate date range for the past 7 days
end_date = datetime.now().date()
start_date = end_date - timedelta(days=7)
date_range = pd.date_range(start=start_date, end=end_date)

# Get the list of VDS
vds_list = get_vds_list()

# Collect data for each VDS
data = []
for vds in vds_list:
    date_counts = get_date_counts(vds, start_date, end_date)
    for row in date_counts:
        data.append({'vds': vds, 'date': row['date'], 'count': row['count']})

# Create a DataFrame and pivot it
df = pd.DataFrame(data)
pivot_df = df.pivot_table(index='vds', columns='date', values='count', fill_value=0)

# Convert the pivot table to HTML with CSS styling
html_table = pivot_df.to_html(classes='table table-striped', border=0, index=False)

# Define CSS styles
css_styles = """
<style>
.table {
    width: 100%;
    border-collapse: collapse;
}
.table th, .table td {
    border: 1px solid #ddd;
    padding: 8px;
}
.table th {
    background-color: #f2f2f2;
    text-align: left;
}
</style>
"""

# Combine HTML and CSS
html_output = css_styles + html_table

# Save the HTML output to a file
with open('dremio_vds_report.html', 'w') as file:
    file.write(html_output)

print("HTML report generated successfully!")
