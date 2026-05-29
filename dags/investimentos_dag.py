from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys

sys.path.append("/opt/airflow")

from etl.extract import extract_bcb, extract_frankfurter
from etl.transform import transform_data, create_dim_ativo, create_dim_data
from etl.validate import validate_data
from etl.load import load_dimensions, load_facts


default_args = {
    "owner": "grupo-investimentos",
    "retries": 1,
    "retry_delay": timedelta(minutes=1)
}


def task_extract_bcb(**context):
    df_bcb = extract_bcb()
    context["ti"].xcom_push(key="df_bcb", value=df_bcb.to_json())


def task_extract_frankfurter(**context):
    df_frankfurter = extract_frankfurter()
    context["ti"].xcom_push(
        key="df_frankfurter",
        value=df_frankfurter.to_json()
    )


def task_transform(**context):
    import pandas as pd
    from io import StringIO

    df_bcb_json = context["ti"].xcom_pull(key="df_bcb")
    df_frankfurter_json = context["ti"].xcom_pull(key="df_frankfurter")

    df_bcb = pd.read_json(StringIO(df_bcb_json))
    df_frankfurter = pd.read_json(StringIO(df_frankfurter_json))

    df_final = transform_data(df_bcb, df_frankfurter)
    df_ativo = create_dim_ativo(df_final)
    df_data = create_dim_data(df_final)

    df_final["data"] = df_final["data"].astype(str)
    df_data["data"] = df_data["data"].astype(str)

    context["ti"].xcom_push(key="df_final", value=df_final.to_json())
    context["ti"].xcom_push(key="df_ativo", value=df_ativo.to_json())
    context["ti"].xcom_push(key="df_data", value=df_data.to_json())


def task_validate(**context):
    import pandas as pd
    from io import StringIO

    df_final_json = context["ti"].xcom_pull(key="df_final")
    df_final = pd.read_json(StringIO(df_final_json))

    validate_data(df_final)


def task_load(**context):
    import pandas as pd
    from io import StringIO

    df_final = pd.read_json(StringIO(context["ti"].xcom_pull(key="df_final")))
    df_ativo = pd.read_json(StringIO(context["ti"].xcom_pull(key="df_ativo")))
    df_data = pd.read_json(StringIO(context["ti"].xcom_pull(key="df_data")))

    df_final["data"] = pd.to_datetime(df_final["data"]).dt.date
    df_data["data"] = pd.to_datetime(df_data["data"]).dt.date

    load_dimensions(df_ativo, df_data)
    load_facts(df_final)


with DAG(
    dag_id="monitor_investimentos_global",
    default_args=default_args,
    start_date=datetime(2026, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    tags=["cambio", "etl", "investimentos"]
) as dag:

    extract_bcb_task = PythonOperator(
        task_id="extract_bcb",
        python_callable=task_extract_bcb
    )

    extract_frankfurter_task = PythonOperator(
        task_id="extract_frankfurter",
        python_callable=task_extract_frankfurter
    )

    transform_task = PythonOperator(
        task_id="transform_data",
        python_callable=task_transform
    )

    validate_task = PythonOperator(
        task_id="validate_data_quality",
        python_callable=task_validate
    )

    load_task = PythonOperator(
        task_id="load_postgres",
        python_callable=task_load
    )

    [extract_bcb_task, extract_frankfurter_task] >> transform_task >> validate_task >> load_task