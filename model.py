import pandas as pd
import yfinance as yf
from rotkehlchen.assets.asset import Asset
from rotkehlchen.externalapis.coingecko import Coingecko

gc = Coingecko()

for ETHC_ticker in ('DTSRF', 'ETHC.NE', '2KV.MU'):
    ticker = yf.Ticker(ETHC_ticker)

    currency = Asset(ticker.info['currency'])
    eth_price = float(gc.simple_price(Asset('ETH'), currency))
    mkr_price = float(gc.simple_price(Asset('MKR'), currency))

    holdings = pd.read_csv("./holdings.csv", sep=';', parse_dates=['Date'])
    current_holdings = holdings.iloc[-1]

    shares_outstanding = ticker.info['sharesOutstanding']
    price = ticker.history(period='1d').iloc[-1].Close

    print("--")
    print(f"{ticker.info['longName']} ({ticker.info['symbol']}) Holdings")
    print()
    print("ETH:\t", current_holdings.ETH)
    print("MKR:\t", current_holdings.MKR)
    print("Wyre:\t", current_holdings.Wyre_USD)
    print()

    nav = current_holdings.ETH * eth_price + current_holdings.MKR * mkr_price + current_holdings.Wyre_USD
    nav_per_share = nav / shares_outstanding

    print("NAV:\t{0:.0f} {1}".format(nav, currency.symbol))
    print("NAV per share:\t{0:.2f} {1}".format(nav_per_share, currency.symbol))
    print("Share price:\t{0:.2f} {1}".format(price, currency.symbol))
    print("Premium:\t{0:+.2f} %".format((price / nav_per_share - 1) * 100, currency.symbol))
