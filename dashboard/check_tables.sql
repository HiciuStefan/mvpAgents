-- Check if tables exist and their structure
SELECT table_name, column_name, data_type 
FROM information_schema.columns 
WHERE table_schema = 'public' 
  AND table_name IN ('deai_processed_items', 'deai_website', 'deai_email', 'deai_twitter')
ORDER BY table_name, ordinal_position;

-- Alternative: List all tables
SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name LIKE 'deai_%'; 