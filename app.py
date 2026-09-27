import streamlit as st
import pandas as pd
import random
import requests
from collections import Counter

# Configuração visual da página inicial
st.set_page_config(page_title="Radar Lotérico IA", layout="wide", page_icon="🎯")

# --- 1. CONFIGURAÇÕES DO JOGO (Menu Lateral) ---
st.sidebar.title("Configurações")
jogo_escolhido = st.sidebar.radio("Selecione a Loteria:", ["Mega-Sena", "Lotofácil"])

# Define as regras matemáticas dependendo de qual jogo o usuário escolheu
if jogo_escolhido == "Mega-Sena":
    max_dezenas = 60
    dezenas_sorteio = 6
    # Proporção do bilhete gerado: 3 quentes, 2 médias, 1 fria (Total 6)
    qtd_quentes, qtd_medias, qtd_frias = 3, 2, 1
else:
    max_dezenas = 25
    dezenas_sorteio = 15
    # Proporção do bilhete gerado: 7 quentes, 5 médias, 3 frias (Total 15)
    qtd_quentes, qtd_medias, qtd_frias = 7, 5, 3

st.title(f"🎯 Radar Analítico: {jogo_escolhido}")

# --- 2. BUSCA DE DADOS REAIS (API Oculta) ---
@st.cache_data(ttl=86400) # Mantém os dados salvos por 24 horas para o app não ficar lento
def carregar_resultados(jogo):
    endpoint = "megasena" if jogo == "Mega-Sena" else "lotofacil"
    url = f"https://loteriascaixa-api.herokuapp.com/api/{endpoint}"
    
    try:
        # A IA tenta ir na internet buscar os dados oficiais
        resposta = requests.get(url, timeout=15)
        dados = resposta.json()
        
        sorteios_reais = []
        for concurso in dados:
            # Pega as dezenas de cada concurso e converte para número
            dezenas_inteiras = [int(num) for num in concurso['dezenas']]
            sorteios_reais.append(dezenas_inteiras)
            
        return sorteios_reais
        
    except Exception as e:
        # PLANO B: Se a API oficial sair do ar, o app não quebra! 
        st.error(f"⚠️ A conexão com a base oficial falhou hoje. Usando simulação estatística para {jogo}.")
        return [random.sample(range(1, max_dezenas + 1), dezenas_sorteio) for _ in range(1000)]

base_dados = carregar_resultados(jogo_escolhido)

# --- 3. ANÁLISE MILIMÉTRICA (IA) ---
# Separa o histórico de todos os tempos vs. o histórico dos últimos 10 sorteios
historico_total = [num for sorteio in base_dados for num in sorteio]
historico_recente = [num for sorteio in base_dados[-10:] for num in sorteio]

freq_total = Counter(historico_total)
freq_recente = Counter(historico_recente)

# Cria a tabela de dados cruzando as informações
df_analise = pd.DataFrame({
    'Dezena': range(1, max_dezenas + 1),
    'Total_Vezes': [freq_total.get(i, 0) for i in range(1, max_dezenas + 1)],
    'Vezes_Recente_10': [freq_recente.get(i, 0) for i in range(1, max_dezenas + 1)]
})

# CÁLCULO DA TEMPERATURA: 
# Dá peso de 70% para o que está acontecendo AGORA e 30% para a história toda
df_analise['Temperatura'] = (df_analise['Total_Vezes'] * 0.3) + (df_analise['Vezes_Recente_10'] * 0.7)
# Ordena da mais quente para a mais fria
df_analise = df_analise.sort_values(by='Temperatura', ascending=False).reset_index(drop=True)

st.write(f"A IA processou **{len(base_dados)} sorteios** da {jogo_escolhido} cruzando o histórico total com os últimos 10 resultados para calcular a 'Temperatura' atual de cada dezena.")

# --- 4. EXIBIÇÃO DE DADOS NA TELA ---
col1, col2 = st.columns(2)
with col1:
    st.subheader("🔥 Top 5 Dezenas 'Fervendo'")
    st.write("Estão saindo muito nos sorteios recentes:")
    st.dataframe(df_analise.head(5)[['Dezena', 'Vezes_Recente_10', 'Temperatura']], hide_index=True)

with col2:
    st.subheader("🧊 Top 5 Dezenas 'Congeladas'")
    st.write("Estão estatisticamente atrasadas (sumidas):")
    st.dataframe(df_analise.tail(5)[['Dezena', 'Vezes_Recente_10', 'Temperatura']], hide_index=True)

# --- 5. MOTOR DE GERAÇÃO ESTRATÉGICA ---
st.header("⚙️ Gerador de Aposta Otimizado")
st.markdown(f"**Estratégia {jogo_escolhido}:** O algoritmo mescla **{qtd_quentes} quentes, {qtd_medias} médias e {qtd_frias} frias** para criar um bilhete balanceado e fugir de padrões viciados.")

if st.button("Gerar Bilhete Estratégico"):
    # Divide todas as bolas disponíveis em 3 categorias iguais (Terços)
    terco = max_dezenas // 3
    
    quentes = df_analise.head(terco)['Dezena'].tolist()
    medias = df_analise.iloc[terco:(terco*2)]['Dezena'].tolist()
    frias = df_analise.tail(terco)['Dezena'].tolist()
    
    # Sorteia os números garantindo a proporção exata da estratégia matemática
    meu_jogo = random.sample(quentes, qtd_quentes) + random.sample(medias, qtd_medias) + random.sample(frias, qtd_frias)
    meu_jogo.sort()
    
    st.success(f"Seu jogo gerado: **{' - '.join(map(lambda x: f'{x:02d}', meu_jogo))}**")
    
st.markdown("---")
st.caption("Aviso: A loteria é um jogo de azar de eventos independentes. Este software analisa frequência estatística e tendências descritivas, não garantindo prêmios ou previsões exatas de sorteios futuros.")
