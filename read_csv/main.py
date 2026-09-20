import pandas as pd

def read_csv(file_path: str) -> pd.DataFrame:
  return pd.read_csv(file_path)


if __name__ == "__main__":
  df = read_csv("data/raw/customers.csv")
  print(df.head())


