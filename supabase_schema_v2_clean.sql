-- ============================================
-- 🆕 Schema جديد نظيف - Supabase pgvector
-- ============================================
-- جداول جديدة منفصلة تماماً عن القديمة
-- بعد نجاح الاختبارات، سيتم حذف القديمة وإعادة تسمية هذه

-- ============================================
-- الخطوة 1: تفعيل pgvector (إذا لم يكن مفعل)
-- ============================================
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================
-- الخطوة 2: إنشاء جدول documents_v2
-- ============================================
CREATE TABLE IF NOT EXISTS documents_v2 (
    id BIGSERIAL PRIMARY KEY,
    filename TEXT NOT NULL,
    upload_date TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    total_chunks INTEGER NOT NULL
);

-- ============================================
-- الخطوة 3: إنشاء جدول chunks_v2 مع pgvector
-- ============================================
CREATE TABLE IF NOT EXISTS chunks_v2 (
    id BIGSERIAL PRIMARY KEY,
    document_id BIGINT REFERENCES documents_v2(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    embedding_id TEXT NOT NULL,
    embedding vector(768) NOT NULL  -- ⚠️ CRITICAL: محدد بوضوح 768 فقط!
);

-- ============================================
-- الخطوة 4: Indexes للأداء
-- ============================================

-- Index على document_id للـ foreign key
CREATE INDEX IF NOT EXISTS idx_chunks_v2_document_id ON chunks_v2(document_id);

-- Index على embedding_id
CREATE INDEX IF NOT EXISTS idx_chunks_v2_embedding_id ON chunks_v2(embedding_id);

-- ⭐ Index للبحث الفيكتوري السريع (IVFFlat)
CREATE INDEX IF NOT EXISTS idx_chunks_v2_embedding ON chunks_v2 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- ============================================
-- الخطوة 5: Functions للبحث والإحصائيات
-- ============================================

-- حذف الـ functions القديمة إذا كانت موجودة
DROP FUNCTION IF EXISTS match_chunks_v2(vector, int, bigint);
DROP FUNCTION IF EXISTS match_chunks_v2(vector, int);
DROP FUNCTION IF EXISTS match_chunks_v2;

-- Function للبحث الفيكتوري
CREATE OR REPLACE FUNCTION match_chunks_v2(
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
    chunks_v2.id,
    chunks_v2.document_id,
    chunks_v2.chunk_index,
    chunks_v2.content,
    chunks_v2.embedding_id,
    1 - (chunks_v2.embedding <=> query_embedding) as similarity
  FROM chunks_v2
  WHERE 
    CASE 
      WHEN filter_document_id IS NOT NULL THEN chunks_v2.document_id = filter_document_id
      ELSE TRUE
    END
  ORDER BY chunks_v2.embedding <=> query_embedding
  LIMIT match_count;
$$;

-- Function للإحصائيات
DROP FUNCTION IF EXISTS check_migration_status_v2();

CREATE OR REPLACE FUNCTION check_migration_status_v2()
RETURNS TABLE (
  table_name text,
  total_rows bigint,
  rows_with_embeddings bigint,
  percentage numeric
)
LANGUAGE SQL
AS $$
  SELECT
    'chunks_v2'::text as table_name,
    COUNT(*) as total_rows,
    COUNT(embedding) as rows_with_embeddings,
    ROUND((COUNT(embedding)::numeric / NULLIF(COUNT(*), 0) * 100), 2) as percentage
  FROM chunks_v2;
$$;

-- ============================================
-- الخطوة 6: التحقق من Schema
-- ============================================

-- عرض معلومات عمود embedding
SELECT 
    column_name,
    data_type,
    udt_name,
    pg_catalog.format_type(a.atttypid, a.atttypmod) as full_type
FROM information_schema.columns c
JOIN pg_catalog.pg_attribute a ON a.attname = c.column_name
WHERE 
    c.table_name = 'chunks_v2' 
    AND c.column_name = 'embedding'
    AND a.attrelid = 'chunks_v2'::regclass;

-- ============================================
-- الخطوة 7: Comments للتوثيق
-- ============================================

COMMENT ON TABLE documents_v2 IS 'جدول المستندات (النسخة الجديدة النظيفة)';
COMMENT ON TABLE chunks_v2 IS 'جدول النصوص مع embeddings - pgvector 768 dimensions';
COMMENT ON COLUMN chunks_v2.embedding IS 'Vector embedding: بالضبط 768 dimensions من Gemini';
COMMENT ON FUNCTION match_chunks_v2 IS 'البحث الفيكتوري باستخدام cosine similarity';
COMMENT ON INDEX idx_chunks_v2_embedding IS 'IVFFlat index للبحث السريع';

-- ============================================
-- ✅ التحقق النهائي
-- ============================================

SELECT 'Schema v2 جاهز للاستخدام!' as status;
