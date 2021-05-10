import pandas as pd
import yfinance as yf
import os

from rotkehlchen.assets.utils import symbol_to_asset_or_token
from rotkehlchen.externalapis.coingecko import Coingecko

gc = Coingecko(data_directory='.')
rows = []

holdings = pd.read_csv("./holdings.csv", parse_dates=['Date'])
current_holdings = holdings.iloc[-1]


for ETHC_ticker in ('DTSRF', 'ETHC.NE', '2KV.MU'):
    ticker = yf.Ticker(ETHC_ticker)

    currency = symbol_to_asset_or_token(ticker.info['currency'])
    eth_price = float(gc.query_current_price(symbol_to_asset_or_token('ETH'), currency))
    mkr_price = float(gc.query_current_price(symbol_to_asset_or_token('MKR'), currency))

    shares_outstanding = ticker.info['sharesOutstanding']
    shares_outstanding = 33_780_000
    price = ticker.history(period='5d').iloc[-1].Close

    print("--")
    print(f"{ticker.info['longName']} ({ticker.info['symbol']}) Holdings")
    print()
    print("ETH:\t", current_holdings.ETH)
    print("MKR:\t", current_holdings.MKR)
    print("Wyre:\t", current_holdings.Wyre_USD)
    print()

    nav = current_holdings.ETH * eth_price + current_holdings.MKR * mkr_price + current_holdings.Wyre_USD
    nav_per_share = nav / shares_outstanding

    print("Shares outstanding:\t{0}".format(shares_outstanding))
    print("NAV:\t{0:.0f} {1}".format(nav, currency.symbol))
    print("NAV per share:\t{0:.2f} {1}".format(nav_per_share, currency.symbol))
    print("Share price:\t{0:.2f} {1}".format(price, currency.symbol))
    print("Premium:\t{0:+.2f} %".format((price / nav_per_share - 1) * 100, currency.symbol))

    rows += [{
        'ticker': ETHC_ticker,
        'currency': currency.symbol,
        'nav': nav,
        'nav_per_share': nav_per_share,
        'share_price': price,
        'shares_outstanding': shares_outstanding,
        'premium': (price / nav_per_share - 1) * 100
    }]

dp_token = os.environ.get('DATAPANE_TOKEN')

if dp_token:
    import datapane as dp
    dp.login(token=dp_token)

    df = pd.DataFrame(rows)
    r = dp.Report(
        f'### Holdings',
        dp.Table(pd.DataFrame(current_holdings).iloc[1:]),
        f'### Share Price Premium',
        dp.Table(df),
        f'The maximum discount is {-df["premium"].min():.1f} %' \
                if df["premium"].mean() < 0 else
                f'The maximum premium is {df["premium"].max():+.1f} %'
    )

    r.publish(
        name=f'Ether Capital Corp. Premium',
        open=False,
        description=f'Calculate the premium of the ETHC share price compared to the holdings'
    )

