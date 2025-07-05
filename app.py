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

weather_options = ["Seco ☀️", "Chuva Intermediária 🌧️", "Chuva Forte ⛈️"]

st.title("Setup F1 25 - Cadastro e Consulta")

def hora_brasil():
    return datetime.now(pytz.timezone("America/Sao_Paulo")).strftime("%d/%m/%Y %H:%M")

# Carregamento de dados
if os.path.exists(SETUP_FILE):
    df = pd.read_csv(SETUP_FILE)
    if "Última Atualização" not in df.columns:
        df["Última Atualização"] = ""
    if "Nome do Setup" not in df.columns:
        df["Nome do Setup"] = ""
else:
    df = pd.DataFrame(columns=["Nome do Setup", "Última Atualização"])

def fazer_backup():
    if os.path.exists(SETUP_FILE):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(BACKUP_FOLDER, f"backup_{timestamp}.csv")
        df.to_csv(backup_path, index=False)

def get_value(coluna, padrao):
    if "menu" in st.session_state and st.session_state.menu != "Cadastrar Novo" and coluna in df.columns and st.session_state.menu in df["Nome do Setup"].values:
        valor = df.loc[df["Nome do Setup"] == st.session_state.menu, coluna].values
        if len(valor) > 0:
            return valor[0]
    return padrao

# Botões de setup na sidebar
st.sidebar.title("Setups Salvos")

# Ordenar pelo nome da pista
df_sorted = df.copy()
if "Pista" in df_sorted.columns:
    df_sorted["Pista"] = df_sorted["Pista"].fillna("")
    df_sorted = df_sorted.sort_values(by="Pista", key=lambda x: x.str.lower())
else:
    df_sorted["Pista"] = ""
    df_sorted = df_sorted.sort_values(by="Nome do Setup", key=lambda x: x.str.lower())
setup_names = df_sorted["Nome do Setup"].dropna().tolist()

if st.sidebar.button("➕ Cadastrar Novo Setup"):
    st.session_state.menu = "Cadastrar Novo"
    st.rerun()

for setup in setup_names:
    row = df[df["Nome do Setup"] == setup].fillna("")
    pista = row["Pista"].values[0] if "Pista" in row.columns else ""
    clima = row["Clima"].values[0] if "Clima" in row.columns else ""

    flag = pista.split(" ")[0] if pista else ""
    circuit_name = pista[pista.find(" ")+1:] if pista else ""
    icon = clima.split(" ")[-1] if clima else ""
    clima_nome = " ".join(clima.split(" ")[:-1]) if clima else ""

    label = f"{flag} {circuit_name} | {clima_nome} {icon} | {setup}"

    btn_style = "primary" if "menu" in st.session_state and st.session_state.menu == setup else "secondary"
    if st.sidebar.button(label, key=setup):
        st.session_state.menu = setup
        st.rerun()

# Botão para baixar backup
st.sidebar.markdown("---")
st.sidebar.subheader("Backup dos Setups")

if st.sidebar.download_button(
    label="⬇️ Baixar Backup",
    data=df.to_csv(index=False).encode('utf-8'),
    file_name="backup_setups_f1_25.csv",
    mime="text/csv"
):
    st.toast("Backup baixado com sucesso! 🗃️")

# Upload de backup
uploaded_file = st.sidebar.file_uploader("📤 Importar Backup CSV", type=["csv"])
if uploaded_file:
    try:
        new_df = pd.read_csv(uploaded_file)
        if "Nome do Setup" in new_df.columns:
            df = pd.concat([df, new_df]).drop_duplicates(subset=["Nome do Setup"], keep="last")
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
    setup_info = df[df["Nome do Setup"] == menu]
    if not setup_info.empty:
        data_atualizacao = setup_info.iloc[0].get("Última Atualização", "Não disponível")
        st.info(f"🕒 Última atualização: {data_atualizacao}")

# O restante do código permanece igual, incluindo os sliders, salvamento, exclusão etc.


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
                df = df[df["Nome do Setup"] != menu]
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

# Campos do Setup
nome_setup = st.text_input("Nome do Setup", value=menu if menu != "Cadastrar Novo" else "")
pista = st.selectbox("Pista", tracks, index=tracks.index(get_value("Pista", tracks[0])) if get_value("Pista", tracks[0]) in tracks else 0)
condicao = st.selectbox("Condição Climática", weather_options, index=weather_options.index(get_value("Clima", weather_options[0])) if get_value("Clima", weather_options[0]) in weather_options else 0)

st.subheader("Aerodinâmica")
asa_dianteira = st.slider("Asa Dianteira", 0, 50, int(get_value("Asa Dianteira", 25)))
asa_traseira = st.slider("Asa Traseira", 0, 50, int(get_value("Asa Traseira", 25)))

st.subheader("Transmissão")
diff_on = st.slider("Transmissão Diferencial Pedal On", 0, 100, int(get_value("Transmissão Diferencial Pedal On", 50)), step=5)
diff_off = st.slider("Transmissão Diferencial Pedal Off", 0, 100, int(get_value("Transmissão Diferencial Pedal Off", 50)), step=5)

st.subheader("Geometria da Suspensão")
camb_frontal = st.slider("Cambagem Frontal", -3.5, -2.5, float(get_value("Cambagem Frontal", -3.0)))
camb_tras = st.slider("Cambagem Traseira", -2.0, -1.0, float(get_value("Cambagem Traseira", -1.5)))
toe_diant = st.slider("Toe-out Dianteiro", 0.0, 0.2, float(get_value("Toe-Out Dianteiro", 0.1)))
toe_tras = st.slider("Toe-out Traseiro", 0.1, 0.25, float(get_value("Toe-Out Traseiro", 0.15)))

st.subheader("Suspensão")
susp_diant = st.slider("Suspensão Frontal", 1, 41, int(get_value("Suspensão Frontal", 20)))
susp_tras = st.slider("Suspensão Traseira", 1, 41, int(get_value("Suspensão Traseira", 20)))
anti_roll_d = st.slider("Anti-Roll Dianteiro", 1, 21, int(get_value("Anti-Roll Dianteiro", 10)))
anti_roll_t = st.slider("Anti-Roll Traseiro", 1, 21, int(get_value("Anti-Roll Traseiro", 10)))
altura_d = st.slider("Altura Frontal", 15, 35, int(get_value("Altura Frontal", 25)))
altura_t = st.slider("Altura Traseira", 40, 60, int(get_value("Altura Traseira", 50)))

st.subheader("Freios")
bal_freio = st.slider("Balanceamento de Freios Dianteiro", 50, 70, int(get_value("Balanceamento De Freios Dianteiro", 50)), step=1)
st.caption("Valores menores = mais freio dianteiro")
press_freio = st.slider("Pressão dos freios", 80, 100, int(get_value("Pressão Dos Freios", 95)))

st.subheader("Pneus")
press_dd = st.slider("Pressão Dianteiro Direito", 22.5, 29.5, float(get_value("Pressão Dianteiro Direito", 26.0)), step=0.5)
press_de = st.slider("Pressão Dianteiro Esquerdo", 22.5, 29.5, float(get_value("Pressão Dianteiro Esquerdo", 26.0)), step=0.5)
press_td = st.slider("Pressão Traseiro Direito", 20.5, 26.5, float(get_value("Pressão Traseiro Direito", 23.5)), step=0.5)
press_te = st.slider("Pressão Traseiro Esquerdo", 20.5, 26.5, float(get_value("Pressão Traseiro Esquerdo", 23.5)), step=0.5)

# Botão de salvar
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

        if nome_setup in df["Nome do Setup"].values:
            df.loc[df["Nome do Setup"] == nome_setup, nova_linha.keys()] = nova_linha.values()
        else:
            df = pd.concat([df, pd.DataFrame([nova_linha])], ignore_index=True)

        df.to_csv(SETUP_FILE, index=False)
        fazer_backup()
        st.success("✅ Setup salvo com sucesso!")
        st.balloons()
        time.sleep(3)
        st.rerun()
    else:
        st.warning("⚠️ O nome do setup é obrigatório para salvar.")