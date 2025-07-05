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
    setup_names = ["Cadastrar Novo"] + df["Nome do Setup"].dropna().unique().tolist() if "Nome do Setup" in df.columns else ["Cadastrar Novo"]
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

    if st.button("🗑️ Excluir Setup"):
        if not st.session_state.delete_clicked:
            st.session_state.delete_clicked = True
            st.experimental_rerun()
        else:
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
                    st.experimental_rerun()

# Função para campos padrão
def campos_comuns():
    pista = st.selectbox("Escolha a pista", tracks)
    clima = st.selectbox("Condição Climática", weather_options)
    asa_dianteira = st.slider("Asa Dianteira", 1, 50, 25)
    asa_traseira = st.slider("Asa Traseira", 1, 50, 25)

    st.subheader("Transmissão")
    diff_on = st.slider("Transmissão Diferencial Pedal On", 0, 100, 50, step=5)
    diff_off = st.slider("Transmissão Diferencial Pedal Off", 0, 100, 50, step=5)

    st.subheader("Geometria da Suspensão")
    camb_frontal = st.slider("Cambagem Frontal", -3.5, -2.5, -3.0)
    camb_tras = st.slider("Cambagem Traseira", -2.0, -1.0, -1.5)
    toe_diant = st.slider("Toe-out Dianteiro", 0.0, 0.2, 0.1)
    toe_tras = st.slider("Toe-out Traseiro", 0.1, 0.25, 0.15)

    st.subheader("Suspensão")
    susp_diant = st.slider("Suspensão Frontal", 1, 41, 20)
    susp_tras = st.slider("Suspensão Traseira", 1, 41, 20)
    anti_roll_d = st.slider("Anti-Roll Dianteiro", 1, 21, 10)
    anti_roll_t = st.slider("Anti-Roll Traseiro", 1, 21, 10)
    altura_d = st.slider("Altura Frontal", 15, 35, 25)
    altura_t = st.slider("Altura Traseira", 40, 60, 50)

    st.subheader("Freios")
    bal_freio = st.slider("Balanceamento de Freios Dianteiro", 50, 70, 50, step=1)
    st.caption("Valores menores = mais freio dianteiro")
    press_freio = st.slider("Pressão dos freios", 80, 100, 95)

    st.subheader("Pneus")
    press_dd = st.slider("Pressão Dianteiro Direito", 22.5, 29.5, 26.0)
    press_de = st.slider("Pressão Dianteiro Esquerdo", 22.5, 29.5, 26.0)
    press_td = st.slider("Pressão Traseiro Direito", 20.5, 26.5, 23.5)
    press_te = st.slider("Pressão Traseiro Esquerdo", 20.5, 26.5, 23.5)

    return locals()

# Cadastro ou Edição do Setup
if menu == "Cadastrar Novo":
    st.header("Cadastrar Novo Setup")
    nome_setup = st.text_input("Nome do Setup", key="novo_nome_setup")
    valores = campos_comuns()
else:
    st.header(f"Editar Setup: {menu}")
    nome_setup = menu
    valores = campos_comuns()

# Botão de salvar
if st.button("💾 Salvar Alterações"):
    if nome_setup:
        novo_setup = {"Nome do Setup": nome_setup, "Última Atualização": hora_brasil()}
        for k, v in valores.items():
            if k != "nome_setup":
                novo_setup[k.replace("_", " ").title()] = v

        if menu == "Cadastrar Novo":
            df = pd.concat([df, pd.DataFrame([novo_setup])], ignore_index=True)
            st.success("Novo setup cadastrado com sucesso!")
        else:
            index = df[df["Nome do Setup"] == nome_setup].index
            for col in novo_setup:
                df.loc[index, col] = novo_setup[col]
            st.success("Setup atualizado com sucesso!")

        df.to_csv(SETUP_FILE, index=False)
        fazer_backup()
        st.stop()
    else:
        st.warning("⚠️ Por favor, insira um nome para o setup.")
