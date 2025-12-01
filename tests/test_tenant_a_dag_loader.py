import importlib


def test_tenant_a_dags_loaded():
    """Import the tenant_a dag_loader and assert DAG objects are created.

    The loader uses `dagfactory.load_yaml_dags` to populate the module globals
    with Airflow `DAG` objects based on YAML files in `yml_definitions/`.
    This test imports the loader module (which triggers DAG creation) and
    verifies at least two DAG objects were produced and that they contain
    the expected task ids defined in the YAML examples.
    """
    mod = importlib.import_module("tenant_a.dag_loader")

    try:
        from airflow.models import DAG
    except Exception as exc:  # pragma: no cover - environment may not have Airflow
        raise RuntimeError(
            "Airflow must be installed in the test environment to run this test"
        ) from exc

    dags = [obj for obj in vars(mod).values() if isinstance(obj, DAG)]

    assert len(dags) >= 2, "Expected at least two DAG objects to be created"

    expected_tasks = {"task_1", "task_2", "example_task_group.task_3"}
    for dag in dags:
        task_ids = {t.task_id for t in dag.tasks}
        assert expected_tasks.issubset(task_ids), (
            f"DAG {getattr(dag, 'dag_id', repr(dag))} missing expected tasks"
        )
