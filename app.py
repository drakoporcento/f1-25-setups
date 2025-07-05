import streamlit as st
import pandas as pd
import os
from datetime import datetime
import pytz

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

# Lista de pistas com bandeiras
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

# Função auxiliar para horário com fuso do Brasil
def hora_brasil():
    return datetime.now(pytz.timezone("America/Sao_Paulo")).strftime("%d/%m/%Y %H:%M")

# Carregamento de dados
if os.path.exists(SETUP_FILE):
    df = pd.read_csv(SETUP_FILE)
    if "Última Atualização" not in df.columns:
        df["Última Atualização"] = ""
    if "Nome do Setup" not in df.columns:
        df["Nome do Setup"] = ""
    setup_names = ["Cadastrar Novo"] + df["Nome do Setup"].dropna().unique().tolist()
else:
    df = pd.DataFrame()
    setup_names = ["Cadastrar Novo"]

menu = st.sidebar.selectbox("Menu", setup_names)

# Função de backup automático
def fazer_backup():
    if os.path.exists(SETUP_FILE):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(BACKUP_FOLDER, f"backup_{timestamp}.csv")
        df.to_csv(backup_path, index=False)

# Mostrar data da última atualização
if menu != "Cadastrar Novo" and not df.empty:
    setup_info = df[df["Nome do Setup"] == menu]
    if not setup_info.empty:
        data_atualizacao = setup_info.iloc[0].get("Última Atualização", "Não disponível")
        st.info(f"🕒 Última atualização: {data_atualizacao}")

# Lógica de exclusão do setup
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

# Edição ou cadastro de setups
if menu:
    if menu == "Cadastrar Novo":
        st.header("Cadastrar Novo Setup")
        setup_info = pd.DataFrame()
    else:
        st.header(f"Editar Setup: {menu}")
        setup_info = df[df["Nome do Setup"] == menu]

    def get_value(campo, padrao):
        if not setup_info.empty and campo in setup_info.columns:
            valor = setup_info.iloc[0][campo]
            return valor if pd.notna(valor) else padrao
        return padrao

    nome_setup = st.text_input("Nome do Setup", value=menu if menu != "Cadastrar Novo" else "")
    pista = st.selectbox("Escolha a pista", tracks, index=tracks.index(get_value("Pista", tracks[0])))
    clima = st.selectbox("Condição Climática", weather_options, index=weather_options.index(get_value("Clima", weather_options[0])))

    st.subheader("Aerodinâmica")
    asa_dianteira = st.slider("Asa Dianteira", 1, 50, int(get_value("Asa Dianteira", 25)))
    asa_traseira = st.slider("Asa Traseira", 1, 50, int(get_value("Asa Traseira", 25)))

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
    press_dd = st.slider("Pressão Dianteiro Direito", 22.5, 29.5, float(get_value("Pressão Dianteiro Direito", 26.0)))
    press_de = st.slider("Pressão Dianteiro Esquerdo", 22.5, 29.5, float(get_value("Pressão Dianteiro Esquerdo", 26.0)))
    press_td = st.slider("Pressão Traseiro Direito", 20.5, 26.5, float(get_value("Pressão Traseiro Direito", 23.5)))
    press_te = st.slider("Pressão Traseiro Esquerdo", 20.5, 26.5, float(get_value("Pressão Traseiro Esquerdo", 23.5)))

    if st.button("📀 Salvar Alterações"):
        novo_registro = {
            "Nome do Setup": nome_setup,
            "Pista": pista,
            "Clima": clima,
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
            "Pressão Traseiro Esquerdo": press_te,
            "Última Atualização": hora_brasil()
        }

        if nome_setup in df["Nome do Setup"].values:
            df.loc[df["Nome do Setup"] == nome_setup, novo_registro.keys()] = novo_registro.values()
        else:
            df = pd.concat([df, pd.DataFrame([novo_registro])], ignore_index=True)

        df.to_csv(SETUP_FILE, index=False)
        fazer_backup()
        st.success("Setup salvo com sucesso!")
        st.rerun()