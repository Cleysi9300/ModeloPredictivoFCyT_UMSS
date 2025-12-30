import joblib

modelo = joblib.load("model/modelo_XGBOOST.joblib")
print(type(modelo))

