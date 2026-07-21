"""Static safety checks for the Astro-only usage metering migration."""

from pathlib import Path

MIGRATION = Path("supabase/migrations/20260721161000_api_usage_metering_v1.sql")


def test_usage_migration_is_present_and_scoped_to_astro_objects() -> None:
    sql = MIGRATION.read_text(encoding="utf-8").lower()

    assert "create table if not exists public.api_rate_limit_windows" in sql
    assert "create table if not exists public.api_usage_monthly" in sql
    assert "create table if not exists public.api_usage_events" in sql
    assert "create or replace function public.api_usage_admit_v1" in sql
    assert "create or replace function public.api_usage_finalize_v1" in sql
    assert "mdms" not in sql
    assert "alter table public.profiles" not in sql
    assert "alter table public.subscriptions" not in sql


def test_usage_migration_is_service_role_only_and_rls_enabled() -> None:
    sql = MIGRATION.read_text(encoding="utf-8").lower()

    assert sql.count("enable row level security") == 3
    assert "revoke all on public.api_rate_limit_windows from anon, authenticated" in sql
    assert "revoke all on public.api_usage_monthly from anon, authenticated" in sql
    assert "revoke all on public.api_usage_events from anon, authenticated" in sql
    assert "security definer" in sql
    assert "grant execute on function public.api_usage_admit_v1" in sql
    assert "grant execute on function public.api_usage_finalize_v1" in sql
    assert "to service_role" in sql


def test_usage_migration_reserves_then_finalizes_billable_credits() -> None:
    sql = MIGRATION.read_text(encoding="utf-8").lower()

    assert "credits_reserved" in sql
    assert "outcome = 'pending'" in sql
    assert "p_response_status between 200 and 399" in sql
    assert "outcome = case when v_billable then 'succeeded' else 'failed' end" in sql
    assert "admitted_at < v_now - interval '10 minutes'" in sql
