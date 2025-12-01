import pytest
from unittest.mock import MagicMock, patch
from airflow.models import DagBag, TaskInstance
from airflow.utils.state import State
from airflow.utils.dates import days_ago

# Mock the SnowflakeHook to prevent actual connection attempts
@patch('airflow.providers.snowflake.hooks.snowflake.SnowflakeHook')
def test_snowflake_operator_sql_execution(mock_snowflake_hook, dagbag):
    """
    Test that the SnowflakeOperator renders the SQL template correctly
    and calls the execute method on the hook with the expected query.
    """
    # 1. Get the DAG and the task
    dag = dagbag.get_dag(dag_id='customer_summary_dag')
    task = dag.get_task(task_id='create_customer_summary')

    # 2. Create a TaskInstance to execute the task in a test context
    ti = TaskInstance(task=task, execution_date=days_ago(1))

    # 3. Render the templates (this replaces {{ params... }} in the SQL)
    ti.render_templates()

    # 4. Define the expected SQL after templating
    expected_sql = """
-- Create a summary table of customer orders
CREATE OR REPLACE TRANSIENT TABLE analytics.customer_summary_daily AS
SELECT
    c.customer_id,
    c.customer_name,
    COUNT(o.order_id) AS total_orders,
    SUM(o.order_amount) AS total_spent,
    MAX(o.order_date) AS last_order_date
FROM
    raw.orders o
JOIN
    raw.customers c ON o.customer_id = c.customer_id
GROUP BY
    c.customer_id,
    c.customer_name
HAVING
    total_orders > 0;
"""

    # 5. Mock the hook's run method and return a mock connection/cursor
    mock_hook_instance = mock_snowflake_hook.return_value
    mock_conn = mock_hook_instance.get_conn.return_value
    mock_cursor = mock_conn.cursor.return_value

    # 6. Execute the task
    task.execute(context=ti.get_template_context())

    # 7. Assertions
    # Check that the hook was initialized with the correct connection ID
    mock_snowflake_hook.assert_called_with(
        snowflake_conn_id='my_snowflake_conn',
        warehouse='COMPUTE_WH',
        database='MY_DB',
        schema='ANALYTICS',
        role=None,
        authenticator=None,
        session_parameters=None,
    )

    # Check that the run method was called once
    assert mock_hook_instance.run.call_count == 1

    # Get the actual arguments passed to the run method
    # run(sql, autocommit, parameters)
    call_args = mock_hook_instance.run.call_args[0]
    actual_sql = call_args[0]

    # Normalize whitespace for comparison (to avoid trivial failures)
    assert " ".join(actual_sql.split()) == " ".join(expected_sql.split())

    print("\nCreate table test passed successfully!")

# Optional: A simpler test to check if the DAG loads correctly
def test_dag_loads_with_no_errors(dagbag):
    dag = dagbag.get_dag(dag_id='customer_summary_dag')
    assert dag is not None
    assert len(dag.tasks) == 1
    assert dagbag.import_errors == {}
