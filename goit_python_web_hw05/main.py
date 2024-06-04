import argparse
import asyncio
from currency_exchange import out_for_cli


CURRENCIES = {
    "AUD": "Australian dollar",
    "AZN": "Azerbaijani manat",
    "BYN": "Belarusian ruble",
    "CAD": "Canadian dollar",
    "CHF": "Swiss franc",
    "CNY": "Chinese yuan",
    "CZK": "Czech koruna",
    "DKK": "Danish krone",
    "EUR": "Euro",
    "GBP": "Sterling",
    "GEL": "Georgian lari",
    "HUF": "Hungarian forint",
    "ILS": "Israeli shekel",
    "JPY": "Japanese yen",
    "KZT": "Kazakhstani tenge",
    "MDL": "Moldovan leu",
    "NOK": "Norwegian krone",
    "PLN": "Polish złoty",
    "SEK": "Swedish krona",
    "SGD": "Singapore dollar",
    "TMT": "Turkmenistani manat",
    "TRY": "Turkish lira",
    "USD": "United States dollar",
    "UZS": "Uzbekistani sum",
    "XAU": "Gold"
}


def main():
    parser = argparse.ArgumentParser(
        description='PrivatBank currency exchange rate'
    )
    parser.add_argument(
        "days",
        default=1,
        nargs="?",
        help="show exchange rate for n days: 1 - today (default), max 10 days"
    )
    parser.add_argument(
        "-c",
        "--currency",
        choices=tuple(key.lower() for key in CURRENCIES),
        nargs="*",
        help="Available currencies: "
        "; ".join(f"{key} - {des}" for key, des in CURRENCIES.items())
    )
    args = parser.parse_args()
    days = int(args.days)
    if not 0 < days <= 10:
        raise ValueError("Days number out of range")
    currencies = args.currency
    if not currencies:
        currencies = ["usd", "eur"]
    print(asyncio.run(out_for_cli(days, currencies)))


if __name__ == "__main__":
    main()
