WITH virtual_datasets AS (
SELECT
TABLE_SCHEMA,
TABLE_NAME
FROM
INFORMATION_SCHEMA."TABLES"
WHERE
TABLE_TYPE = 'VIEW'
AND TABLE_SCHEMA = 'your_space_name'
),
dataset_info AS (
SELECT
vd.TABLE_SCHEMA,
vd.TABLE_NAME,
COUNT(*) AS row_count,
MAX(CASE WHEN c.COLUMN_NAME LIKE '%date%' THEN c.COLUMN_NAME ELSE NULL END) AS date_column
FROM
virtual_datasets vd
JOIN
INFORMATION_SCHEMA."COLUMNS" c
ON
vd.TABLE_SCHEMA = c.TABLE_SCHEMA
AND vd.TABLE_NAME = c.TABLE_NAME
GROUP BY
vd.TABLE_SCHEMA, vd.TABLE_NAME
)
SELECT
TABLE_SCHEMA,
TABLE_NAME,
row_count,
date_column,
TABLE_NAME AS view_name
FROM
dataset_info;

--Pivot

SELECT
date_column,
MAX(CASE WHEN view_name = 'dataset1' THEN row_count ELSE NULL END) AS dataset1,
MAX(CASE WHEN view_name = 'dataset2' THEN row_count ELSE NULL END) AS dataset2,
-- Add more datasets as needed
FROM (
SELECT
TABLE_SCHEMA,
TABLE_NAME,
row_count,
date_column,
TABLE_NAME AS view_name
FROM
dataset_info
) AS source
GROUP BY
date_column;