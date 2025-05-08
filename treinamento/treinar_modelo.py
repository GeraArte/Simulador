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

# Corrigir tipos
df['Qtd Ckt'] = pd.to_numeric(df['Qtd Ckt'], errors='coerce')

# Selecionar apenas variáveis corretas
colunas_usadas = [
    'UF', 'Tipo Obra', 'Frete', 'Conceito',
    'm²', 'Qtd Ckt', '% Centrais', 'Distância para Bauru (km)', 'Valor Pedido'
]
df = df[colunas_usadas].dropna()

# Separar X e y
X = df.drop(columns=['Valor Pedido'])
y = df['Valor Pedido']

categorical_cols = X.select_dtypes(include='object').columns.tolist()

# Pipeline
preprocessor = ColumnTransformer(transformers=[
    ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_cols)
], remainder='passthrough')

pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('model', CatBoostRegressor(verbose=0, random_state=42))
])

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
pipeline.fit(X_train, y_train)

# Salvar modelo
os.makedirs('../model', exist_ok=True)
joblib.dump(pipeline, '../model/modelo_valor_pedido_simulador.pkl')

print("✅ Novo modelo treinado e salvo em '../model/modelo_valor_pedido_simulador.pkl'")