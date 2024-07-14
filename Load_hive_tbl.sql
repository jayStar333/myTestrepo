--To copy data from a local directory to a Hive table, you can use the LOAD DATA command
LOAD DATA LOCAL INPATH '/path/to/local/file.csv' INTO TABLE your_table_name;

--This command will export the data from your_table_name into the specified local directory in CSV format.
INSERT OVERWRITE LOCAL DIRECTORY '/home/user/employees_data'
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
SELECT * FROM employees;
