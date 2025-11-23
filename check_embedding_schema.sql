-- التحقق من schema عمود embedding في chunks_v2

-- طريقة 1: التحقق من النوع الكامل
SELECT 
    column_name,
    data_type,
    udt_name,
    character_maximum_length,
    pg_catalog.format_type(a.atttypid, a.atttypmod) as full_data_type
FROM information_schema.columns c
JOIN pg_catalog.pg_attribute a ON a.attname = c.column_name
WHERE 
    c.table_name = 'chunks_v2' 
    AND c.column_name = 'embedding'
    AND a.attrelid = 'chunks_v2'::regclass;

-- طريقة 2: التحقق المباشر من pg_attribute
SELECT 
    a.attname AS column_name,
    pg_catalog.format_type(a.atttypid, a.atttypmod) AS data_type,
    a.atttypmod
FROM pg_catalog.pg_attribute a
WHERE 
    a.attrelid = 'chunks_v2'::regclass 
    AND a.attname = 'embedding'
    AND NOT a.attisdropped;
