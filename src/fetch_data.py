import yfinance as yf
import pandas as pd
import time
from loguru import logger
from datetime import datetime, timedelta
from typing import List, Union


class FinancialDataExtractor:
    VALID_INTERVALS = [
        "1m",
        "2m",
        "5m",
        "15m",
        "30m",
        "60m",
        "90m",
        "1h",
        "1d",
        "5d",
        "1wk",
        "1mo",
        "3mo",
    ]

    def __init__(
        self,
        symbols: Union[str, List[str]],
        start: str,
        end: str,
        interval: str = "1d",
        max_retries: int = 3,
        delay: int = 1,
    ):
        if isinstance(symbols, str):
            symbols = [symbols]
        elif isinstance(symbols, list):
            if not all(isinstance(symbol, str) for symbol in symbols):
                raise ValueError("All elements in 'symbols' must be strings.")
        else:
            raise TypeError("'symbols' must be a string or a list of strings.")

        if interval not in self.VALID_INTERVALS:
            raise ValueError(
                f"Invalid interval. Must be one of {self.VALID_INTERVALS}."
            )

        try:
            pd.to_datetime(start)
            pd.to_datetime(end)
        except ValueError:
            raise ValueError("Invalid start or end date.")

        if start > end:
            raise ValueError("Start date should be before end date.")

        if interval == "1m" and start < datetime.now() - timedelta(days=30):
            raise ValueError(
                "For 1 min interval, the start date must be within 30 days from the current date."
            )

        self.symbols = symbols
        self.start = start
        self.end = end
        self.interval = interval
        self.max_retries = max_retries
        self.delay = delay
        self.data = self.get_data()

        if self.data is None or self.data.empty:
            raise ValueError("No data was found for the given parameters.")

    def get_data(self):
        for _ in range(self.max_retries):
            try:
                final = pd.DataFrame()
                for symbol in self.symbols:
                    ticker = yf.Ticker(symbol)
                    data = ticker.history(
                        start=self.start, end=self.end, period=self.interval
                    ).assign(Symbol=symbol)
                    final = pd.concat([final, data])
                return final
            except Exception as e:
                logger.error(f"Failed to fetch data for {self.symbols} - {e}")
                time.sleep(self.delay)

        else:
            logger.error(
                f"Failed to fetch data for {self.symbol} after {self.max_retries} retries."
            )
            return None
