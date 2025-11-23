-- ============================================
-- Supabase Schema مع pgvector للهجرة من ChromaDB
-- ============================================

-- تفعيل pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- جدول المستندات (موجود مسبقاً)
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    filename TEXT NOT NULL,
    total_chunks INTEGER,
    upload_date TIMESTAMP DEFAULT NOW()
);

-- جدول الـ chunks مع دعم pgvector
CREATE TABLE IF NOT EXISTS chunks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER,
    content TEXT NOT NULL,
    embedding_id TEXT,
    embedding vector(768)  -- ✅ الجديد: عمود embeddings (768 dimension لـ Gemini)
);

-- Indexes للأداء
CREATE INDEX IF NOT EXISTS idx_chunks_document_id ON chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_chunks_embedding_id ON chunks(embedding_id);

-- ✅ Index للبحث الفيكتوري السريع
CREATE INDEX IF NOT EXISTS idx_chunks_embedding ON chunks 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- ============================================
-- Function للبحث الفيكتوري (Vector Search)
-- ============================================

CREATE OR REPLACE FUNCTION match_chunks(
  query_embedding vector(768),
  match_count int DEFAULT 20,
  filter_document_id uuid DEFAULT NULL
)
RETURNS TABLE (
  id uuid,
  document_id uuid,
  chunk_index integer,
  content text,
  embedding_id text,
  similarity float
)
LANGUAGE SQL STABLE
AS $$
  SELECT
    chunks.id,
    chunks.document_id,
    chunks.chunk_index,
    chunks.content,
    chunks.embedding_id,
    1 - (chunks.embedding <=> query_embedding) as similarity
  FROM chunks
  WHERE 
    CASE 
      WHEN filter_document_id IS NOT NULL THEN chunks.document_id = filter_document_id
      ELSE TRUE
    END
  ORDER BY chunks.embedding <=> query_embedding
  LIMIT match_count;
$$;

-- ============================================
-- Helper Functions
-- ============================================

-- Function لحساب عدد chunks لمستند معين
CREATE OR REPLACE FUNCTION count_document_chunks(doc_id uuid)
RETURNS integer
LANGUAGE SQL STABLE
AS $$
  SELECT COUNT(*)::integer
  FROM chunks
  WHERE document_id = doc_id;
$$;

-- Function للحصول على إحصائيات النظام
CREATE OR REPLACE FUNCTION get_system_stats()
RETURNS TABLE (
  total_documents bigint,
  total_chunks bigint,
  total_embeddings bigint,
  avg_chunks_per_document numeric
)
LANGUAGE SQL STABLE
AS $$
  SELECT
    COUNT(DISTINCT d.id) as total_documents,
    COUNT(c.id) as total_chunks,
    COUNT(c.embedding) as total_embeddings,
    ROUND(COUNT(c.id)::numeric / NULLIF(COUNT(DISTINCT d.id), 0), 2) as avg_chunks_per_document
  FROM documents d
  LEFT JOIN chunks c ON d.id = c.document_id;
$$;

-- ============================================
-- Comments للتوثيق
-- ============================================

COMMENT ON TABLE documents IS 'جدول المستندات المرفوعة';
COMMENT ON TABLE chunks IS 'جدول مقاطع النصوص مع embeddings';
COMMENT ON COLUMN chunks.embedding IS 'Vector embedding (768 dimensions من Gemini)';
COMMENT ON FUNCTION match_chunks IS 'البحث الفيكتوري باستخدام cosine similarity';
COMMENT ON INDEX idx_chunks_embedding IS 'IVFFlat index للبحث السريع في vectors';
