import os

import pyspark.sql.functions as F
from pyspark.sql.types import StringType, IntegerType


def get_last_element(data):
    return data[-1]


get_last_element_udf = F.udf(get_last_element)


def get_symbol_filename(data):
    file = os.path.basename(data)
    return file[:-4]


get_symbol_filename_udf = F.udf(get_symbol_filename, StringType())


def number_sign(data):
    if data is None:
        return None
    return (data > 0) - (data < 0)


get_number_sign_udf = F.udf(number_sign, IntegerType())


def get_market_trend(price_sign, volume_sign):
    if price_sign is None or volume_sign is None or price_sign == 0 or volume_sign == 0:
        return None
    elif price_sign > 0:
        if volume_sign > 0:
            return 'Bullish'
        else:
            return 'Weak Buying'
    else:
        if volume_sign > 0:
            return 'Bearish'
        else:
            return 'Weak Selling'


get_market_trend_udf = F.udf(get_market_trend, StringType())
