import requests
import pandas as pd
from datetime import datetime, timedelta


MOEDAS = ["USD", "EUR", "GBP", "JPY", "ARS"]


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
                "valor": item["cotacaoVenda"]
            })

    return pd.DataFrame(rows)


def extract_frankfurter():
    end_date = datetime.today().date()
    start_date = end_date - timedelta(days=30)

    moedas = "USD,GBP,JPY,ARS,BRL"

    url = (
        f"https://api.frankfurter.app/{start_date}..{end_date}"
        f"?from=EUR&to={moedas}"
    )

    response = requests.get(url, timeout=30)
    response.raise_for_status()

    data = response.json()
    rates = data.get("rates", {})

    rows = []

    for data_cotacao, valores in rates.items():
        for moeda, valor in valores.items():
            rows.append({
                "data": data_cotacao,
                "codigo_ativo": moeda,
                "fonte": "FRANKFURTER",
                "valor": valor
            })

        rows.append({
            "data": data_cotacao,
            "codigo_ativo": "EUR",
            "fonte": "FRANKFURTER",
            "valor": 1.0
        })

    return pd.DataFrame(rows)