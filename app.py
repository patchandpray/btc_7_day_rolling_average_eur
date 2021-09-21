import logging
from datetime import datetime

import pandas as pd
import pandera as pa
import requests
from dateutil.relativedelta import relativedelta

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

# The schema holds all information about our internal data structure and how to use it
SCHEMA = pa.DataFrameSchema(
    columns={
        "original_usd_price": pa.Column(float),
        "converted_eur_price": pa.Column(float),
        "7_day_rolling_average": pa.Column(float),
    },
    index="reference_date",
    name="btc_7_day_rolling_average_eur",
)

SCHEMA.columns_to_plot = [
    "converted_eur_price",
    "7_day_rolling_average",
]


def get_bitcoin_price_index_data():
    """Used for fetching the bitcoin price index data in USD over a yearly period"""

    datetime_format = "%Y-%m-%d"

    end_date = datetime.now()
    start_date = end_date - relativedelta(years=1)

    url_base = "https://api.coindesk.com/"
    api_version = "v1"
    api = "bpi/historical/close.json"
    api_params = f"start={start_date.strftime(datetime_format)}&end={end_date.strftime(datetime_format)}"

    url = f"{url_base}{api_version}/{api}?{api_params}"

    result = requests.get(url)
    result.raise_for_status()

    # We are only interested in the bpi (bitcoin price index)
    return result.json()["bpi"]


def get_exchange_rate():
    """Used for getting the USD to EUR exchange rate.

    Uses ecb series key, desired content-type and fetches the exhange rate information for a yearly period for
    daily dimensions.
    This daily dimension is denoted by the D in the series key.
    See: https://sdw-wsrest.ecb.europa.eu/help/ key under Data -> Syntax Definition for more info on how this
    series_key is constructed.

    """

    # Retrieving data as text/csv as this is easier to parse and utilize downstream from this api versus json
    content_type = "text/csv"
    headers = {"Accept": content_type}

    series_key = "D.USD.EUR.SP00.A"

    # We only care about the data required to do our calculations https://sdw-wsrest.ecb.europa.eu/help/ -> Data -> Detail
    detail = "dataonly"

    datetime_format = "%Y-%m-%d"

    end_date = datetime.now()
    start_date = end_date - relativedelta(years=1)

    url_base = "https://sdw-wsrest.ecb.europa.eu/"
    api = "service/data/EXR"
    api_params = f"startPeriod={start_date.strftime(datetime_format)}&endPeriod={end_date.strftime(datetime_format)}&detail={detail}"

    url = f"{url_base}{api}/{series_key}?{api_params}"

    result = requests.get(url, headers=headers)
    result.raise_for_status()

    try:
        with open("tmp.csv", "w") as f:
            f.write(result.text)
    except IOError:
        logger.exception("Failed to write data to csv")
        raise


def write_csv(df: pd.DataFrame):
    """Used for writing to csv.

    Uses a schema definition and a dataframe to produce a csv.

    """

    try:
        with open(f"{SCHEMA.name}.csv", "w+") as f:
            df.to_csv(
                f,
                index=True,
                columns=[*SCHEMA.columns.keys()],
            )
    except IOError:
        logger.exception("Failed to write data from dataframe to csv")
        raise


def generate_visualisation(df: pd.DataFrame):
    """Used for generating a visualisation of the 7 day average over time."""

    # Plot and save image
    fig = df[SCHEMA.columns_to_plot].plot().get_figure()

    fig.savefig(f"{SCHEMA.name}.pdf")


def generate_dataframe(input_1: dict) -> pd.DataFrame:
    """Used for generating the dataframe containing all data pertaining to model.

    Creates two dataframes
    Update dataframe keys to enable transformation
    Merges dataframes
    Calculates conversion to EUR
    Calculates rolling average

    """

    # Load dataframe and adhere to schema
    df_1 = pd.DataFrame(
        input_1.items(),
        columns=[SCHEMA.index, SCHEMA.columns["original_usd_price"].name],
    )
    df_1 = df_1.set_index(SCHEMA.index)

    # Load dataframe and adhere to schema
    df_2 = pd.read_csv("tmp.csv")
    df_2 = df_2.rename(columns={"TIME_PERIOD": SCHEMA.index})
    df_2 = df_2.set_index(SCHEMA.index)

    # Merge schema's
    df = pd.merge(df_1, df_2, on=SCHEMA.index)

    # Calculate converted_eur_price by multiplying base * exchange_rate
    df[SCHEMA.columns["converted_eur_price"].name] = (
        df[SCHEMA.columns["original_usd_price"].name] * df["OBS_VALUE"]
    )

    # Calculate 7 day rolling average
    df[SCHEMA.columns["7_day_rolling_average"].name] = (
        df[SCHEMA.columns["converted_eur_price"].name].rolling(7).mean()
    )

    return df


def main():
    """Application entrypoint.

    Application flow is composed and called here.

    Get our input data:
        - bitcoin price index rater over a period of a year by day
        - usd to eur exchange rate over a period of a year by day

    Prepare data for rolling average calculation by using panda's.

    Produce outputs.

    """
    btc_price_index_data = get_bitcoin_price_index_data()
    get_exchange_rate()
    df = generate_dataframe(
        btc_price_index_data,
    )
    generate_visualisation(df)
    write_csv(df)


if __name__ == "__main__":
    main()
