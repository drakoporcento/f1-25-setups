import streamlit as st
import pandas as pd
import os
from datetime import datetime
import pytz
import time

# CONFIGURAÇÕES DE ACESSO
PASSWORD = "f1buscape"
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    senha = st.text_input("Digite a senha para acessar:", type="password")
    if senha == PASSWORD:
        st.session_state.authenticated = True
        st.rerun()
    else:
        st.stop()

# Caminho do arquivo CSV
SETUP_FILE = 'setups_f1_25.csv'
BACKUP_FOLDER = 'backups'
os.makedirs(BACKUP_FOLDER, exist_ok=True)

# Lista de pistas com bandeiras corrigidas
tracks = [
    "🇦🇺 GP da Austrália, Melbourne", "🇨🇳 GP da China, Xangai", "🇯🇵 GP do Japão, Suzuka",
    "🇧🇭 GP do Bahrein, Sakhir", "🇸🇦 GP da Arábia Saudita, Jeddah", "🇺🇸 GP de Miami, EUA",
    "🇮🇹 GP da Emilia-Romagna, Ímola", "🇲🇨 GP de Mônaco, Monte Carlo", "🇪🇸 GP da Espanha, Barcelona",
    "🇨🇦 GP do Canadá, Montreal", "🇦🇹 GP da Áustria, Red-Bull Ring", "🇦🇹 GP da Áustria, Red-Bull Ring Invertido",
    "🇬🇧 GP da Inglaterra, Silverstone", "🇬🇧 GP da Inglaterra, Silverstone Invertido", "🇧🇪 GP da Bélgica, Spa-Francorchamps",
    "🇭🇺 GP da Hungria, Hungaroring", "🇳🇱 GP da Holanda, Zandvoort", "🇳🇱 GP da Holanda, Zandvoort Invertido",
    "🇮🇹 GP da Itália, Monza", "🇦🇿 GP do Azerbaijão, Baku", "🇸🇬 GP de Singapura, Marina Bay",
    "🇺🇸 GP dos Estados Unidos, Austin Texas", "🇲🇽 GP do México, Cidade do México", "🇧🇷 GP de São Paulo, Interlagos",
    "🇺🇸 GP de Las Vegas, Las Vegas", "🇶🇦 GP do Catar, Lusail", "🇦🇪 GP de Abu Dhabi, Yas Marina"
]

# Mapeamento de descrições técnicas para exibição nos tooltips
setup_descriptions = {
    "Aerodinâmica": "A aerodinâmica ajusta a força que 'cola' o carro no chão. Por exemplo, uma asa dianteira em 20 e traseira em 10 resulta em mais pressão na frente, ajudando nas curvas, mas com menor pressão atrás, o que deixa o carro mais solto na traseira e mais rápido em retas. Ideal para pistas com muitas retas.",
    "Transmissão": "Define como o carro transfere a potência para as rodas. Um diferencial ON em 80% faz com que ambas as rodas traseiras girem de forma mais parecida, o que melhora tração em saídas de curva, mas pode causar subesterço. Já OFF em 50% melhora controle ao soltar o acelerador.",
    "Geometria da Suspensão": "Ajusta a angulação das rodas. Mais cambagem (ex: -3.5) melhora aderência nas curvas, mas desgasta mais os pneus. Menor toe-out (ex: 0.0) reduz arrasto, ajudando na velocidade, mas prejudica a estabilidade.",
    "Suspensão": "Controla a rigidez e estabilidade do carro:\n- Suspensões mais duras (ex: 35) deixam o carro mais ágil e responsivo, mas instável ao passar por zebras ou ondulações.\n- Anti-roll bars mais altos (ex: 20) reduzem a rolagem lateral em curvas, dando mais controle, mas tornam o carro mais imprevisível em trechos irregulares.\n- Altura Frontal/Traseira afeta aerodinâmica e equilíbrio. Altura frontal baixa e traseira alta aumenta pressão frontal e melhora entrada de curva, mas pode causar instabilidade em retas ou raspadas em zebras.",
    "Freios": "Ajusta o equilíbrio da frenagem entre frente e traseira. Um valor de 70% dianteiro concentra a força de frenagem na frente, ideal para frenagens fortes, mas pode causar travamento das rodas. Um valor mais próximo de 50% traz mais equilíbrio.",
    "Pneus": "Pressão afeta aderência e desgaste. Pressões mais baixas (ex: 22.5) aumentam a área de contato, melhorando aderência em curvas, mas aumentam desgaste. Pressões mais altas (ex: 29.5) reduzem desgaste e aquecimento, ideais para longos stints."
}

# Função para renderizar título com tooltip
def titulo_setup_com_info(nome):
    info = setup_descriptions.get(nome, "")
    return st.markdown(f'<div class="setup-section-title">{nome} <span title="{info}" style="cursor: help;">ℹ️</span></div>', unsafe_allow_html=True)

weather_options = ["Seco ☀️", "Chuva Intermediária 🌧️", "Chuva Forte ⛈️"]

st.set_page_config(layout="wide")
st.markdown("""
    <style>
        .block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
        }

        /* Estilo para sliders menores */
        .stSlider > div[data-baseweb="slider"] {
            width: 90% !important;
            margin: auto !important;
        }

        /* Título centralizado nos grupos */
        .setup-section-title {
            text-align: center;
            font-weight: 600;
            font-size: 1.2rem;
            margin-top: 1rem;
            margin-bottom: 0.5rem;
        }

        /* Container interno das colunas */
        [data-testid="column"] {
            padding-left: 0.5rem;
            padding-right: 0.5rem;
        }
    </style>
""", unsafe_allow_html=True)

st.title("Setup F1 25 - Cadastro e Consulta")

def hora_brasil():
    return datetime.now(pytz.timezone("America/Sao_Paulo")).strftime("%d/%m/%Y %H:%M")

# Carregamento de dados
if os.path.exists(SETUP_FILE):
    df = pd.read_csv(SETUP_FILE)
else:
    df = pd.DataFrame(columns=[
        "Nome do Setup", "Última Atualização", "Pista", "Clima", "Asa Dianteira", "Asa Traseira",
        "Transmissão Diferencial Pedal On", "Transmissão Diferencial Pedal Off",
        "Cambagem Frontal", "Cambagem Traseira", "Toe-Out Dianteiro", "Toe-Out Traseiro",
        "Suspensão Frontal", "Suspensão Traseira", "Anti-Roll Dianteiro", "Anti-Roll Traseiro",
        "Altura Frontal", "Altura Traseira", "Balanceamento De Freios Dianteiro", "Pressão Dos Freios",
        "Pressão Dianteiro Direito", "Pressão Dianteiro Esquerdo", "Pressão Traseiro Direito", "Pressão Traseiro Esquerdo"
    ])

def fazer_backup():
    if os.path.exists(SETUP_FILE):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(BACKUP_FOLDER, f"backup_{timestamp}.csv")
        df.to_csv(backup_path, index=False)

def get_value(coluna, padrao):
    if "menu" in st.session_state and st.session_state.menu != "Cadastrar Novo":
        row = df[(df["Nome do Setup"] == st.session_state.menu.split("__")[0]) & (df["Pista"] == st.session_state.menu.split("__")[1])]
        if not row.empty and coluna in row.columns:
            return row[coluna].values[0]
    return padrao

# Sidebar com setups
st.sidebar.title("Setups Salvos")
df_sorted = df.copy()
track_order = {track: idx for idx, track in enumerate(tracks)}
df_sorted["ordem_pista"] = df_sorted["Pista"].map(track_order)
df_sorted = df_sorted.sort_values(by="ordem_pista", na_position="last").drop(columns="ordem_pista")


if st.sidebar.button("➕ Cadastrar Novo Setup"):
    st.session_state.menu = "Cadastrar Novo"
    st.rerun()

for index, row in df_sorted.iterrows():
    setup = row["Nome do Setup"]
    pista = row.get("Pista", "")
    clima = row.get("Clima", "")
    flag = pista.split(" ")[0] if pista else ""
    circuit_name = pista[pista.find(" ")+1:] if pista else ""
    icon = clima.split(" ")[-1] if clima else ""
    clima_nome = " ".join(clima.split(" ")[:-1]) if clima else ""
    label = f"{flag} {circuit_name} | {clima_nome} {icon} | {setup}"
    unique_key = f"{setup}__{pista}"
    if st.sidebar.button(label, key=unique_key):
        st.session_state.menu = unique_key
        st.rerun()

# Backup e Upload
st.sidebar.markdown("---")
st.sidebar.subheader("Backup dos Setups")
if st.sidebar.download_button("⬇️ Baixar Backup", data=df.to_csv(index=False).encode('utf-8'), file_name="backup_setups_f1_25.csv", mime="text/csv"):
    st.toast("Backup baixado com sucesso! 🗃️")

uploaded_file = st.sidebar.file_uploader("📤 Importar Backup CSV", type=["csv"])
if uploaded_file:
    try:
        new_df = pd.read_csv(uploaded_file)
        if "Nome do Setup" in new_df.columns:
            df = pd.concat([df, new_df]).drop_duplicates(subset=["Nome do Setup", "Pista", "Clima"], keep="last")
            df.to_csv(SETUP_FILE, index=False)
            st.sidebar.success("Backup importado com sucesso!")
            st.rerun()
        else:
            st.sidebar.error("Arquivo inválido. Verifique se possui a coluna 'Nome do Setup'.")
    except Exception as e:
        st.sidebar.error(f"Erro ao importar backup: {e}")

# Define valor padrão
if "menu" not in st.session_state:
    st.session_state.menu = "Cadastrar Novo"
menu = st.session_state.menu

if menu != "Cadastrar Novo" and not df.empty:
    setup_info = df[(df["Nome do Setup"] == menu.split("__")[0]) & (df["Pista"] == menu.split("__")[1])]
    if not setup_info.empty:
        data_atualizacao = setup_info.iloc[0].get("Última Atualização", "Não disponível")
        st.info(f"🕒 Última atualização: {data_atualizacao}")

# Exclusão
if menu != "Cadastrar Novo" and not df.empty:
    st.markdown("---")
    if "delete_clicked" not in st.session_state:
        st.session_state.delete_clicked = False

    if st.session_state.delete_clicked:
        st.warning("Tem certeza que deseja excluir este setup?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Confirmar Exclusão"):
                df = df[~((df["Nome do Setup"] == menu.split("__")[0]) & (df["Pista"] == menu.split("__")[1]))]
                df.to_csv(SETUP_FILE, index=False)
                fazer_backup()
                st.session_state.delete_clicked = False
                st.success("Setup excluído com sucesso.")
                st.rerun()
        with col2:
            if st.button("❌ Cancelar"):
                st.session_state.delete_clicked = False
                st.rerun()
    else:
        if st.button("🗑️ Excluir Setup"):
            st.session_state.delete_clicked = True
            st.rerun()

# Campos do Setup em layout otimizado
st.markdown("## Cadastro de Setup")
col_a, col_b, col_c = st.columns(3)

with col_a:
    nome_setup = st.text_input("Nome do Setup", value=menu.split("__")[0] if menu != "Cadastrar Novo" else "")

with col_b:
    pista = st.selectbox("Pista", tracks, index=tracks.index(menu.split("__")[1]) if menu != "Cadastrar Novo" and menu.split("__")[1] in tracks else 0)

with col_c:
    condicao = st.selectbox("Condição Climática", weather_options, index=weather_options.index(get_value("Clima", weather_options[0])) if get_value("Clima", weather_options[0]) in weather_options else 0)

with st.expander("🔧 Configurações do Setup", expanded=True):
    col1, col2, col3 = st.columns(3)

    with col1:
        titulo_setup_com_info("Aerodinâmica")
        asa_dianteira = st.slider("Dianteira", 0, 50, int(get_value("Asa Dianteira", 25)))
        asa_traseira = st.slider("Traseira", 0, 50, int(get_value("Asa Traseira", 25)))

        titulo_setup_com_info("Transmissão")
        diff_on = st.slider("Diferencial ON", 0, 100, int(get_value("Transmissão Diferencial Pedal On", 50)), step=5)
        diff_off = st.slider("Diferencial OFF", 0, 100, int(get_value("Transmissão Diferencial Pedal Off", 50)), step=5)
        
        titulo_setup_com_info("Geometria da Suspensão")
        camb_frontal = st.slider("Cambagem Frontal", -3.5, -2.5, float(get_value("Cambagem Frontal", -3.5)))
        camb_tras = st.slider("Cambagem Traseira", -2.0, -1.0, float(get_value("Cambagem Traseira", -2.0)))
        toe_diant = st.slider("Toe-Out Dianteiro", 0.0, 0.2, float(get_value("Toe-Out Dianteiro", 0.0)))
        toe_tras = st.slider("Toe-Out Traseiro", 0.1, 0.25, float(get_value("Toe-Out Traseiro", 0.10)))        

    with col2:

        titulo_setup_com_info("Suspensão")
        susp_diant = st.slider("Frontal", 1, 41, int(get_value("Suspensão Frontal", 20)))
        susp_tras = st.slider("Traseira", 1, 41, int(get_value("Suspensão Traseira", 20)))
        anti_roll_d = st.slider("Anti-Roll D", 1, 21, int(get_value("Anti-Roll Dianteiro", 10)))
        anti_roll_t = st.slider("Anti-Roll T", 1, 21, int(get_value("Anti-Roll Traseiro", 10)))
        altura_d = st.slider("Altura Frontal", 15, 35, int(get_value("Altura Frontal", 25)))
        altura_t = st.slider("Altura Traseira", 40, 60, int(get_value("Altura Traseira", 50)))

    with col3:

        titulo_setup_com_info("Freios")
        bal_freio = st.slider("Balanceamento Dianteiro", 50, 70, int(get_value("Balanceamento De Freios Dianteiro", 50)), step=1)
        press_freio = st.slider("Pressão dos Freios", 80, 100, int(get_value("Pressão Dos Freios", 95)))

        titulo_setup_com_info("Pneus")
        press_dd = st.slider("Dianteiro Direito", 22.5, 29.5, float(get_value("Pressão Dianteiro Direito", 26.0)), step=0.5)
        press_de = st.slider("Dianteiro Esquerdo", 22.5, 29.5, float(get_value("Pressão Dianteiro Esquerdo", 26.0)), step=0.5)
        press_td = st.slider("Traseiro Direito", 20.5, 26.5, float(get_value("Pressão Traseiro Direito", 23.5)), step=0.5)
        press_te = st.slider("Traseiro Esquerdo", 20.5, 26.5, float(get_value("Pressão Traseiro Esquerdo", 23.5)), step=0.5)

if st.button("📅 Salvar Alterações"):
    if nome_setup:
        nova_linha = {
            "Nome do Setup": nome_setup,
            "Última Atualização": hora_brasil(),
            "Pista": pista,
            "Clima": condicao,
            "Asa Dianteira": asa_dianteira,
            "Asa Traseira": asa_traseira,
            "Transmissão Diferencial Pedal On": diff_on,
            "Transmissão Diferencial Pedal Off": diff_off,
            "Cambagem Frontal": camb_frontal,
            "Cambagem Traseira": camb_tras,
            "Toe-Out Dianteiro": toe_diant,
            "Toe-Out Traseiro": toe_tras,
            "Suspensão Frontal": susp_diant,
            "Suspensão Traseira": susp_tras,
            "Anti-Roll Dianteiro": anti_roll_d,
            "Anti-Roll Traseiro": anti_roll_t,
            "Altura Frontal": altura_d,
            "Altura Traseira": altura_t,
            "Balanceamento De Freios Dianteiro": bal_freio,
            "Pressão Dos Freios": press_freio,
            "Pressão Dianteiro Direito": press_dd,
            "Pressão Dianteiro Esquerdo": press_de,
            "Pressão Traseiro Direito": press_td,
            "Pressão Traseiro Esquerdo": press_te
        }
        duplicado = (
            (df["Nome do Setup"] == nome_setup) &
            (df["Pista"] == pista) &
            (df["Clima"] == condicao)
        )
        if duplicado.any():
            df.loc[duplicado, nova_linha.keys()] = nova_linha.values()
        else:
            df = pd.concat([df, pd.DataFrame([nova_linha])], ignore_index=True)
        df.to_csv(SETUP_FILE, index=False)
        fazer_backup()
        st.success("✅ Setup salvo com sucesso!")
        st.balloons()
        time.sleep(2)
        st.rerun()
    else:
        st.warning("⚠️ O nome do setup é obrigatório para salvar.")