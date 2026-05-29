def validate_data(df):
    errors = []

    if df.empty:
        errors.append("DataFrame vazio.")

    required_columns = [
        "data",
        "codigo_ativo",
        "fonte",
        "valor_em_brl",
        "valor_em_usd"
    ]

    for column in required_columns:
        if column not in df.columns:
            errors.append(f"Coluna obrigatória ausente: {column}")

    if errors:
        raise ValueError(" | ".join(errors))

    if df["data"].isnull().any():
        errors.append("Existem datas nulas.")

    if df["codigo_ativo"].isnull().any():
        errors.append("Existem ativos nulos.")

    if df["fonte"].isnull().any():
        errors.append("Existem fontes nulas.")

    duplicated = df.duplicated(
        subset=["data", "codigo_ativo", "fonte"]
    ).sum()

    if duplicated > 0:
        errors.append(f"Existem {duplicated} registros duplicados.")

    invalid_brl = df["valor_em_brl"].dropna().le(0).sum()
    invalid_usd = df["valor_em_usd"].dropna().le(0).sum()

    if invalid_brl > 0:
        errors.append("Existem valores em BRL menores ou iguais a zero.")

    if invalid_usd > 0:
        errors.append("Existem valores em USD menores ou iguais a zero.")

    linhas_sem_preco = (
        df["valor_em_brl"].isnull() &
        df["valor_em_usd"].isnull()
    ).sum()

    if linhas_sem_preco > 0:
        errors.append(f"Existem {linhas_sem_preco} linhas sem preço.")

    if errors:
        raise ValueError("Erros de qualidade: " + " | ".join(errors))

    return True