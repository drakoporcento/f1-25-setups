import streamlit as st
import pandas as pd
import os

# Caminho do arquivo CSV
SETUP_FILE = 'setups_f1_25.csv'

# Lista de pistas
tracks = [
    "GP da Austrália, Melbourne", "GP da China, Xangai", "GP do Japão, Suzuka",
    "GP do Bahrein, Sakhir", "GP da Arábia Saudita, Jeddah", "GP de Miami, EUA",
    "GP da Emilia-Romagna, Ímola", "GP de Mônaco, Monte Carlo", "GP da Espanha, Barcelona",
    "GP do Canadá, Montreal", "GP da Austria, Red-Bull Ring", "GP da Austria, Red-Bull Ring Invertido",
    "GP da Inglaterra, Silverstone", "GP da Inglaterra, Silverstone Invertido", "GP da Bélgica, Spa-Francorchamps",
    "GP da Hungria, Hungaroring", "GP da Holanda, Zandvoort", "GP da Holanda, Zandvoort Invertido",
    "GP da Itália, Monza", "GP do Azerbaijão, Baku", "GP de Singapura, Marina Bay",
    "GP dos Estados Unidos, Austin Texas", "GP do México, Cidade do México", "GP de São Paulo, Interlagos",
    "GP de Las Vegas, Las Vegas", "GP do Catar, Lusail", "GP de Abu Dhabi, Yas Marina"
]

weather_options = ["Seco", "Chuva Intermediária", "Chuva Forte"]

st.title("Setup F1 25 - Cadastro e Consulta")

if os.path.exists(SETUP_FILE):
    df = pd.read_csv(SETUP_FILE)
    setup_names = ["Cadastrar Novo"] + df["Nome do Setup"].dropna().unique().tolist() if "Nome do Setup" in df.columns else ["Cadastrar Novo"]
else:
    df = pd.DataFrame()
    setup_names = ["Cadastrar Novo"]

menu = st.sidebar.selectbox("Menu", setup_names)

if menu == "Cadastrar Novo":
    st.header("Cadastrar novo setup")
    nome_setup = st.text_input("Nome do Setup")
    pista = st.selectbox("Escolha a pista", tracks)
    clima = st.selectbox("Condição climática", weather_options)

    st.subheader("Aerodinâmica")
    aero_diant = st.slider("Aero Asa Dianteira", 1, 50, 20)
    aero_tras = st.slider("Aero Asa Traseira", 1, 50, 20)

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

    if st.button("Salvar Setup") and nome_setup:
        setup = {
            "Nome do Setup": nome_setup,
            "Pista": pista, "Clima": clima,
            "Aero Asa Dianteira": aero_diant, "Aero Asa Traseira": aero_tras,
            "Transmissão Diferencial Pedal On": diff_on, "Transmissão Diferencial Pedal Off": diff_off,
            "Cambagem Frontal": camb_frontal, "Cambagem Traseira": camb_tras,
            "Toe-out Dianteiro": toe_diant, "Toe-out Traseiro": toe_tras,
            "Suspensão Frontal": susp_diant, "Suspensão Traseira": susp_tras,
            "Anti-Roll Dianteiro": anti_roll_d, "Anti-Roll Traseiro": anti_roll_t,
            "Altura Frontal": altura_d, "Altura Traseira": altura_t,
            "Balanceamento de Freios Dianteiro": bal_freio, "Pressão dos freios": press_freio,
            "Pressão Dianteiro Direito": press_dd, "Pressão Dianteiro Esquerdo": press_de,
            "Pressão Traseiro Direito": press_td, "Pressão Traseiro Esquerdo": press_te
        }

        if os.path.exists(SETUP_FILE):
            df = pd.read_csv(SETUP_FILE)
            df = pd.concat([df, pd.DataFrame([setup])], ignore_index=True)
        else:
            df = pd.DataFrame([setup])

        df.to_csv(SETUP_FILE, index=False)
        st.success("Setup salvo com sucesso!")

elif menu in setup_names:
    st.header(f"Editar Setup: {menu}")

    selected_setup = df[df["Nome do Setup"] == menu].iloc[0]
    nome_setup = selected_setup["Nome do Setup"]
    nome_original = nome_setup  # manter o nome original para atualização

    st.text_input("Nome do Setup", value=nome_setup, disabled=True)

    pista = st.selectbox("Escolha a pista", tracks, index=tracks.index(selected_setup["Pista"]) if selected_setup["Pista"] in tracks else 0)
    clima = st.selectbox("Condição climática", weather_options, index=weather_options.index(selected_setup["Clima"]) if selected_setup["Clima"] in weather_options else 0)

    st.subheader("Aerodinâmica")
    aero_diant = st.slider("Aero Asa Dianteira", 1, 50, int(selected_setup["Aero Asa Dianteira"]))
    aero_tras = st.slider("Aero Asa Traseira", 1, 50, int(selected_setup["Aero Asa Traseira"]))

    st.subheader("Transmissão")
    diff_on = st.slider("Transmissão Diferencial Pedal On", 0, 100, int(selected_setup["Transmissão Diferencial Pedal On"]), step=5)
    diff_off = st.slider("Transmissão Diferencial Pedal Off", 0, 100, int(selected_setup["Transmissão Diferencial Pedal Off"]), step=5)

    st.subheader("Geometria da Suspensão")
    camb_frontal = st.slider("Cambagem Frontal", -3.5, -2.5, float(selected_setup["Cambagem Frontal"]))
    camb_tras = st.slider("Cambagem Traseira", -2.0, -1.0, float(selected_setup["Cambagem Traseira"]))
    toe_diant = st.slider("Toe-out Dianteiro", 0.0, 0.2, float(selected_setup["Toe-out Dianteiro"]))
    toe_tras = st.slider("Toe-out Traseiro", 0.1, 0.25, float(selected_setup["Toe-out Traseiro"]))

    st.subheader("Suspensão")
    susp_diant = st.slider("Suspensão Frontal", 1, 41, int(selected_setup["Suspensão Frontal"]))
    susp_tras = st.slider("Suspensão Traseira", 1, 41, int(selected_setup["Suspensão Traseira"]))
    anti_roll_d = st.slider("Anti-Roll Dianteiro", 1, 21, int(selected_setup["Anti-Roll Dianteiro"]))
    anti_roll_t = st.slider("Anti-Roll Traseiro", 1, 21, int(selected_setup["Anti-Roll Traseiro"]))
    altura_d = st.slider("Altura Frontal", 15, 35, int(selected_setup["Altura Frontal"]))
    altura_t = st.slider("Altura Traseira", 40, 60, int(selected_setup["Altura Traseira"]))

    st.subheader("Freios")
    bal_freio = st.slider("Balanceamento de Freios Dianteiro", 50, 70, int(selected_setup["Balanceamento de Freios Dianteiro"]), step=1)
    st.caption("Valores menores = mais freio dianteiro")
    press_freio = st.slider("Pressão dos freios", 80, 100, int(selected_setup["Pressão dos freios"]))

    st.subheader("Pneus")
    press_dd = st.slider("Pressão Dianteiro Direito", 22.5, 29.5, float(selected_setup["Pressão Dianteiro Direito"]))
    press_de = st.slider("Pressão Dianteiro Esquerdo", 22.5, 29.5, float(selected_setup["Pressão Dianteiro Esquerdo"]))
    press_td = st.slider("Pressão Traseiro Direito", 20.5, 26.5, float(selected_setup["Pressão Traseiro Direito"]))
    press_te = st.slider("Pressão Traseiro Esquerdo", 20.5, 26.5, float(selected_setup["Pressão Traseiro Esquerdo"]))

    if st.button("Salvar Alterações"):
        index = df[df["Nome do Setup"] == nome_original].index[0]
        df.loc[index] = [
            nome_original, pista, clima,
            aero_diant, aero_tras,
            diff_on, diff_off,
            camb_frontal, camb_tras,
            toe_diant, toe_tras,
            susp_diant, susp_tras,
            anti_roll_d, anti_roll_t,
            altura_d, altura_t,
            bal_freio, press_freio,
            press_dd, press_de, press_td, press_te
        ]
        df.to_csv(SETUP_FILE, index=False)
        st.success("Setup atualizado com sucesso!")
