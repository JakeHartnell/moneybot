# -*- coding: utf-8 -*-
from datetime import datetime
from logging import getLogger
from time import sleep
from time import time
from typing import Generator
from copy import deepcopy

import pandas as pd

from moneybot.market.adapters import MarketAdapter
from moneybot.strategy import Strategy


logger = getLogger(__name__)


class Fund:
    '''
    Funds are the MoneyBot's highest level abstraction.
    Funds have a Strategy, which proposes trades to
    their MarketAdapter.

    There are two ways for a Fund to run: live, or in a backtest.

       my_fund.run_live()

    or

       my_fund.begin_backtest(start, end)

    In both cases, the fund executes its private method `step(time)`
    repeatedly. Strategies decide their own trading interval; this
    dictates the temporal spacing between a fund's steps.
    '''

    def __init__(self, strategy: Strategy, adapter: MarketAdapter) -> None:
        self.strategy = strategy
        # MarketAdapter executes trades, fetches balances
        self.market_adapter = adapter
        # MarketHistory stores historical market data
        self.market_history = adapter.market_history

    def step(self, time: datetime) -> float:
        # We make a copy of our MarketAdapter's market_state
        # This way, we can pass the copy to Strategy.propose_trades()
        # without having to worry about the strategy mutating the market_state
        # to pull some sort of shennannigans (even accidentally).
        # This way, the Strategy cannot communicate at all with the MarketAdapter
        # except through ProposedTrades.
        copied_market_state = deepcopy(self.market_adapter.get_market_state(time))
        # print('market_state.balances', market_state.balances)
        # Now, propose trades. If you're writing a strategy, you will override this method.
        proposed_trades = self.strategy.propose_trades(copied_market_state, self.market_history)
        # If the strategy proposed any trades, we execute them.
        if proposed_trades:
            # Finally, the MarketAdapter will execute our trades.
            # If we're backtesting, these trades won't really happen.
            # If we're trading for real, we will attempt to execute the proposed trades
            # at the best price we can.
            # In either case, this method is side-effect-y;
            # it sets MarketAdapter.balances, after all trades have been executed.
            self.market_adapter.filter_and_execute(proposed_trades)
        # print('market_adapter.balances after propose_trades()', # self.market_adapter.balances)
        # Finally, we get the USD value of our whole fund,
        # now that all trades (if there were any) have been executed.
        usd_value = self.market_adapter.market_state.estimate_total_value_usd()
        return usd_value

    def run_live(self):
        start_time = time()
        PERIOD = self.strategy.trade_interval
        while True:
            # Get time loop starts, so
            # we can account for the time
            # that the step took to run
            cur_time = datetime.now()
            # Before anything,
            # scrape poloniex
            # to make sure we have freshest data
            self.market_history.scrape_latest()
            # Now the fund can step()
            logger.info(f'Fund::step({cur_time})')
            usd_val = self.step(cur_time)
            # After its step, we have got the USD value.
            logger.info(f'Est. USD value: {usd_val}')
            # Wait until our next time to run,
            # Accounting for the time that this step took to run
            sleep(PERIOD - ((time() - start_time) % PERIOD))

    def begin_backtest(
        self,
        start_time: str,
        end_time: str,
    ) -> Generator[float, None, None]:
        '''
        Takes a start time and end time (as parse-able date strings).

        Returns a generator over a list of USD values for each point (trade
        interval) between start and end.
        '''
        # MarketAdapter executes trades
        # Set up the historical coinstore
        # A series of trade-times to run each of our strategies through.
        dates = pd.date_range(
            pd.Timestamp(start_time),
            pd.Timestamp(end_time),
            freq=f'{self.strategy.trade_interval}S',
        )
        for date in dates:
            val = self.step(date)
            yield val
