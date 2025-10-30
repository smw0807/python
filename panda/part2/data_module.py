import pandas as pd
pd.options.display.max_rows = 6  # 6행까지만 출력
url = 'https://github.com/panda-kim/excel/blob/main/module.xlsx?raw=true'
df = pd.read_excel(url, parse_dates=['일시'])
print(df)