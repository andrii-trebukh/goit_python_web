from datetime import timedelta, date
import json
from currency_exchange import PBFetch


URL_PATTERN = "https://api.privatbank.ua/p24api/exchange_rates?json&date={}"


async def get_url_list(days):
    url_list = []
    for day in range(days):
        curr_date = date.today() - timedelta(day)
        url_list.append(URL_PATTERN.format(curr_date.strftime("%d.%m.%Y")))
    return url_list


async def get_currency_list(data, currencies):
    for item in data:
        if item is None:
            continue
        new_rates = []
        rates = item["exchangeRate"]
        for rate in rates:
            if rate["currency"].lower() in currencies:
                new_rates.append(rate)
        item["exchangeRate"] = new_rates
    return data


async def nice_out_cli(data):
    out = []
    for item in data:
        item_out = {}
        if item is None:
            continue
        for rate in item['exchangeRate']:
            item_out[rate['currency']] = {
                "sale": rate['saleRate'] if rate.get('saleRate') is not None
                else rate['saleRateNB'],
                "purchase": rate['purchaseRate']
                if rate.get('purchaseRate') is not None
                else rate['purchaseRateNB']
            }
        out.append({item['date']: item_out})
    return json.dumps(out, indent=2)


async def fetch_data(urls):
    fetch = PBFetch()
    return await fetch.get_fetch(urls)


async def out_for_cli(days, currencies):
    url_list = await get_url_list(days)
    data = await fetch_data(url_list)
    data = await get_currency_list(data, currencies)
    return await nice_out_cli(data)


async def out_for_chat(input_str: str):
    input_str = input_str.removeprefix("exchange").strip()
    if input_str.isdigit():
        days = int(input_str)
        if not 0 < days <= 10:
            return "Found exchange command with incorrect options. " \
                "Days number out of range: 1 - today (default), max 10 days"
    elif input_str == "":
        days = 1
    else:
        return "Found exchange command with incorrect options." \
            "Usage: exchange [days]"
    url_list = await get_url_list(days)
    data = await fetch_data(url_list)
    data = await get_currency_list(data, ["usd", "eur"])
    output = ["PrivatBank currency exchange rates:"]
    for item in data:
        if item is None:
            continue
        output.append(f"Date: {item['date']},")
        for rate in item['exchangeRate']:
            output.append(
                f"{rate['currency']}: "
                f"sale: {rate['saleRate'] if rate.get('saleRate') is not None else rate['saleRateNB']}, "
                f"purchase: {rate['purchaseRate'] if rate.get('purchaseRate') is not None else rate['purchaseRateNB']};"
            )
    return " ".join(output)
