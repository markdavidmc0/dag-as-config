# dag-as-config
Create Airflow DAGs from a config file

## Overview
This repository generates Airflow DAGs from configuration files so DAG definitions can be managed as data (YAML/JSON) and produced at import time. DAG code lives under `dags/` grouped by tenant.

## Development (using uv)
Prerequisites
- macOS or Linux (instructions below assume macOS zsh)
- Python 3.12 (adjust if your environment differs)
- A working virtual environment

Quick local setup
```bash
uv init
```

Notes
- Project dependencies are declared in `pyproject.toml` and a lockfile is provided at `uv.lock` for reproducible installs.
- If you prefer `pip`, `poetry`, or `pip-tools`, you can use those workflows instead — the codebase doesn't require `uv` at runtime, it's just used for dependency management in development.

Running tests
```bash
# activate .venv first (see Quick local setup)
uv --add pytest
```
Tests are located in the `tests/` directory (for example `tests/test_tenant_a_ee_dag.py`).

Contributing guidelines
- Create a feature branch named `feature/<short-description>` or `fix/<short-description>`.
- Run tests locally before opening a PR.
- Keep DAGs under the appropriate tenant folder in `dags/` (for example `dags/tenant_a/`).
- Add SQL files used by DAGs into `sql/` and reference them from DAG configs or operator calls.
- Follow existing DAG patterns when adding new DAGs and add unit tests for DAG structure or logic changes.

## Using a DAG factory to create new DAG configs
This repository generates DAGs from configuration. A DAG-factory approach separates DAG structure (config) from construction (loader). Below are the recommended steps and a minimal example.

1) Install your DAG factory helper (example):
```bash
uv add dag-factory
```

2) Add a config file for the new DAG under the tenant folder, for example:
```
dags/tenant_c/my_new_dag.yaml
```

Example YAML skeleton (adjust to match your factory schema):
```yaml
dag_id: tenant_c.my_new_dag
default_args:
	owner: team
	start_date: 2025-01-01
schedule_interval: '@daily'
tasks:
	extract:
		operator: SnowflakeOperator
		sql: sql/tenant_c/extract.sql
	transform:
		operator: PythonOperator
		python_callable: my_package.my_module.transform_fn
		upstream: [extract]
```

3) Add a small Python loader that reads the YAML and generates DAG objects. Example (pseudo-code — adapt to the DAG factory library you use):
```python
from dagfactory import DagFactory

config_path = "dags/tenant_c/my_new_dag.yaml"
factory = DagFactory(config_path)
# Generate DAG objects into the module globals so Airflow can discover them
factory.generate_dags(globals())
```

4) Verify the DAG loads in Airflow and add unit tests that assert the DAG exists and expected task_ids are present. Use `scripts/test_dag_equal.py` as a reference helper.

## Helpful files and patterns
- Example DAGs:
	- `dags/tenant_a/ee_dag.py`
	- `dags/tenant_b/zoom_dag.py`
- SQL directory: `sql/`
- Test helpers and scripts: `scripts/` (for example `scripts/test_dag_equal.py`)
