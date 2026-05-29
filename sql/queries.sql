-- 1. Ranking de retorno acumulado
SELECT
    a.codigo,
    a.nome,
    f.fonte,
    ROUND(MAX(f.retorno_acumulado) * 100, 2) AS retorno_percentual
FROM fato_cotacao f
JOIN dim_ativo a ON a.ativo_id = f.ativo_id
GROUP BY a.codigo, a.nome, f.fonte
ORDER BY retorno_percentual DESC;


-- 2. Moedas mais voláteis
SELECT
    a.codigo,
    a.nome,
    f.fonte,
    ROUND(AVG(f.volatilidade_7d) * 100, 2) AS volatilidade_media_percentual
FROM fato_cotacao f
JOIN dim_ativo a ON a.ativo_id = f.ativo_id
WHERE f.volatilidade_7d IS NOT NULL
GROUP BY a.codigo, a.nome, f.fonte
ORDER BY volatilidade_media_percentual DESC;


-- 3. Melhor relação retorno-risco
SELECT
    a.codigo,
    a.nome,
    f.fonte,
    ROUND(
        MAX(f.retorno_acumulado) / NULLIF(AVG(f.volatilidade_7d), 0),
        4
    ) AS score_retorno_risco
FROM fato_cotacao f
JOIN dim_ativo a ON a.ativo_id = f.ativo_id
WHERE f.volatilidade_7d IS NOT NULL
GROUP BY a.codigo, a.nome, f.fonte
ORDER BY score_retorno_risco DESC;


-- 4. Série histórica
SELECT
    d.data,
    a.codigo,
    a.nome,
    f.fonte,
    f.valor,
    ROUND(f.retorno_acumulado * 100, 2) AS retorno_percentual
FROM fato_cotacao f
JOIN dim_ativo a ON a.ativo_id = f.ativo_id
JOIN dim_data d ON d.data_id = f.data_id
ORDER BY d.data, a.codigo, f.fonte;