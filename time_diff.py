import sys
import os
import pandas as pd
import csv


def check_input(file: str) -> None:
    try:
        if not os.path.exists(file):
            raise FileNotFoundError
        if not file.endswith(".csv") or not os.path.isfile(file):
            raise ValueError
        if os.stat(file).st_size == 0:
            raise ValueError
    except FileNotFoundError:
        print("File not found")
        sys.exit(1)
    except ValueError:
        print("Invalid file")
        sys.exit(1)


def main():
    if not len(sys.argv) == 2:
        print("Usage: python3 time_diff.py <file.csv>")
        sys.exit(1)
    file = sys.argv[1]
    check_input(file)
    #df = pd.read_csv(file, usecols=[1, 3])
    df = pd.read_csv(file)
    df = df.dropna()
    # delete all whitespaces of columns
    df = df.apply(lambda x: x.str.replace(" ", ""))
    # replace all dots with :
    df = df.apply(lambda x: x.str.replace(".", ":"))
    # 
    
    print(df)


if __name__ == "__main__":
    main()
