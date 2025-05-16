import streamlit as st
import pandas as pd
from datetime import datetime
import os

DATA_FILE = 'registos_trabalho.csv'

# Carregar dados do ficheiro CSV ao iniciar
if 'data' not in st.session_state:
    if os.path.exists(DATA_FILE):
        st.session_state['data'] = pd.read_csv(DATA_FILE).to_dict('records')
    else:
        st.session_state['data'] = []

# Função para adicionar registo e guardar no ficheiro
def add_record(name, date, hours, rate):
    new_record = {
        'Nome': name,
        'Data': date,
        'Horas': hours,
        'Taxa/Hora': rate,
        'Total': hours * rate
    }
    st.session_state['data'].append(new_record)
    # Guardar todos os registos no ficheiro CSV
    pd.DataFrame(st.session_state['data']).to_csv(DATA_FILE, index=False)

# Função para calcular totais
def calculate_totals():
    df = pd.DataFrame(st.session_state['data'])
    if not df.empty:
        totals = df.groupby('Nome').agg({'Horas': 'sum', 'Total': 'sum'}).reset_index()
        return totals
    return pd.DataFrame()

# Layout da aplicação
st.title('Gestão de Horas de Trabalho - VetSync')

# Formulário de registo
with st.form(key='work_hours_form'):
    name = st.text_input('Nome do Colaborador')
    date = st.date_input('Data', datetime.now())
    hours = st.number_input('Horas Trabalhadas', min_value=0.0, step=0.5)
    rate = 12.5  # Taxa por hora fixa
    st.markdown(f'Taxa/Hora: {rate} €')
    submit_button = st.form_submit_button(label='Registar')

    if submit_button:
        add_record(name, date, hours, rate)
        st.success('Registo adicionado com sucesso!')

# Mostrar tabela de registos
st.subheader('Registos de Trabalho')
df = pd.DataFrame(st.session_state['data'])

if not df.empty:
    for i, row in df.iterrows():
        cols = st.columns((5, 1))
        cols[0].write(
            f"{row['Nome']} | {row['Data']} | {row['Horas']}h | {row['Taxa/Hora']}€/h | {row['Total']}€"
        )
        if cols[1].button("Apagar", key=f"delete_{i}"):
            st.session_state['data'].pop(i)
            pd.DataFrame(st.session_state['data']).to_csv(DATA_FILE, index=False)
            st.rerun()
else:
    st.write("Sem registos.")

# Mostrar totais por colaborador
st.subheader('Totais por Colaborador')
totals_df = calculate_totals()
st.dataframe(totals_df)

# Exportar CSV
if not df.empty:
    st.download_button(
        label="Exportar Dados",
        data=df.to_csv(index=False).encode('utf-8'),
        file_name='registos_trabalho.csv',
        mime='text/csv'
    )