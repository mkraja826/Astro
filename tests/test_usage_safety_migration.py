"""Static checks for the request identity safety migration."""

from pathlib import Path

MIGRATION = Path("supabase/migrations/20260721170000_api_usage_metering_safety_v1.sql")


def test_safety_migration_serializes_global_request_ids() -> None:
    sql = MIGRATION.read_text(encoding="utf-8").lower()

    assert "'request:' || p_request_id" in sql
    assert "request_id_reused" in sql
    assert "where request_id = p_request_id" in sql
    assert "'allowed', false" in sql


def test_safety_migration_validates_consumer_and_initial_quota() -> None:
    sql = MIGRATION.read_text(encoding="utf-8").lower()

    assert "if p_consumer_id is null" in sql
    assert "p_credit_cost <= p_monthly_credit_limit" in sql
    assert "p_monthly_credit_limit = 0" in sql


def test_safety_migration_remains_service_role_only() -> None:
    sql = MIGRATION.read_text(encoding="utf-8").lower()

    assert "security definer" in sql
    assert "set search_path = public, pg_temp" in sql
    assert "from public, anon, authenticated" in sql
    assert "to service_role" in sql
    assert "mdms" not in sql
