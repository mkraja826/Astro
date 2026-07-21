"""Static contract tests for the non-mutating usage health RPC migration."""

from pathlib import Path

MIGRATION = Path(
    "supabase/migrations/20260721173000_api_usage_health_v1.sql"
)


def test_usage_health_rpc_is_non_mutating_and_service_role_only() -> None:
    sql = MIGRATION.read_text(encoding="utf-8").lower()

    assert "create or replace function public.api_usage_health_v1()" in sql
    assert "language sql" in sql
    assert "stable" in sql
    assert "security definer" in sql
    assert "to_regclass('public.api_rate_limit_windows')" in sql
    assert "to_regclass('public.api_usage_monthly')" in sql
    assert "to_regclass('public.api_usage_events')" in sql
    assert "hdaugtypjpniesdgyral" in sql
    assert "api_usage_metering_safety_v1" in sql
    assert "revoke all on function public.api_usage_health_v1()" in sql
    assert "grant execute on function public.api_usage_health_v1()" in sql
    assert "to service_role" in sql

    forbidden = ("insert into", "update public.", "delete from", "truncate ")
    assert not any(statement in sql for statement in forbidden)
