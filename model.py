import datetime

import datapane as dp
import pandas as pd
import yfinance as yf

rows = []
now = datetime.datetime.now()

holdings = pd.read_csv("./holdings.csv", parse_dates=['Date'])
current_holdings = holdings.iloc[-1]


eth_ticker = yf.Ticker('ETH-USD')
eth_usd_price = eth_ticker.history(period='5yahod').iloc[-1].Close
print(eth_usd_price)

eur_usd_ticker = yf.Ticker('EURUSD=X')
eur_usd_price = eur_usd_ticker.history(period='5yahod').iloc[-1].Close
print(eur_usd_price)

cad_usd_ticker = yf.Ticker('CADUSD=X')
cad_usd_price = cad_usd_ticker.history(period='5yahod').iloc[-1].Close
print(cad_usd_price)

nav_usd = current_holdings.ETH * eth_usd_price + \
        current_holdings.StakedETH * eth_usd_price + \
        current_holdings.MKR * 0 + \
        current_holdings.Wyre_USD + \
        current_holdings.USD

print(f"ETH:\t{current_holdings.ETH}\t{current_holdings.ETH * eth_usd_price} USD")
print(f"Staked ETH:\t{current_holdings.StakedETH}\t{current_holdings.StakedETH * eth_usd_price} USD")
print("MKR:\t", current_holdings.MKR)
print("Wyre:\t", current_holdings.Wyre_USD)
print("USD:\t", current_holdings.USD)
print("NAV:\t", nav_usd)
print()

for ETHC_ticker in ('DTSRF', 'ETHC.NE', '2KV.MU'):
    ticker = yf.Ticker(ETHC_ticker)

    # currency = symbol_to_asset_or_token(ticker.info['currency'])
    # eth_price = float(gc.query_current_price(symbol_to_asset_or_token('ETH'), currency))
    # mkr_price = float(gc.query_current_price(symbol_to_asset_or_token('MKR'), currency))
    # usd_price = float(gc.query_current_price(symbol_to_asset_or_token('USDC'), currency))
    shares_outstanding = ticker.info['sharesOutstanding']

    # https://www.businesswire.com/news/home/20231211870281/en/Ether-Capital-Announces-Leadership-Transition-Brian-Mosoff-to-Step-Down-as-CEO-Som-Seif-Appointed-as-Interim-CEO-Update-on-Corporate-Treasury-and-NCIB
    shares_outstanding = 33_533_620

    price = ticker.history(period='5yahod').iloc[-1].Close

    currency_symbol = ticker.info['currency']
    if currency_symbol == 'USD':
        local_usd_price = 1
    else:
        local_usd_ticker = yf.Ticker('{0}{1}=X'.format(currency_symbol, 'USD'))
        local_usd_price = local_usd_ticker.history(period='5yahod').iloc[-1].Close

    nav = nav_usd / local_usd_price
    nav_per_share = nav / shares_outstanding

    print("Shares outstanding:\t{0}".format(shares_outstanding))
    print("NAV:\t{0:.0f} {1}".format(nav, currency_symbol))
    print("NAV per share:\t{0:.2f} {1}".format(nav_per_share, currency_symbol))
    print("Share price:\t{0:.2f} {1}".format(price, currency_symbol))
    print("Premium:\t{0:+.2f} %".format((price / nav_per_share - 1) * 100, currency_symbol))

    rows += [{
        'ticker': ETHC_ticker,
        'currency': currency_symbol,
        'nav': nav,
        'nav_per_share': nav_per_share,
        'share_price': price,
        'shares_outstanding': shares_outstanding,
        'premium': (price / nav_per_share - 1) * 100
    }]

df = pd.DataFrame(rows)
r = dp.Report(
    f'# Ether Capital Corp. NAV',
    dp.Text(f'Updated {now}'),
    f'### Holdings',
    dp.Table(pd.DataFrame(current_holdings).iloc[1:]),
    f'### Share Price Premium',
    dp.Table(df),
    f'The maximum discount is {-df["premium"].min():.1f} %' \
            if df["premium"].mean() < 0 else
            f'The maximum premium is {df["premium"].max():+.1f} %'
)

r.save(
    path='report.html',
    name=f'Ether Capital Corp. NAV',
    open=False
)

