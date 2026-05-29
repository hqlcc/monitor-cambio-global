import pandas as pd
from etl.transform import transform_data, create_dim_ativo


def test_transform_remove_duplicados():
    df_bcb = pd.DataFrame([
        {
            "data": "2026-05-01",
            "codigo_ativo": "USD",
            "fonte": "BCB",
            "valor_em_brl": 5.10,
            "valor_em_usd": None
        },
        {
            "data": "2026-05-01",
            "codigo_ativo": "USD",
            "fonte": "BCB",
            "valor_em_brl": 5.10,
            "valor_em_usd": None
        }
    ])

    df_coingecko = pd.DataFrame([])

    result = transform_data(df_bcb, df_coingecko)

    assert len(result) == 1


def test_transform_codigo_uppercase():
    df_bcb = pd.DataFrame([
        {
            "data": "2026-05-01",
            "codigo_ativo": "usd",
            "fonte": "bcb",
            "valor_em_brl": 5.10,
            "valor_em_usd": None
        }
    ])

    df_coingecko = pd.DataFrame([])

    result = transform_data(df_bcb, df_coingecko)

    assert result.iloc[0]["codigo_ativo"] == "USD"
    assert result.iloc[0]["fonte"] == "BCB"


def test_create_dim_ativo():
    df = pd.DataFrame([
        {"codigo_ativo": "USD"},
        {"codigo_ativo": "BTC"}
    ])

    dim = create_dim_ativo(df)

    assert len(dim) == 2
    assert "codigo" in dim.columns
    assert "categoria" in dim.columns