import streamlit as st
import pandas as pd
import numpy as np
import joblib
import math

st.set_page_config(
    page_title="Simulador | Previsão de Valor Pedido",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="auto",
)

st.sidebar.markdown('''
<div style="text-align:center">
<h3>Simulador de Valor Pedido</h3>
</div>

---
''', unsafe_allow_html=True)

st.header("Simulando a Previsão do Valor Pedido")

# Carregar o modelo treinado
modelo = joblib.load('../model/modelo_valor_pedido_simulador.pkl')

# Opções para as variáveis categóricas
ufs = ['SP', 'RJ', 'MG', 'BA', 'CE', 'PA', 'SC', 'RO', 'RS', 'PR', 'GO', 'AM', 'PE']
tipos_obra = ['CVI - PROJETO GERAARTE', 'CVI - PROJETO CADERNO']
conceitos = ['ALTO', 'MÉDIO', 'POPULAR']
fretes = ['CIF', 'FOB']

if 'historico_simulacoes' not in st.session_state:
    st.session_state.historico_simulacoes = []

# Formulário para entrada dos dados
with st.form("form_simulacao"):
    st.subheader("Preencha os campos abaixo:")

    col1, col2 = st.columns(2)

    with col1:
        uf = st.selectbox("UF", options=ufs)
        tipo_obra = st.selectbox("Tipo de Obra", options=tipos_obra)
        frete = st.selectbox("Tipo de Frete", options=fretes)
        conceito = st.selectbox("Padrão da Loja", options=conceitos)

    with col2:
        metros_quadrados = st.number_input("m²", min_value=0, max_value=10000, step=10)
        qtd_ckt = st.number_input("Quantidade de Checkout", min_value=0, max_value=100, step=1)
        perc_centrais = st.slider("% de Centrais", 0.0, 1.0, step=0.01)
        distancia_bauru = st.number_input("Distância para Bauru (km)", min_value=0.0, max_value=5000.0, step=1.0)

    submitted = st.form_submit_button("Simular")

    if submitted:
        # Montar DataFrame com uma linha
        entrada = pd.DataFrame([{
            'Cidade': 'Simulada',
            'UF': uf,
            'Frete': frete,
            'Valor Produção': 0,
            'Valor Instalação': 0,
            'Pedido': 0,
            'Tipo Obra': tipo_obra,
            'BDI': 0,
            'm²': metros_quadrados,
            'Qtd Ckt': qtd_ckt,
            'Conceito': conceito,
            'Centrais': 0,
            '% Centrais': perc_centrais,
            'Distância para Bauru (km)': distancia_bauru
        }])

        # Previsão com acréscimo de 10%
        valor_previsto = modelo.predict(entrada)[0]
        valor_previsto *= 1.10

        # Tempo de instalação (valor previsto dividido por 25, arredondado para cima)
        tempo_instalacao = math.ceil(valor_previsto / 25000)

        # Exibir resultados individuais
        st.success(f"Valor Pedido estimado: R$ {valor_previsto:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        st.info(f"Tempo estimado de instalação: {tempo_instalacao} dias")

        # Salvar a simulação no histórico
        st.session_state.historico_simulacoes.append({
            'UF': uf,
            'Tipo Obra': tipo_obra,
            'Frete': frete,
            'Conceito': conceito,
            'm²': metros_quadrados,
            'Qtd Ckt': qtd_ckt,
            '% Centrais': perc_centrais,
            'Distância para Bauru (km)': distancia_bauru,
            'Valor Pedido Previsto': valor_previsto,
            'Tempo Instalação (dias)': tempo_instalacao
        })

# Mostrar histórico de simulações
if st.session_state.historico_simulacoes:
    st.subheader("Histórico de Simulações")

    # Botão para limpar histórico
    if st.button("Limpar Histórico"):
        st.session_state.historico_simulacoes = []
        st.rerun()

    # Filtros
    filtro_uf = st.multiselect("Filtrar por UF:", options=ufs)
    filtro_tipo_obra = st.multiselect("Filtrar por Tipo de Obra:", options=tipos_obra)
    filtro_conceito = st.multiselect("Filtrar por Conceito:", options=conceitos)

    historico_df = pd.DataFrame(st.session_state.historico_simulacoes)

    if filtro_uf:
        historico_df = historico_df[historico_df['UF'].isin(filtro_uf)]

    if filtro_tipo_obra:
        historico_df = historico_df[historico_df['Tipo Obra'].isin(filtro_tipo_obra)]

    if filtro_conceito:
        historico_df = historico_df[historico_df['Conceito'].isin(filtro_conceito)]

    st.dataframe(historico_df.style.format({
        "Valor Pedido Previsto": "R$ {:,.2f}",
        "Tempo Instalação (dias)": "{:,.0f}"
    }))