import talib
from talib._ta_lib import CDLINVERTEDHAMMER, CDLDOJI, CDLSHOOTINGSTAR, CDLHAMMER, CDLHARAMI, CDLPIERCING

from config.cst import *
from evaluator.TA.TA_evaluator import MomentumEvaluator
from evaluator.Util.advanced_manager import AdvancedManager

from evaluator.Util.trend_analyser import TrendAnalyser

from evaluator.Util.momentum_analyser import MomentumAnalyser


class RSIMomentumEvaluator(MomentumEvaluator):
    def __init__(self):
        super().__init__()
        self.pertinence = 1
        self.enabled = True

    # TODO : temp analysis
    def eval_impl(self):
        rsi_v = talib.RSI(self.data[PriceStrings.STR_PRICE_CLOSE.value])

        long_trend = TrendAnalyser.get_trend(rsi_v, self.long_term_averages)
        short_trend = TrendAnalyser.get_trend(rsi_v, self.short_term_averages)

        # check if trend change
        if short_trend > 0 > long_trend:
            # trend changed to up
            self.set_eval_note(-short_trend)

        elif long_trend > 0 > short_trend:
            # trend changed to down
            self.set_eval_note(short_trend)

        # use RSI current value
        last_rsi_value = rsi_v.tail(1).values[0]
        if last_rsi_value > 50:
            self.set_eval_note(rsi_v.tail(1).values[0] / 200)
        else:
            self.set_eval_note((rsi_v.tail(1).values[0] - 100) / 200)

# bollinger_bands
class BBMomentumEvaluator(MomentumEvaluator):
    def __init__(self):
        super().__init__()
        self.enabled = True

    def eval_impl(self):
        self.eval_note = AdvancedManager.get_class(self.config, MomentumAnalyser).bollinger_momentum_analysis(
            self.data[PriceStrings.STR_PRICE_CLOSE.value])

class CandlePatternMomentumEvaluator(MomentumEvaluator):
    def __init__(self):
        super().__init__()
        self.pertinence = 1
        self.factor = 0.5
        self.enabled = True

    def update_note(self, pattern_bool):
        last_value = pattern_bool.tail(1).values[0]

        # bullish
        if last_value >= 100:

            # confirmation
            if last_value > 200:
                self.set_eval_note(-2 * self.factor)
            else:
                self.set_eval_note(-1 * self.factor)

        # bearish
        elif last_value <= -100:

            # confirmation
            if last_value > 200:
                self.set_eval_note(2 * self.factor)
            else:
                self.set_eval_note(1 * self.factor)

    def eval_impl(self):
        open_values = self.data[PriceStrings.STR_PRICE_OPEN.value]
        high_values = self.data[PriceStrings.STR_PRICE_HIGH.value]
        low_values = self.data[PriceStrings.STR_PRICE_LOW.value]
        close_values = self.data[PriceStrings.STR_PRICE_CLOSE.value]

        # Inverted Hammer
        # When the low and the open are the same, a bullish Inverted Hammer candlestick is formed and
        # it is considered a stronger bullish sign than when the low and close are the same, forming a bearish
        # Hanging Man (the bearish Hanging Man is still considered bullish, just not as much because the day ended by
        # closing with losses).
        self.update_note(CDLINVERTEDHAMMER(open_values, high_values, low_values, close_values))

        # Hammer
        # The long lower shadow of the Hammer implies that the market tested to find where support and
        # demand was located. When the market found the area of support, the lows of the day, bulls began to push
        # prices higher, near the opening price. Thus, the bearish advance downward was rejected by the bulls.
        self.update_note(CDLHAMMER(open_values, high_values, low_values, close_values))

        # Doji
        # It is important to emphasize that the Doji pattern does not mean reversal, it means indecision.Doji's
        # are often found during periods of resting after a significant move higher or lower; the market,
        # after resting, then continues on its way. Nevertheless, a Doji pattern could be interpreted as a sign that
        # a prior trend is losing its strength, and taking some profits might be well advised.
        self.update_note(CDLDOJI(open_values, high_values, low_values, close_values))

        # Shooting star
        # The Shooting Star formation is considered less bearish, but nevertheless bearish when the
        # open and low are roughly the same. The bears were able to counteract the bulls, but were not able to bring
        # the price back to the price at the open.
        # The long upper shadow of the Shooting Star implies that the market tested to find where resistance and
        # supply was located. When the market found the area of resistance, the highs of the day, bears began to push
        #  prices lower, ending the day near the opening price. Thus, the bullish advance upward was rejected by the
        # bears.
        self.update_note(CDLSHOOTINGSTAR(open_values, high_values, low_values, close_values))

        # Harami A buy signal could be triggered when the day after the bullish Harami occured, price rose higher,
        # closing above the downward resistance trendline. A bullish Harami pattern and a trendline break is a
        # combination that potentially could resulst in a buy signal. A sell signal could be triggered when the day
        # after the bearish Harami occured, price fell even further down, closing below the upward support trendline.
        #  When combined, a bearish Harami pattern and a trendline break might be interpreted as a potential sell
        # signal.
        self.update_note(CDLHARAMI(open_values, high_values, low_values, close_values))

        # Piercing Line
        # Pattern Bullish Engulfing Pattern (see: Bullish Engulfing Pattern) is typically viewed as
        # being more bullish than the Piercing Pattern because it completely reverses the losses of Day 1 and adds
        # new gains.
        self.update_note(CDLPIERCING(open_values, high_values, low_values, close_values))

        # if neutral
        if self.eval_note == 0:
            self.eval_note = START_PENDING_EVAL_NOTE


# ADX --> trend_strength
class ADXMomentumEvaluator(MomentumEvaluator):
    def __init__(self):
        super().__init__()
        self.enabled = False

    # TODO : temp analysis
    def eval_impl(self):
        adx_v = talib.ADX(self.data[PriceStrings.STR_PRICE_HIGH.value],
                          self.data[PriceStrings.STR_PRICE_LOW.value],
                          self.data[PriceStrings.STR_PRICE_CLOSE.value])

        last = adx_v.tail(1).values

        # An ADX above 30 on the scale indicates there is a strong trend
        if last > 30:
            pass

        # When ADX drops below 18, it often leads to a sideways or horizontal trading pattern
        elif last < 18:
            pass


class OBVMomentumEvaluator(MomentumEvaluator):
    def __init__(self):
        super().__init__()
        self.enabled = False

    def eval_impl(self):
        obv_v = talib.OBV(self.data[PriceStrings.STR_PRICE_CLOSE.value],
                          self.data[PriceStrings.STR_PRICE_VOL.value])


# William's % R --> overbought / oversold
class WilliamsRMomentumEvaluator(MomentumEvaluator):
    def __init__(self):
        super().__init__()
        self.enabled = False

    def eval_impl(self):
        willr_v = talib.WILLR(self.data[PriceStrings.STR_PRICE_HIGH.value],
                              self.data[PriceStrings.STR_PRICE_LOW.value],
                              self.data[PriceStrings.STR_PRICE_CLOSE.value])


# TRIX --> percent rate-of-change trend
class TRIXMomentumEvaluator(MomentumEvaluator):
    def __init__(self):
        super().__init__()
        self.enabled = False

    def eval_impl(self):
        trix_v = talib.TRIX(self.data[PriceStrings.STR_PRICE_CLOSE.value])


class MACDMomentumEvaluator(MomentumEvaluator):
    def __init__(self):
        super().__init__()
        self.enabled = False

    def eval_impl(self):
        macd_v = talib.MACD(self.data[PriceStrings.STR_PRICE_CLOSE.value])


class ChaikinOscillatorMomentumEvaluator(MomentumEvaluator):
    def __init__(self):
        super().__init__()
        self.enabled = False

    def eval_impl(self):
        pass


class StochasticMomentumEvaluator(MomentumEvaluator):
    def __init__(self):
        super().__init__()
        self.enabled = False

    def eval_impl(self):
        slowk, slowd = talib.STOCH(self.data[PriceStrings.STR_PRICE_HIGH.value],
                                   self.data[PriceStrings.STR_PRICE_LOW.value],
                                   self.data[PriceStrings.STR_PRICE_CLOSE.value])
