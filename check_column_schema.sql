-- التحقق من schema العمود embedding في Supabase
-- نفذ هذا في Supabase SQL Editor

SELECT 
    column_name,
    data_type,
    udt_name,
    character_maximum_length
FROM information_schema.columns
WHERE table_name = 'chunk' AND column_name = 'embedding';

-- أيضاً، التحقق من vector type
SELECT 
    a.attname as column_name,
    pg_catalog.format_type(a.atttypid, a.atttypmod) as data_type
FROM pg_catalog.pg_attribute a
WHERE 
    a.attrelid = 'chunk'::regclass 
    AND a.attname = 'embedding'
    AND NOT a.attisdropped;
