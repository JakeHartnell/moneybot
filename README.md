# MoneyBot

[![Build Status](https://travis-ci.org/elsehow/moneybot.svg?branch=master)](https://travis-ci.org/elsehow/moneybot)

MoneyBot allows you to backtest trading strategies, and deploy these strategies to live-trade, without changing code.

For now, MoneyBot only supports Poloniex. However, a generic `MarketAdapter` pattern could allow trading over many exchanges. PRs welcome!

# install

First, install Python dependencies.

```
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

Then setup up docker on your machine if you haven't already (note: for OSX we recommend using `docker-machine` instead of the docker app, which you can install with homebrew).

Next, set up the Postgres database and restore the historical data. We provide scripts to automate this process with Docker (note, however, that you'll need to install postgres on your system for the restore, `brew install postgresql` with homebrew):

```
cd local-services/postgres
make image
make server
./restore.sh
```

(By default, the database password is `secretpass` - you can change that in `local-services/postgres/Makefile`.)

# use

First, make sure Postgres is running (`cd local-services/postgres; make server`).

There are a few `Strategy` implementations in `moneybot.examples.strategies`.

>The strategies included herein are viable for live-trading use, but crypto trading is serious business. It's entirely possible to lose a lot of money, very quickly. The authors of this library provide these for the sake of illustration and assume no responsibility for their performance if deployed.

## backtesting

```
python3 examples/backtest.py -c config.yml -s buffed-coin
```

## live trading

**NOTE**: See disclaimer!

To live-trade, you will need Poloniex API keys. You can generate those via the [Poloniex web interface](https://www.youtube.com/watch?v=OScIbgXZoW0). You'll only need to allow "trading" permissions on the keys. See the `config-example.yaml` file, add your Poloniex credentials and save it as `config.yml`.

```
python3 examples/live_trading.py -c config.yml -s buffed-coin
```

# disclaimer

Use MoneyBot AT YOUR OWN RISK. Specifically,

- Backtests are no guarantee of future/live performance.
- MoneyBot relies on 3rd-party APIs, like Poloniex, which may fail at anytime.
- MoneyBot is experimental software, and also may fail at any time.
- Running a bot, and trading in general, requires careful study of the risks, and parameters. Wrong settings can cause a major loss.
- Never leave MoneyBot un-monitored for long periods of time. Be prepared to stop it if too much loss occurs.

*You alone* are responsible for anything that happens when you're live-trading!

# license

BSD
