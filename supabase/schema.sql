-- Run this once in Supabase Dashboard -> SQL Editor.
-- Keep the Supabase secret/service-role key only in GitHub Actions secrets and local .env.
create extension if not exists pgcrypto;

create table if not exists public.project_memory (
    id uuid primary key default gen_random_uuid(),
    slug text not null unique,
    title text not null,
    category text not null,
    difficulty text not null default 'Intermediate',
    estimated_days integer not null default 5 check (estimated_days between 1 and 60),
    summary text not null,
    tech_stack text[] not null default '{}',
    spec_json jsonb not null,
    brief_markdown text not null,
    research_sources jsonb not null default '[]'::jsonb,
    review_json jsonb not null default '{}'::jsonb,
    ai_provider text not null,
    status text not null default 'planned'
        check (status in ('planned', 'building', 'completed', 'skipped')),
    build_notes text not null default '',
    github_owner text not null default 'AzamAbbasi123889',
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create index if not exists project_memory_created_at_idx
    on public.project_memory (created_at desc);
create index if not exists project_memory_category_idx
    on public.project_memory (category);
create index if not exists project_memory_status_idx
    on public.project_memory (status);

alter table public.project_memory enable row level security;
revoke all on table public.project_memory from anon, authenticated;
grant all on table public.project_memory to service_role;

-- To mark a project as in progress:
-- update public.project_memory set status = 'building', updated_at = now()
-- where slug = 'your-project-slug';
-- To mark it completed and record what you learned:
-- update public.project_memory set status = 'completed',
--   build_notes = 'Implemented API, tests and deployment; add real outcomes here.',
--   updated_at = now()
-- where slug = 'your-project-slug';
