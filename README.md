# Monitor de Câmbio Global — Melhor Moeda para Investir

## Sobre o Projeto

O **Monitor de Câmbio Global** é um projeto de Engenharia de Dados desenvolvido para coletar, processar e analisar cotações de moedas internacionais através de um pipeline ETL automatizado.

O sistema utiliza dados provenientes do **Banco Central do Brasil (PTAX)** e da **Frankfurter API**, armazenando as informações em um Data Warehouse PostgreSQL para permitir análises sobre retorno e volatilidade das moedas monitoradas.

---

## Objetivo

Identificar quais moedas apresentaram melhor desempenho no período analisado, considerando indicadores de:

- Retorno acumulado
- Volatilidade
- Relação risco-retorno

---

## Arquitetura

```text
Banco Central (PTAX) ─┐
                       ├── Extract
Frankfurter API ──────┘

          ↓

      Transform

          ↓

      Validate

          ↓

 PostgreSQL DW

          ↓

 Consultas Analíticas
```

---

## Tecnologias Utilizadas

### Linguagens

- Python 3.8+

### Engenharia de Dados

- Pandas
- Apache Airflow

### Banco de Dados

- PostgreSQL

### Infraestrutura

- Docker
- Docker Compose

### APIs

- Banco Central do Brasil (PTAX)
- Frankfurter API

---

## Modelo Dimensional

### Dimensão Ativo

| Campo     | Descrição          |
| --------- | ------------------ |
| ativo_id  | Chave substituta   |
| codigo    | Código da moeda    |
| nome      | Nome da moeda      |
| categoria | Categoria do ativo |

---

### Dimensão Data

| Campo   | Descrição        |
| ------- | ---------------- |
| data_id | Chave substituta |
| data    | Data da cotação  |
| dia     | Dia do mês       |
| mes     | Mês              |
| ano     | Ano              |

---

### Fato Cotação

| Campo             | Descrição                    |
| ----------------- | ---------------------------- |
| cotacao_id        | Chave substituta             |
| data_id           | FK para dimensão data        |
| ativo_id          | FK para dimensão ativo       |
| fonte             | Origem da cotação            |
| valor             | Valor da cotação             |
| variacao_diaria   | Variação percentual diária   |
| retorno_acumulado | Retorno acumulado            |
| volatilidade_7d   | Volatilidade móvel de 7 dias |

---

## Pipeline ETL

### Extract

Coleta automática de dados através de:

- Banco Central do Brasil (PTAX)
- Frankfurter API

### Transform

Processamento dos dados:

- Padronização de datas
- Tratamento de valores nulos
- Remoção de duplicidades
- Cálculo de retorno acumulado
- Cálculo de volatilidade móvel

### Validate

Validação de:

- Valores nulos
- Duplicidades
- Valores inválidos
- Integridade dos dados

### Load

Carga incremental para:

- dim_ativo
- dim_data
- fato_cotacao

---

## Como Executar

### Clonar o repositório

```bash
git clone <URL_DO_REPOSITORIO>
cd monitor-cambio-global
```

### Subir os containers

```bash
docker compose up -d
```

### Acessar o Airflow

```text
http://localhost:8080
```

Usuário:

```text
admin
```

Senha:

```text
admin
```

### Executar a DAG

```text
monitor_investimentos_global
```

---

## Consultas Analíticas

### Melhor retorno acumulado

```sql
SELECT
    a.codigo,
    a.nome,
    f.fonte,
    ROUND(MAX(f.retorno_acumulado)::numeric * 100, 2) AS retorno_percentual
FROM fato_cotacao f
JOIN dim_ativo a ON a.ativo_id = f.ativo_id
GROUP BY a.codigo, a.nome, f.fonte
ORDER BY retorno_percentual DESC;
```

### Maior volatilidade

```sql
SELECT
    a.codigo,
    a.nome,
    f.fonte,
    ROUND(AVG(f.volatilidade_7d)::numeric * 100, 2) AS volatilidade_media
FROM fato_cotacao f
JOIN dim_ativo a ON a.ativo_id = f.ativo_id
WHERE f.volatilidade_7d IS NOT NULL
GROUP BY a.codigo, a.nome, f.fonte
ORDER BY volatilidade_media DESC;
```

---

## Resultados Obtidos

Durante os testes foram processados:

- 5 moedas monitoradas
- 22 datas analisadas
- 198 registros carregados

### Melhor desempenho

| Moeda | Retorno |
| ----- | ------: |
| JPY   |   2,08% |
| USD   |   1,20% |
| BRL   |   0,98% |

### Maior volatilidade

| Moeda | Volatilidade |
| ----- | -----------: |
| JPY   |        0,89% |
| USD   |        0,56% |
| EUR   |        0,51% |

---

## Licença

Este projeto foi desenvolvido para fins acadêmicos na disciplina de Integração de Dados.
