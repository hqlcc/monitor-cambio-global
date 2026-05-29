-- 1. Top ativos por retorno acumulado
SELECT
    a.codigo,
    a.nome,
    a.categoria,
    f.fonte,
    ROUND(MAX(f.retorno_acumulado) * 100, 2) AS retorno_acumulado_percentual
FROM fato_cotacao f
JOIN dim_ativo a ON a.ativo_id = f.ativo_id
GROUP BY a.codigo, a.nome, a.categoria, f.fonte
ORDER BY retorno_acumulado_percentual DESC;


-- 2. Ativos mais voláteis
SELECT
    a.codigo,
    a.nome,
    a.categoria,
    f.fonte,
    ROUND(AVG(f.volatilidade_7d) * 100, 2) AS volatilidade_media_percentual
FROM fato_cotacao f
JOIN dim_ativo a ON a.ativo_id = f.ativo_id
WHERE f.volatilidade_7d IS NOT NULL
GROUP BY a.codigo, a.nome, a.categoria, f.fonte
ORDER BY volatilidade_media_percentual DESC;


-- 3. Melhor relação retorno-risco
SELECT
    a.codigo,
    a.nome,
    a.categoria,
    f.fonte,
    ROUND(
        MAX(f.retorno_acumulado) / NULLIF(AVG(f.volatilidade_7d), 0),
        4
    ) AS score_retorno_risco
FROM fato_cotacao f
JOIN dim_ativo a ON a.ativo_id = f.ativo_id
WHERE f.volatilidade_7d IS NOT NULL
GROUP BY a.codigo, a.nome, a.categoria, f.fonte
ORDER BY score_retorno_risco DESC;


-- 4. Série histórica para gráfico
SELECT
    d.data,
    a.codigo,
    a.categoria,
    f.fonte,
    f.valor_em_brl,
    f.valor_em_usd,
    ROUND(f.retorno_acumulado * 100, 2) AS retorno_percentual
FROM fato_cotacao f
JOIN dim_ativo a ON a.ativo_id = f.ativo_id
JOIN dim_data d ON d.data_id = f.data_id
ORDER BY d.data, a.codigo;