import pandas as pd
from indicators import compute_indicators


class TimeframeSignal:
    """Analyze a single timeframe dataframe and produce signals."""

    def __init__(self, df: pd.DataFrame, atr_sl: float, atr_tp: float, vol_mult: float):
        self.df = compute_indicators(df.copy())
        self.df["VolumeEMA"] = self.df["volume"].ewm(span=20, adjust=False).mean()
        self.atr_sl = atr_sl
        self.atr_tp = atr_tp
        self.vol_mult = vol_mult

    def _determine(self, row: pd.Series) -> str:
        if (
            row["close"] > row["EMA200"]
            and row["EMA9"] > row["EMA21"] > row["EMA50"] > row["EMA200"]
            and row["RSI"] > 55
        ):
            return "LONG"
        if (
            row["close"] < row["EMA200"]
            and row["EMA9"] < row["EMA21"] < row["EMA50"] < row["EMA200"]
            and row["RSI"] < 45
        ):
            return "SHORT"
        return "NO_SIGNAL"

    def signal_at(self, timestamp: pd.Timestamp) -> tuple[str, float, float, float]:
        rows = self.df[self.df["open_time"] <= timestamp]
        if rows.empty:
            return "NO_SIGNAL", 0.0, 0.0, 0.0
        row = rows.iloc[-1]
        sig = self._determine(row)
        volume_ok = row["volume"] >= row["VolumeEMA"] * self.vol_mult
        confidence = 1.0 if sig in ["LONG", "SHORT"] and volume_ok else 0.0
        price = row["close"]
        sl = price - row["ATR"] * self.atr_sl if sig == "LONG" else price + row["ATR"] * self.atr_sl
        tp = price + row["ATR"] * self.atr_tp if sig == "LONG" else price - row["ATR"] * self.atr_tp
        return sig, confidence, sl, tp


class MultiTimeframeAnalyzer:
    """Combine multiple timeframe signals into a final signal."""

    def __init__(
        self,
        data: dict[str, pd.DataFrame],
        atr_sl: float = 1.5,
        atr_tp: float = 3.0,
        volume_mult: float = 1.0,
        confidence_threshold: float = 0.75,
    ) -> None:
        self.analyzers = {
            tf: TimeframeSignal(df, atr_sl, atr_tp, volume_mult) for tf, df in data.items()
        }
        self.threshold = confidence_threshold

    def analyze(
        self, timestamp: pd.Timestamp
    ) -> tuple[str, dict[str, dict[str, float]], float]:
        results = {}
        orientations = []
        confidences = []
        for tf, an in self.analyzers.items():
            sig, conf, sl, tp = an.signal_at(timestamp)
            results[tf] = {"signal": sig, "sl": sl, "tp": tp, "confidence": conf}
            orientations.append(sig)
            confidences.append(conf)

        final = "NO_SIGNAL"
        if all(s == "LONG" for s in orientations):
            final = "LONG"
        elif all(s == "SHORT" for s in orientations):
            final = "SHORT"

        confidence = sum(confidences) / len(confidences) if confidences else 0.0
        if final in ["LONG", "SHORT"] and confidence < self.threshold:
            final = "NO_SIGNAL"

        return final, results, confidence
