from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys

sys.path.append("/opt/airflow")

from etl.extract import extract_bcb, extract_coingecko
from etl.transform import transform_data, create_dim_ativo, create_dim_data
from etl.validate import validate_data
from etl.load import load_dimensions, load_facts


default_args = {
    "owner": "grupo-investimentos",
    "retries": 2,
    "retry_delay": timedelta(minutes=2)
}


def task_extract_bcb(**context):
    df_bcb = extract_bcb()
    context["ti"].xcom_push(key="df_bcb", value=df_bcb.to_json())


def task_extract_coingecko(**context):
    df_coingecko = extract_coingecko()
    context["ti"].xcom_push(key="df_coingecko", value=df_coingecko.to_json())


def task_transform(**context):
    import pandas as pd

    df_bcb_json = context["ti"].xcom_pull(key="df_bcb")
    df_coingecko_json = context["ti"].xcom_pull(key="df_coingecko")

    df_bcb = pd.read_json(df_bcb_json)
    df_coingecko = pd.read_json(df_coingecko_json)

    df_final = transform_data(df_bcb, df_coingecko)
    df_ativo = create_dim_ativo(df_final)
    df_data = create_dim_data(df_final)

    context["ti"].xcom_push(key="df_final", value=df_final.to_json())
    context["ti"].xcom_push(key="df_ativo", value=df_ativo.to_json())
    context["ti"].xcom_push(key="df_data", value=df_data.to_json())


def task_validate(**context):
    import pandas as pd

    df_final_json = context["ti"].xcom_pull(key="df_final")
    df_final = pd.read_json(df_final_json)

    validate_data(df_final)


def task_load(**context):
    import pandas as pd

    df_final = pd.read_json(context["ti"].xcom_pull(key="df_final"))
    df_ativo = pd.read_json(context["ti"].xcom_pull(key="df_ativo"))
    df_data = pd.read_json(context["ti"].xcom_pull(key="df_data"))

    load_dimensions(df_ativo, df_data)
    load_facts(df_final)


with DAG(
    dag_id="monitor_investimentos_global",
    default_args=default_args,
    start_date=datetime(2026, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    tags=["investimentos", "cambio", "cripto", "etl"]
) as dag:

    extract_bcb_task = PythonOperator(
        task_id="extract_bcb",
        python_callable=task_extract_bcb
    )

    extract_coingecko_task = PythonOperator(
        task_id="extract_coingecko",
        python_callable=task_extract_coingecko
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

    [extract_bcb_task, extract_coingecko_task] >> transform_task >> validate_task >> load_task