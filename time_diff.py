import sys
import os
import pandas as pd
import csv
import re


def check_input(file: str) -> None:
    '''Check if the input file is valid'''
    try:
        if not os.path.exists(file):
            raise FileNotFoundError
        if not file.endswith('.csv') or not os.path.isfile(file):
            raise ValueError
        if os.stat(file).st_size == 0:
            raise ValueError
        if not csv.Sniffer().has_header(file):
            raise ValueError
        with open(file, 'r') as f:
            reader = csv.reader(f)
            header = next(reader)
            if len(header) < 2 or not header[0] == 'start_time' or not header[1] == 'stop_time':
                raise ValueError
    except FileNotFoundError:
        print('File not found')
        sys.exit(1)
    except ValueError:
        print('Invalid file')
        sys.exit(1)


def convert_to_24h(time: str) -> str:
    '''Convert the time from 12h to 24h format'''
    match = re.match(r'(\d+):(\d+)(am|pm)', time)
    if match:
        hour, minute, period = match.groups()
        hour = int(hour)
        if period == 'pm' and hour != 12:
            hour += 12
        elif period == 'am' and hour == 12:
            hour = 0
        return f"{hour:02}:{minute}"
    else:
        return time


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    '''Clean the dataset'''
    # delete all rows with NaN
    df = df.dropna()
    df = df.replace({"a.m": "am", "p.m": "pm", " ": "", "\.": ":"}, regex=True)
    # add ':00' to the time if it is missing between the hour and the am/pm
    df = df.applymap(lambda x: x[:-2] + ':00' + x[-2:] if ':' not in x else x)
    # delete everything that is not a number or ':' or am/pm
    df = df[~df.apply(lambda x: x.str.contains(
        '[^:\dapm]', na=False)).any(axis=1)]
    # translate the time to 24h format
    df = df.applymap(convert_to_24h)
    # delete all rows that are not in the format '%H:%M'
    df = df.applymap(lambda x: x if re.match(r'\d{2}:\d{2}', x) else None)
    # delete all rows with NaN
    df = df.dropna()
    return df


def main():
    '''Main function'''
    if not len(sys.argv) == 2:
        print('Usage: $> python3 time_diff.py <dataset.csv>')
        sys.exit(1)

    file = sys.argv[1]
    check_input(file)
    # df = pd.read_csv(file, usecols=[1, 3]) # only read the 2nd and 4th column
    df = pd.read_csv(file)  # read all columns
    df = clean_data(df)

    # format is now hh:mm, add a 3rd column with the difference
    df['diff_time'] = pd.to_datetime(df['stop_time'], format='%H:%M') - \
        pd.to_datetime(df['start_time'], format='%H:%M')
    # print in a csv file which will have the same name as the input file with '_diff' added
    df.to_csv(file[:-4] + '_diff.csv', index=False)


if __name__ == '__main__':
    main()
