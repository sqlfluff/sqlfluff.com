"""A local DuckDB project for the SQLMesh templater worked example."""

from sqlmesh import Config

config = Config(
    model_defaults={"dialect": "duckdb"},
    default_gateway="local",
    gateways={"local": {"connection": {"type": "duckdb", "database": ":memory:"}}},
    variables={"minimum_amount": 100},
)
