--To copy data from a local directory to a Hive table, you can use the LOAD DATA command
LOAD DATA LOCAL INPATH '/path/to/local/file.csv' INTO TABLE your_table_name;

--This command will export the data from your_table_name into the specified local directory in CSV format.
INSERT OVERWRITE LOCAL DIRECTORY '/home/user/employees_data'
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
SELECT * FROM employees;

#!/bin/bash
# Extract job names and target table names from JIL file

# Define the JIL file
JIL_FILE="all_jobs.jil"

# Parse the JIL file
awk '
BEGIN { FS=": " }
/insert_job/ { job_name=$2 }
/command/ { command=$2; print job_name, command }
' $JIL_FILE > job_details.txt

