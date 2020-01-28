import os
import pandas as pd
from datetime import datetime


def persist_links(links, filename=None):
    file_name = filename or f'home_detail_links_{datetime.now().strftime("%Y%m%d%H%M%S")}.txt'
    with open(file_name, 'w') as f:
        for link in links:
            print(link, file=f)


def write_to_csv(home_info, filename='home_info.csv', sep=","):
    df = pd.DataFrame(home_info)

    if not os.path.isfile(filename):
        df.to_csv(filename, mode='a', index=False, sep=sep)
    elif len(df.columns) != len(pd.read_csv(filename, nrows=1, sep=sep).columns):
        raise Exception("Columns do not match!! Dataframe has " + str(len(df.columns)) + " columns. CSV file has " + str(len(pd.read_csv(filename, nrows=1, sep=sep).columns)) + " columns.")
    elif not (df.columns == pd.read_csv(filename, nrows=1, sep=sep).columns).all():
        raise Exception("Columns and column order of dataframe and csv file do not match!!")
    else:
        df.to_csv(filename, mode='a', index=False, sep=sep, header=False)


def read_file_content(filename):
    with open(filename, 'r') as file:
        content = [line.rstrip() for line in file]
    return content


def get_last_processed_link(filename):
    try:
        content = pd.read_csv(filename)
        return content.Link.iat[-1]
    except Exception:
        return None
