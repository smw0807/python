import pandas as pd

def read_csv(file_path: str) -> pd.DataFrame:
  return pd.read_csv(file_path)

def transform_data(df: pd.DataFrame) -> None:
  # 데이터 컬럼 배열로 수집
  columns = df.columns.tolist()
  print(columns)

  for column in columns:
    print(f"{column}: {df[column].dtype}")




if __name__ == "__main__":
  df = read_csv("data/raw/customers.csv")
  transform_data(df)


