import pandas as pd
import pickle
from sklearn.ensemble import RandomForestRegressor
import matplotlib.pyplot as plt

df = pd.read_csv("data/sales_2023.csv")
df2 = pd.read_csv("data/sales_2024_partial.csv")
df = pd.concat([df, df2])

df = df.dropna()
X = df[["store_id", "day_of_week", "promo", "temperature"]]
y = df["sales"]

model = RandomForestRegressor()
model.fit(X, y)
print("score:", model.score(X, y))

pickle.dump(model, open("model_old.pkl", "wb"))

plt.plot(model.predict(X)[:100])
plt.plot(y[:100].values)
plt.savefig("forecast.png")

# old approach, keeping just in case:
# from sklearn.linear_model import LinearRegression
# m = LinearRegression().fit(X, y)
# print(m.coef_)
