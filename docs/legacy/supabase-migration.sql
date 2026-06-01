-- Enable the pgvector extension
create extension if not exists vector;

-- Main document store
create table if not exists workspace_documents (
  id bigserial primary key,
  content text not null,
  embedding vector(768),
  metadata jsonb not null default '{}',
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- IVFFlat index for fast cosine similarity search
create index if not exists idx_workspace_documents_embedding
  on workspace_documents
  using ivfflat (embedding vector_cosine_ops)
  with (lists = 100);

-- Index on metadata for filtered queries
create index if not exists idx_workspace_documents_metadata
  on workspace_documents
  using gin (metadata);

-- Similarity search function
create or replace function match_documents(
  query_embedding vector(768),
  match_threshold float default 0.7,
  match_count int default 10,
  filter_metadata jsonb default '{}'
)
returns table (
  id bigint,
  content text,
  metadata jsonb,
  similarity float
)
language plpgsql as $$
begin
  return query
  select
    wd.id,
    wd.content,
    wd.metadata,
    1 - (wd.embedding <=> query_embedding) as similarity
  from workspace_documents wd
  where 1 - (wd.embedding <=> query_embedding) > match_threshold
    and (filter_metadata = '{}' or wd.metadata @> filter_metadata)
  order by wd.embedding <=> query_embedding
  limit match_count;
end;
$$;

-- Upsert helper: update embedding if source_path + chunk_index already exists
create or replace function upsert_document(
  p_content text,
  p_embedding vector(768),
  p_metadata jsonb
)
returns void
language plpgsql as $$
begin
  insert into workspace_documents (content, embedding, metadata, updated_at)
  values (p_content, p_embedding, p_metadata, now())
  on conflict ((metadata->>'source_path'), ((metadata->>'chunk_index')::int))
  do update set
    content = excluded.content,
    embedding = excluded.embedding,
    metadata = excluded.metadata,
    updated_at = now();
exception
  when others then
    insert into workspace_documents (content, embedding, metadata, updated_at)
    values (p_content, p_embedding, p_metadata, now());
end;
$$;
