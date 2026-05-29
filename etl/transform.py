import pandas as pd


ATIVO_INFO = {
    "USD": {"nome": "Dólar Americano", "categoria": "MOEDA"},
    "EUR": {"nome": "Euro", "categoria": "MOEDA"},
    "GBP": {"nome": "Libra Esterlina", "categoria": "MOEDA"},
    "JPY": {"nome": "Iene Japonês", "categoria": "MOEDA"},
    "ARS": {"nome": "Peso Argentino", "categoria": "MOEDA"},
    "BRL": {"nome": "Real Brasileiro", "categoria": "MOEDA"},
}


def transform_data(df_bcb, df_frankfurter):
    df = pd.concat([df_bcb, df_frankfurter], ignore_index=True)

    df["data"] = pd.to_datetime(df["data"]).dt.date
    df["codigo_ativo"] = df["codigo_ativo"].astype(str).str.upper()
    df["fonte"] = df["fonte"].astype(str).str.upper()
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce")

    df = df.dropna(subset=["data", "codigo_ativo", "fonte", "valor"])
    df = df[df["valor"] > 0]
    df = df.drop_duplicates(subset=["data", "codigo_ativo", "fonte"])
    df = df.sort_values(["codigo_ativo", "fonte", "data"])

    df["variacao_diaria"] = (
        df.groupby(["codigo_ativo", "fonte"])["valor"].pct_change()
    )

    df["retorno_acumulado"] = (
        df.groupby(["codigo_ativo", "fonte"])["valor"]
        .transform(lambda x: (x / x.iloc[0]) - 1)
    )

    df["volatilidade_7d"] = (
        df.groupby(["codigo_ativo", "fonte"])["variacao_diaria"]
        .rolling(7, min_periods=2)
        .std()
        .reset_index(level=[0, 1], drop=True)
    )

    return df


def create_dim_ativo(df):
    rows = []

    for codigo in df["codigo_ativo"].drop_duplicates():
        info = ATIVO_INFO.get(codigo, {"nome": codigo, "categoria": "MOEDA"})

        rows.append({
            "codigo": codigo,
            "nome": info["nome"],
            "categoria": info["categoria"]
        })

    return pd.DataFrame(rows)


def create_dim_data(df):
    datas = pd.to_datetime(df["data"].drop_duplicates())

    return pd.DataFrame({
        "data": datas.dt.date,
        "dia": datas.dt.day,
        "mes": datas.dt.month,
        "ano": datas.dt.year
    })