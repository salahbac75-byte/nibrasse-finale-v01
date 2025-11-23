-- ============================================
-- 🛡️ Migration آمن: إضافة pgvector للجداول الموجودة
-- ============================================
-- هذا السكربت آمن 100% ولن يحذف أي بيانات موجودة

-- ✅ الخطوة 1: تفعيل pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- ✅ الخطوة 2: إضافة عمود embedding للجدول الموجود "chunk"
-- استخدام IF NOT EXISTS لتجنب الخطأ إذا كان العمود موجود
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'chunk' AND column_name = 'embedding'
    ) THEN
        ALTER TABLE chunk ADD COLUMN embedding vector(768);
    END IF;
END $$;

-- ✅ الخطوة 3: إنشاء index للبحث السريع
-- DROP IF EXISTS أولاً لتجنب الخطأ
DROP INDEX IF EXISTS idx_chunk_embedding;

-- إنشاء IVFFlat index للبحث الفيكتوري السريع
CREATE INDEX idx_chunk_embedding ON chunk 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- ============================================
-- 📊 Function للبحث الفيكتوري
-- ============================================

-- حذف الـ function القديم إذا كان موجوداً (حل تعارض الأسماء)
DROP FUNCTION IF EXISTS match_chunks(vector, int, bigint);
DROP FUNCTION IF EXISTS match_chunks(vector, int);
DROP FUNCTION IF EXISTS match_chunks;

CREATE OR REPLACE FUNCTION match_chunks(
  query_embedding vector(768),
  match_count int DEFAULT 20,
  filter_document_id bigint DEFAULT NULL
)
RETURNS TABLE (
  id bigint,
  document_id bigint,
  chunk_index integer,
  content text,
  embedding_id text,
  similarity float
)
LANGUAGE SQL STABLE
AS $$
  SELECT
    chunk.id,
    chunk.document_id,
    chunk.chunk_index,
    chunk.content,
    chunk.embedding_id,
    1 - (chunk.embedding <=> query_embedding) as similarity
  FROM chunk
  WHERE 
    chunk.embedding IS NOT NULL  -- فقط الـ chunks التي لها embeddings
    AND CASE 
      WHEN filter_document_id IS NOT NULL THEN chunk.document_id = filter_document_id
      ELSE TRUE
    END
  ORDER BY chunk.embedding <=> query_embedding
  LIMIT match_count;
$$;

-- ============================================
-- 🔍 Function للتحقق من الـ Migration
-- ============================================

DROP FUNCTION IF EXISTS check_migration_status();

CREATE OR REPLACE FUNCTION check_migration_status()
RETURNS TABLE (
  table_name text,
  total_rows bigint,
  rows_with_embeddings bigint,
  percentage numeric
)
LANGUAGE SQL
AS $$
  SELECT
    'chunk'::text as table_name,
    COUNT(*) as total_rows,
    COUNT(embedding) as rows_with_embeddings,
    ROUND((COUNT(embedding)::numeric / NULLIF(COUNT(*), 0) * 100), 2) as percentage
  FROM chunk;
$$;

-- ============================================  
-- ✅ تشغيل التحقق من الحالة
-- ============================================

SELECT * FROM check_migration_status();

-- ============================================
-- 📝 Comments للتوثيق
-- ============================================

COMMENT ON COLUMN chunk.embedding IS 'Vector embedding (768 dimensions من Gemini)';
COMMENT ON FUNCTION match_chunks IS 'البحث الفيكتوري باستخدام cosine similarity';
COMMENT ON INDEX idx_chunk_embedding IS 'IVFFlat index للبحث السريع في vectors';
COMMENT ON FUNCTION check_migration_status IS 'التحقق من نسبة الـ chunks التي تم إضافة embeddings لها';
