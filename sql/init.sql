CREATE TABLE IF NOT EXISTS dim_ativo (
    ativo_id SERIAL PRIMARY KEY,
    codigo VARCHAR(20) UNIQUE NOT NULL,
    nome VARCHAR(100) NOT NULL,
    categoria VARCHAR(30) NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_data (
    data_id SERIAL PRIMARY KEY,
    data DATE UNIQUE NOT NULL,
    dia INT NOT NULL,
    mes INT NOT NULL,
    ano INT NOT NULL
);

CREATE TABLE IF NOT EXISTS fato_cotacao (
    cotacao_id SERIAL PRIMARY KEY,
    data_id INT NOT NULL REFERENCES dim_data(data_id),
    ativo_id INT NOT NULL REFERENCES dim_ativo(ativo_id),
    fonte VARCHAR(50) NOT NULL,
    valor_em_brl NUMERIC(18, 6),
    valor_em_usd NUMERIC(18, 6),
    variacao_diaria NUMERIC(18, 8),
    retorno_acumulado NUMERIC(18, 8),
    volatilidade_7d NUMERIC(18, 8),
    data_carga TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(data_id, ativo_id, fonte)
);