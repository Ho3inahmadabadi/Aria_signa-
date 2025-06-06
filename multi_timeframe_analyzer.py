import pandas as pd
from indicators import compute_indicators


class TimeframeSignal:
    """Generate a signal for a single timeframe."""

    def __init__(self, df: pd.DataFrame):
        self.df = compute_indicators(df.copy())

    def _signal(self, row: pd.Series) -> str:
        bull = (
            row["close"] > row["EMA200"]
            and row["EMA9"] > row["EMA21"] > row["EMA50"] > row["EMA200"]
            and row["RSI"] > 55
        )
        bear = (
            row["close"] < row["EMA200"]
            and row["EMA9"] < row["EMA21"] < row["EMA50"] < row["EMA200"]
            and row["RSI"] < 45
        )
        if bull:
            return "LONG"
        if bear:
            return "SHORT"
        return "NO_SIGNAL"

    def at(self, timestamp: pd.Timestamp) -> str:
        rows = self.df[self.df["open_time"] <= timestamp]
        if rows.empty:
            return "NO_SIGNAL"
        return self._signal(rows.iloc[-1])


class MultiTimeframeAnalyzer:
    """Combine timeframe signals into a final decision."""

    def __init__(self, data: dict[str, pd.DataFrame]):
        self.frames = {tf: TimeframeSignal(df) for tf, df in data.items()}

    def analyze(self, timestamp: pd.Timestamp) -> tuple[str, dict[str, str]]:
        details = {tf: frame.at(timestamp) for tf, frame in self.frames.items()}
        final = "NO_SIGNAL"
        if (
            details.get("5m") == "LONG"
            and details.get("3m") == "LONG"
            and details.get("1m") == "LONG"
            and details.get("15m") in ["LONG", "NO_SIGNAL"]
        ):
            final = "LONG"
        elif (
            details.get("5m") == "SHORT"
            and details.get("3m") == "SHORT"
            and details.get("1m") == "SHORT"
            and details.get("15m") in ["SHORT", "NO_SIGNAL"]
        ):
            final = "SHORT"
        return final, details
