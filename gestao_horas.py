from supabase import create_client, Client
import streamlit as st
import pandas as pd
from datetime import datetime

url = "https://idbgqvynrcytemrggfhb.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlkYmdxdnlucmN5dGVtcmdnZmhiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDc0MTg3MTksImV4cCI6MjA2Mjk5NDcxOX0.r22Cj5lMGf_ecxmImG13_fZSnsIyGySN0XwJQnPhOPA"
supabase: Client = create_client(url, key)

# Adicionar registo
def add_record(name, date, hours, rate):
    supabase.table("registos").insert({
        "nome": name,
        "data": str(date),
        "horas": hours,
        "taxa_hora": rate,
        "total": hours * rate
    }).execute()

# Ler registos
def get_records():
    data = supabase.table("registos").select("*").execute()
    return pd.DataFrame(data.data)

# Apagar registo
def delete_record(record_id):
    supabase.table("registos").delete().eq("id", record_id).execute()

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
        st.experimental_rerun()

# Mostrar tabela de registos
st.subheader('Registos de Trabalho')
df = get_records()

if not df.empty:
    for i, row in df.iterrows():
        cols = st.columns((5, 1))
        cols[0].write(
            f"{row['nome']} | {row['data']} | {row['horas']}h | {row['taxa_hora']}€/h | {row['total']}€"
        )
        if cols[1].button("Apagar", key=f"delete_{row['id']}"):
            delete_record(row['id'])
            st.experimental_rerun()
else:
    st.write("Sem registos.")

# Mostrar totais por colaborador
st.subheader('Totais por Colaborador')
if not df.empty:
    totals_df = df.groupby('nome').agg({'horas': 'sum', 'total': 'sum'}).reset_index()
    st.dataframe(totals_df)
else:
    st.write("Sem totais para mostrar.")

# Exportar CSV
if not df.empty:
    st.download_button(
        label="Exportar Dados",
        data=df.to_csv(index=False).encode('utf-8'),
        file_name='registos_trabalho.csv',
        mime='text/csv'
    )
