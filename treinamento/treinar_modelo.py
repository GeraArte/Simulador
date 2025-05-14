import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.model_selection import train_test_split
from catboost import CatBoostRegressor
import joblib
import os

# Carregar dados
df = pd.read_excel('../input/PEDIDOS_02_ANOS.xlsx')

# Padronizar valores de "Tipo Loja" para capitalizar (Ex: "Varejo", "Atacado")
df['Tipo Loja'] = df['Tipo Loja'].str.capitalize()

# Selecionar apenas variáveis corretas
colunas_usadas = [
    'Tipo Loja', 'Tipo Obra', 'Frete', 'Conceito',
    'm²', '% Centrais', 'Raio', 'Valor Pedido'
]
df = df[colunas_usadas].dropna()

# Separar X e y
X = df.drop(columns=['Valor Pedido'])
y = df['Valor Pedido']

# Identificar colunas categóricas
categorical_cols = X.select_dtypes(include='object').columns.tolist()

# Pipeline de preprocessamento + modelo
preprocessor = ColumnTransformer(transformers=[
    ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_cols)
], remainder='passthrough')

pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('model', CatBoostRegressor(verbose=0, random_state=42))
])

# Treinar modelo
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
pipeline.fit(X_train, y_train)

# Salvar modelo treinado
os.makedirs('../model', exist_ok=True)
joblib.dump(pipeline, '../model/modelo_valor_pedido_simulador.pkl')

print("\u2705 Modelo treinado e salvo em '../model/modelo_valor_pedido_simulador.pkl'")
