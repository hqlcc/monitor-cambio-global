import requests
import pandas as pd
from datetime import datetime, timedelta


MOEDAS = ["USD", "EUR", "GBP", "JPY", "ARS"]

CRIPTOS = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "SOL": "solana",
    "BNB": "binancecoin"
}


def extract_bcb():
    end_date = datetime.today()
    start_date = end_date - timedelta(days=30)

    rows = []

    for moeda in MOEDAS:
        url = (
            "https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/"
            f"CotacaoMoedaPeriodo(moeda=@moeda,dataInicial=@dataInicial,dataFinalCotacao=@dataFinalCotacao)"
            f"?@moeda='{moeda}'"
            f"&@dataInicial='{start_date.strftime('%m-%d-%Y')}'"
            f"&@dataFinalCotacao='{end_date.strftime('%m-%d-%Y')}'"
            "&$format=json"
        )

        response = requests.get(url, timeout=30)
        response.raise_for_status()

        data = response.json().get("value", [])

        for item in data:
            rows.append({
                "data": item["dataHoraCotacao"][:10],
                "codigo_ativo": moeda,
                "fonte": "BCB",
                "valor_em_brl": item["cotacaoVenda"],
                "valor_em_usd": None
            })

    return pd.DataFrame(rows)


def extract_coingecko():
    import time

    rows = []

    headers = {
        "accept": "application/json",
        "User-Agent": "monitor-investimentos-global"
    }

    for codigo, coin_id in CRIPTOS.items():
        url = (
            f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
            "?vs_currency=usd&days=30&interval=daily"
        )

        response = requests.get(url, headers=headers, timeout=30)

        if response.status_code != 200:
            raise Exception(
                f"Erro na CoinGecko para {codigo}: "
                f"status={response.status_code}, resposta={response.text}"
            )

        data = response.json()
        prices = data.get("prices", [])

        if not prices:
            raise Exception(f"CoinGecko não retornou preços para {codigo}")

        for item in prices:
            timestamp_ms = item[0]
            price_usd = item[1]

            data_cotacao = datetime.utcfromtimestamp(timestamp_ms / 1000).date()

            rows.append({
                "data": str(data_cotacao),
                "codigo_ativo": codigo,
                "fonte": "COINGECKO",
                "valor_em_brl": None,
                "valor_em_usd": price_usd
            })

        time.sleep(3)

    return pd.DataFrame(rows)