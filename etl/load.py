import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv("/opt/airflow/.env")


def get_engine():
    user = os.getenv("POSTGRES_USER", "airflow")
    password = os.getenv("POSTGRES_PASSWORD", "airflow")
    host = os.getenv("POSTGRES_HOST", "postgres")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "investimentos")

    return create_engine(
        f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"
    )


def none_if_nan(value):
    if pd.isna(value):
        return None
    return value


def load_dimensions(df_ativo, df_data):
    engine = get_engine()

    with engine.begin() as conn:
        for _, row in df_ativo.iterrows():
            conn.execute(text("""
                INSERT INTO dim_ativo (codigo, nome, categoria)
                VALUES (:codigo, :nome, :categoria)
                ON CONFLICT (codigo) DO UPDATE SET
                    nome = EXCLUDED.nome,
                    categoria = EXCLUDED.categoria
            """), row.to_dict())

        for _, row in df_data.iterrows():
            conn.execute(text("""
                INSERT INTO dim_data (data, dia, mes, ano)
                VALUES (:data, :dia, :mes, :ano)
                ON CONFLICT (data) DO NOTHING
            """), row.to_dict())


def load_facts(df):
    engine = get_engine()

    with engine.begin() as conn:
        for _, row in df.iterrows():
            ids = conn.execute(text("""
                SELECT 
                    d.data_id,
                    a.ativo_id
                FROM dim_data d
                JOIN dim_ativo a ON a.codigo = :codigo_ativo
                WHERE d.data = :data
            """), {
                "codigo_ativo": row["codigo_ativo"],
                "data": row["data"]
            }).fetchone()

            if ids is None:
                continue

            conn.execute(text("""
                INSERT INTO fato_cotacao (
                    data_id,
                    ativo_id,
                    fonte,
                    valor,
                    variacao_diaria,
                    retorno_acumulado,
                    volatilidade_7d
                )
                VALUES (
                    :data_id,
                    :ativo_id,
                    :fonte,
                    :valor,
                    :variacao_diaria,
                    :retorno_acumulado,
                    :volatilidade_7d
                )
                ON CONFLICT (data_id, ativo_id, fonte)
                DO UPDATE SET
                    valor = EXCLUDED.valor,
                    variacao_diaria = EXCLUDED.variacao_diaria,
                    retorno_acumulado = EXCLUDED.retorno_acumulado,
                    volatilidade_7d = EXCLUDED.volatilidade_7d,
                    data_carga = CURRENT_TIMESTAMP
            """), {
                "data_id": ids.data_id,
                "ativo_id": ids.ativo_id,
                "fonte": row["fonte"],
                "valor": none_if_nan(row["valor"]),
                "variacao_diaria": none_if_nan(row["variacao_diaria"]),
                "retorno_acumulado": none_if_nan(row["retorno_acumulado"]),
                "volatilidade_7d": none_if_nan(row["volatilidade_7d"])
            })