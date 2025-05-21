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
modelo = joblib.load('modelo_valor_pedido_simulador.pkl')

# Carregar base original
df_base = pd.read_excel('PEDIDOS_02_ANOS.xlsx')

# Opções para as variáveis categóricas
tipos_loja = ['Atacado', 'Varejo']  
tipos_obra = ['CVI - PROJETO GERAARTE', 'CVI - PROJETO CADERNO']
conceitos = ['ALTO', 'MÉDIO', 'POPULAR']
fretes = ['CIF', 'FOB']
faixas_raio = ['até 300', 'de 301 até 900', 'de 901 até 2.000', 'acima de 2.000']
faixas_centrais = ['10%', '15%', '20%', '25%', '30%', 'acima de 50%']

if 'historico_simulacoes' not in st.session_state:
    st.session_state.historico_simulacoes = []

# Formulário para entrada dos dados
with st.form("form_simulacao"):
    st.subheader("Preencha os campos abaixo:")

    col1, col2 = st.columns(2)

    with col1:
        tipo_loja = st.selectbox("Tipo de Loja", options=tipos_loja)
        tipo_obra = st.selectbox("Tipo de Obra", options=tipos_obra)
        frete = st.selectbox("Tipo de Frete", options=fretes)
        conceito = st.selectbox("Padrão da Loja", options=conceitos)

    with col2:
        metros_quadrados = st.number_input("m²", min_value=0, max_value=10000, step=10)
        perc_centrais_label = st.radio("% de Centrais", options=faixas_centrais, horizontal=True)
        raio = st.selectbox("Raio", options=faixas_raio)

    submitted = st.form_submit_button("Simular")

    if submitted:
        conversao_centrais = {
            '10%': 0.10,
            '15%': 0.15,
            '20%': 0.20,
            '25%': 0.25,
            '30%': 0.30,
            'acima de 50%': 0.60
        }
        perc_centrais = conversao_centrais[perc_centrais_label]

        entrada = pd.DataFrame([{
            'Tipo Loja': tipo_loja,
            'Tipo Obra': tipo_obra,
            'Frete': frete,
            'Conceito': conceito,
            'm²': metros_quadrados,
            '% Centrais': perc_centrais,
            'Raio': raio
        }])

        valor_previsto = modelo.predict(entrada)[0]
        valor_previsto *= 1.10
        tempo_instalacao = math.ceil(valor_previsto / 25000)

        st.success(f"Valor Pedido estimado: R$ {valor_previsto:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        st.info(f"Tempo estimado de instalação: {tempo_instalacao} dias")

        st.session_state.historico_simulacoes.append({
            'Tipo Loja': tipo_loja,
            'Tipo Obra': tipo_obra,
            'Frete': frete,
            'Conceito': conceito,
            'm²': metros_quadrados,
            '% Centrais': perc_centrais,
            'Raio': raio,
            'Valor Pedido Previsto': valor_previsto,
            'Tempo Instalação (dias)': tempo_instalacao
        })

        resultado_df = pd.DataFrame(st.session_state.historico_simulacoes[-1:], index=['Resultado'])
        st.write("\nResultado da simulação atual:")
        st.dataframe(resultado_df.style.format({
            "Valor Pedido Previsto": "R$ {:,.2f}",
            "Tempo Instalação (dias)": "{:,.0f}"
        }))

        # Mostrar parte da base real com filtros correspondentes e valores aproximados
        st.subheader("Histórico combinação aproximada")
        margem_m2 = 500
        margem_valor = 100000
        df_filtro = df_base[
            (df_base['Tipo Loja'].str.capitalize() == tipo_loja) &
            (df_base['Tipo Obra'] == tipo_obra) &
            (df_base['Conceito'] == conceito) &
            (df_base['m²'].between(metros_quadrados - margem_m2, metros_quadrados + margem_m2)) &
            (df_base['Valor Pedido'].between(valor_previsto - margem_valor, valor_previsto + margem_valor))
        ]
        if not df_filtro.empty:
            st.dataframe(
                df_filtro[['Obra', 'Valor Pedido', 'm²', '% Centrais', 'Raio', 'Emissão Pedido']]
                .reset_index(drop=True)
                .style.format({"Valor Pedido": "R$ {:,.2f}"})
            )
        else:
            st.warning("Nenhum registro encontrado com esses filtros aproximados na base de pedidos.")

# Mostrar histórico de simulações
if st.session_state.historico_simulacoes:
    st.subheader("Histórico de Simulações")

    if st.button("Limpar Histórico"):
        st.session_state.historico_simulacoes = []
        st.rerun()

    filtro_tipo_loja = st.multiselect("Filtrar por Tipo de Loja:", options=tipos_loja)
    filtro_tipo_obra = st.multiselect("Filtrar por Tipo de Obra:", options=tipos_obra)
    filtro_conceito = st.multiselect("Filtrar por Conceito:", options=conceitos)

    historico_df = pd.DataFrame(st.session_state.historico_simulacoes)

    if filtro_tipo_loja:
        historico_df = historico_df[historico_df['Tipo Loja'].isin(filtro_tipo_loja)]
    if filtro_tipo_obra:
        historico_df = historico_df[historico_df['Tipo Obra'].isin(filtro_tipo_obra)]
    if filtro_conceito:
        historico_df = historico_df[historico_df['Conceito'].isin(filtro_conceito)]

    st.dataframe(historico_df.style.format({
        "Valor Pedido Previsto": "R$ {:,.2f}",
        "Tempo Instalação (dias)": "{:,.0f}"
    }))

