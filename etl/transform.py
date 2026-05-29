import pandas as pd


ATIVO_INFO = {
    "USD": {"nome": "Dólar Americano", "categoria": "MOEDA"},
    "EUR": {"nome": "Euro", "categoria": "MOEDA"},
    "GBP": {"nome": "Libra Esterlina", "categoria": "MOEDA"},
    "JPY": {"nome": "Iene Japonês", "categoria": "MOEDA"},
    "ARS": {"nome": "Peso Argentino", "categoria": "MOEDA"},
    "BTC": {"nome": "Bitcoin", "categoria": "CRIPTO"},
    "ETH": {"nome": "Ethereum", "categoria": "CRIPTO"},
    "SOL": {"nome": "Solana", "categoria": "CRIPTO"},
    "BNB": {"nome": "BNB", "categoria": "CRIPTO"},
}


def converter_data(valor):
    valor_str = str(valor)

    if valor_str.isdigit():
        return pd.to_datetime(
            int(valor),
            unit="ms"
        ).date()

    return pd.to_datetime(valor).date()


def transform_data(df_bcb, df_coingecko):
    df = pd.concat([df_bcb, df_coingecko], ignore_index=True)

    if df.empty:
        return df

    df["data"] = df["data"].apply(converter_data)

    df["codigo_ativo"] = df["codigo_ativo"].astype(str).str.upper()
    df["fonte"] = df["fonte"].astype(str).str.upper()

    df["valor_em_brl"] = pd.to_numeric(df["valor_em_brl"], errors="coerce")
    df["valor_em_usd"] = pd.to_numeric(df["valor_em_usd"], errors="coerce")

    df = df.drop_duplicates(
        subset=["data", "codigo_ativo", "fonte"]
    )

    df = df.sort_values(
        ["codigo_ativo", "fonte", "data"]
    )

    df["valor_base"] = df["valor_em_brl"].combine_first(
        df["valor_em_usd"]
    )

    df["variacao_diaria"] = (
        df.groupby(["codigo_ativo", "fonte"])["valor_base"]
        .pct_change()
    )

    df["retorno_acumulado"] = (
        df.groupby(["codigo_ativo", "fonte"])["valor_base"]
        .transform(lambda x: (x / x.iloc[0]) - 1 if len(x) > 1 else None)
    )

    df["volatilidade_7d"] = (
        df.groupby(["codigo_ativo", "fonte"])["variacao_diaria"]
        .rolling(window=7, min_periods=2)
        .std()
        .reset_index(level=[0, 1], drop=True)
    )

    df = df.drop(columns=["valor_base"])

    return df


def create_dim_ativo(df):
    codigos = df["codigo_ativo"].drop_duplicates()

    rows = []

    for codigo in codigos:
        info = ATIVO_INFO.get(
            codigo,
            {
                "nome": codigo,
                "categoria": "OUTRO"
            }
        )

        rows.append({
            "codigo": codigo,
            "nome": info["nome"],
            "categoria": info["categoria"]
        })

    return pd.DataFrame(rows)


def create_dim_data(df):
    datas = pd.to_datetime(df["data"].drop_duplicates())

    return pd.DataFrame({
        "data": datas.date,
        "dia": datas.day,
        "mes": datas.month,
        "ano": datas.year
    })