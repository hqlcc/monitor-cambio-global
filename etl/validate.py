def validate_data(df):
    errors = []

    if df.empty:
        errors.append("DataFrame vazio.")

    required_columns = ["data", "codigo_ativo", "fonte", "valor"]

    for column in required_columns:
        if column not in df.columns:
            errors.append(f"Coluna ausente: {column}")

    if errors:
        raise ValueError(" | ".join(errors))

    if df[required_columns].isnull().any().any():
        errors.append("Existem valores nulos em colunas obrigatórias.")

    duplicated = df.duplicated(
        subset=["data", "codigo_ativo", "fonte"]
    ).sum()

    if duplicated > 0:
        errors.append(f"Existem {duplicated} registros duplicados.")

    if (df["valor"] <= 0).any():
        errors.append("Existem cotações menores ou iguais a zero.")

    if errors:
        raise ValueError("Erros de qualidade: " + " | ".join(errors))

    return True