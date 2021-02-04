import pandas as pd
import yfinance as yf
from rotkehlchen.assets.asset import Asset
from rotkehlchen.externalapis.coingecko import Coingecko

gc = Coingecko()

# https://www.microstrategy.com/content/dam/website-assets/collateral/financial-documents\
# /microstrategy-announces-over-1b-in-total-bitcoin-purchases-in-2020.pdf
btc_holdings = 70470

# https://www.sec.gov/ix?doc=/Archives/edgar/data/1050446/000119312521025369/d124926d8k.htm
btc_holdings = 71079
avg_buy_price_usd = 15964


for ticker_symbol in ('MSTR', 'MIGA.F'):
    ticker = yf.Ticker(ticker_symbol)

    currency = Asset(ticker.info['currency'])
    if currency.symbol == 'USD':
        usd_price = 1.0
    else:
        usd_price = float(gc.simple_price(Asset('USD'), currency))

    btc_price = float(gc.simple_price(Asset('BTC'), currency))
    #btc_buy_price = avg_buy_price_usd * usd_price

    #h1_2020_mean_price = ticker.history(start='2020-01-01', end='2020-06-01', interval='1wk').Close.mean()
    price = ticker.history(period='5d').iloc[-1].Close

    shares_outstanding = ticker.info['sharesOutstanding']

    print("--")
    print(f"{ticker.info['longName']} ({ticker.info['symbol']}) Holdings")
    print()
    print("BTC:\t", btc_holdings)
    #print("BTC buy price:\t", btc_buy_price, currency.symbol)
    print("BTC current price:\t", btc_price, currency.symbol)
    print()

    nav = btc_holdings * btc_price
    nav_per_share = nav / shares_outstanding
    #mcap_pre_btc_buys = shares_outstanding * h1_2020_mean_price
    #print(mcap_pre_btc_buys)
    #fair_mcap = mcap_pre_btc_buys - btc_holdings * btc_buy_price + btc_holdings * btc_price
    # print(fair_mcap)
    #fair_price = fair_mcap / shares_outstanding
    #import ipdb; ipdb.set_trace()

    print("BTC holdings:\t{0:.0f} {1}".format(nav, currency.symbol))
    print("BTC holdings per share:\t{0:.2f} {1}".format(nav_per_share, currency.symbol))
    #print("Fair market cap:\t{0:.2f} {1}".format(fair_mcap, currency.symbol))
    #print("Fair share price:\t{0:.2f} {1}".format(fair_price, currency.symbol))
    print("Share price:\t{0:.2f} {1}".format(price, currency.symbol))
    print("Premium:\t{0:+.2f} %".format((price / nav_per_share - 1) * 100, currency.symbol))
