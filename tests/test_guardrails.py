import pytest
from app.services.guardrails import validate_sql


def test_validate_sql_accepts_select():
    validate_sql("SELECT * FROM payments")


def test_validate_sql_accepts_with():
    validate_sql("WITH x AS (SELECT 1 AS a) SELECT * FROM x")


def test_validate_sql_rejects_update():
    with pytest.raises(ValueError):
        validate_sql("UPDATE payments SET amount = 0")


def test_validate_sql_rejects_drop():
    with pytest.raises(ValueError):
        validate_sql("DROP TABLE payments")
