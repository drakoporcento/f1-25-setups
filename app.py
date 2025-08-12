import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import pytz
import time

# ======================= CONFIGURAÇÕES DE ACESSO =======================
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

# ======================= CONFIGURANDO GOOGLE SHEETS =======================
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Lê as credenciais a partir dos segredos
creds = ServiceAccountCredentials.from_json_keyfile_dict(
    st.secrets["gcp"], scope
)
client = gspread.authorize(creds)
sheet = client.open("setups_f1_25").sheet1

# Colunas usadas no app
COLUNAS = [
    "Nome do Setup", "Última Atualização", "Pista", "Clima",
    "Asa Dianteira", "Asa Traseira",
    "Transmissão Diferencial Pedal On", "Transmissão Diferencial Pedal Off",
    "Cambagem Frontal", "Cambagem Traseira", "Toe-Out Dianteiro", "Toe-Out Traseiro",
    "Suspensão Frontal", "Suspensão Traseira",
    "Anti-Roll Dianteiro", "Anti-Roll Traseiro",
    "Altura Frontal", "Altura Traseira",
    "Balanceamento De Freios Dianteiro", "Pressão Dos Freios",
    "Pressão Dianteiro Direito", "Pressão Dianteiro Esquerdo",
    "Pressão Traseiro Direito", "Pressão Traseiro Esquerdo"
]

# Funções de persistência
def carregar_dados():
    records = sheet.get_all_records()
    if not records:
        return pd.DataFrame(columns=COLUNAS)
    df = pd.DataFrame(records)
    df["Chave"] = df["Nome do Setup"] + "__" + df["Pista"] + "__" + df["Clima"]
    return df

def salvar_setup(dados):
    df = carregar_dados()
    chave = f"{dados['Nome do Setup']}__{dados['Pista']}__{dados['Clima']}"
    if 'Chave' not in df.columns:
        df['Chave'] = df["Nome do Setup"] + "__" + df["Pista"] + "__" + df["Clima"]
    if chave in df['Chave'].values:
        idx = df.index[df['Chave'] == chave][0] + 2  # +2 devido ao cabeçalho na linha 1
        sheet.update(f"A{idx}", [list(dados.values())])
    else:
        sheet.append_row(list(dados.values()))

def excluir_setup(chave):
    df = carregar_dados()

    # Garante a coluna 'Chave'
    if "Chave" not in df.columns:
        df["Chave"] = df["Nome do Setup"] + "__" + df["Pista"] + "__" + df["Clima"]

    if chave in df["Chave"].values:
        # Linha na planilha (1 = cabeçalho). DataFrame é 0-based -> +2
        idx = int(df.index[df["Chave"] == chave][0]) + 2

        # A API do Sheets usa índices 0-based para ranges
        start = int(idx) - 1   # início 0-based
        end   = int(idx)       # fim exclusivo 0-based

        # sheet.id às vezes vem como str; garanta int
        sheet_id = int(sheet.id)

        body = {
            "requests": [
                {
                    "deleteDimension": {
                        "range": {
                            "sheetId": sheet_id,
                            "dimension": "ROWS",
                            "startIndex": start,
                            "endIndex": end
                        }
                    }
                }
            ]
        }

        # IMPORTANTÍSSIMO: o batch_update deve ser chamado no Spreadsheet,
        # não no Worksheet
        sheet.spreadsheet.batch_update(body)

# ======================= DADOS ESTÁTICOS PARA A INTERFACE =======================
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

setup_descriptions = {
    "Aerodinâmica": "A aerodinâmica ajusta a força que 'cola' o carro no chão. Por exemplo, uma asa dianteira em 20 e traseira em 10 resulta em mais pressão na frente...",
    "Transmissão": "Define como o carro transfere a potência para as rodas. Um diferencial ON em 80% faz com que ambas as rodas traseiras girem de forma mais parecida...",
    "Geometria da Suspensão": "Ajusta a angulação das rodas. Mais cambagem (ex: -3.5) melhora aderência nas curvas, mas desgasta mais os pneus...",
    "Suspensão": "Controla a rigidez e estabilidade do carro:\n- Suspensões mais duras (ex: 35) deixam o carro mais ágil e responsivo...",
    "Freios": "Ajusta o equilíbrio da frenagem entre frente e traseira. Um valor de 70% dianteiro concentra a força de frenagem na frente...",
    "Pneus": "Pressão afeta aderência e desgaste. Pressões mais baixas (ex: 22.5) aumentam a área de contato, melhorando aderência..."
}

def titulo_setup_com_info(nome):
    info = setup_descriptions.get(nome, "")
    return st.markdown(f'<div class="setup-section-title">{nome} <span title="{info}" style="cursor: help;">ℹ️</span></div>', unsafe_allow_html=True)

weather_options = ["Seco ☀️", "Chuva Intermediária 🌧️", "Chuva Forte ⛈️"]

st.set_page_config(layout="wide")
st.markdown("""
    <style>
        .block-container { padding-top: 1rem; padding-bottom: 1rem; }
        .stSlider > div[data-baseweb="slider"] { width: 90% !important; margin: auto !important; }
        .setup-section-title { text-align: center; font-weight: 600; font-size: 1.2rem; margin-top: 1rem; margin-bottom: 0.5rem; }
        [data-testid="column"] { padding-left: 0.5rem; padding-right: 0.5rem; }
    </style>
""", unsafe_allow_html=True)

st.title("Setup F1 25 - Cadastro e Consulta")

def hora_brasil():
    return datetime.now(pytz.timezone("America/Sao_Paulo")).strftime("%d/%m/%Y %H:%M")

# Carrega dados da planilha
df = carregar_dados()

# Função para pegar valores padrão
def get_value(coluna, padrao):
    if "menu" in st.session_state and st.session_state.menu != "Cadastrar Novo":
        row = df[
            (df["Nome do Setup"] == st.session_state.menu.split("__")[0]) &
            (df["Pista"] == st.session_state.menu.split("__")[1])
        ]
        if not row.empty and coluna in row.columns:
            return row[coluna].values[0]
    return padrao

# ======================= SIDEBAR COM LISTA DE SETUPS =======================
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
    unique_key = f"{setup}__{pista}__{clima}"
    if st.sidebar.button(label, key=unique_key):
        st.session_state.menu = unique_key
        st.rerun()

# Backup download
st.sidebar.markdown("---")
st.sidebar.subheader("Backup dos Setups")
if st.sidebar.download_button(
    "⬇️ Baixar Backup",
    data=carregar_dados().to_csv(index=False).encode('utf-8'),
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
            for _, row in new_df.iterrows():
                salvar_setup(row.to_dict())
            st.sidebar.success("Backup importado com sucesso!")
            st.rerun()
        else:
            st.sidebar.error("Arquivo inválido. Verifique se possui a coluna 'Nome do Setup'.")
    except Exception as e:
        st.sidebar.error(f"Erro ao importar backup: {e}")

# ======================= LOGICA DO MENU =======================
if "menu" not in st.session_state:
    st.session_state.menu = "Cadastrar Novo"
menu = st.session_state.menu

setup_nome = ""
setup_pista = tracks[0]
setup_clima = weather_options[0]

if menu != "Cadastrar Novo" and not df.empty:
    parts = menu.split("__")
    setup_nome = parts[0]
    setup_pista = parts[1]
    setup_clima = parts[2] if len(parts) > 2 else weather_options[0]

    setup_info = df[
        (df["Nome do Setup"] == setup_nome) &
        (df["Pista"] == setup_pista) &
        (df["Clima"] == setup_clima)
    ]
    if not setup_info.empty:
        data_atualizacao = setup_info.iloc[0].get("Última Atualização", "Não disponível")
        st.info(f"🕒 Última atualização: {data_atualizacao}")

# ======================= EXCLUSÃO =======================
if menu != "Cadastrar Novo" and not df.empty:
    st.markdown("---")
    if "delete_clicked" not in st.session_state:
        st.session_state.delete_clicked = False

    if st.session_state.delete_clicked:
        st.warning("Tem certeza que deseja excluir este setup?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Confirmar Exclusão"):
                excluir_setup(f"{setup_nome}__{setup_pista}__{setup_clima}")
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

# ======================= FORMULÁRIO DE CADASTRO/EDIÇÃO =======================
st.markdown("## Cadastro de Setup")
col_a, col_b, col_c = st.columns(3)

with col_a:
    nome_setup = st.text_input("Nome do Setup", value=setup_nome if menu != "Cadastrar Novo" else "")

with col_b:
    pista = st.selectbox("Pista", tracks, index=tracks.index(setup_pista) if setup_pista in tracks else 0)

with col_c:
    condicao = st.selectbox("Condição Climática", weather_options, index=weather_options.index(setup_clima) if setup_clima in weather_options else 0)

with st.expander("🔧 Configurações do Setup", expanded=True):
    col1, col2, col3 = st.columns(3)

    with col1:
        titulo_setup_com_info("Aerodinâmica")
        asa_dianteira = st.slider("Dianteira", 0, 50, int(get_value("Asa Dianteira", 25)))
        asa_traseira  = st.slider("Traseira" , 0, 50, int(get_value("Asa Traseira" , 25)))

        titulo_setup_com_info("Transmissão")
        diff_on  = st.slider("Diferencial ON" , 0, 100, int(get_value("Transmissão Diferencial Pedal On" , 50)), step=5)
        diff_off = st.slider("Diferencial OFF", 0, 100, int(get_value("Transmissão Diferencial Pedal Off", 50)), step=5)

        titulo_setup_com_info("Geometria da Suspensão")
        camb_frontal = st.slider("Cambagem Frontal" , -3.5, -2.5, float(get_value("Cambagem Frontal" , -3.5)))
        camb_tras    = st.slider("Cambagem Traseira" , -2.0, -1.0, float(get_value("Cambagem Traseira", -2.0)))
        toe_diant    = st.slider("Toe-Out Dianteiro", 0.0, 0.2, float(get_value("Toe-Out Dianteiro", 0.0)))
        toe_tras     = st.slider("Toe-Out Traseiro" , 0.1, 0.25, float(get_value("Toe-Out Traseiro",  0.10)))

    with col2:
        titulo_setup_com_info("Suspensão")
        susp_diant = st.slider("Frontal", 1, 41, int(get_value("Suspensão Frontal", 20)))
        susp_tras  = st.slider("Traseira", 1, 41, int(get_value("Suspensão Traseira", 20)))
        anti_roll_d = st.slider("Anti-Roll D", 1, 21, int(get_value("Anti-Roll Dianteiro", 10)))
        anti_roll_t = st.slider("Anti-Roll T", 1, 21, int(get_value("Anti-Roll Traseiro", 10)))
        altura_d = st.slider("Altura Frontal", 15, 35, int(get_value("Altura Frontal", 25)))
        altura_t = st.slider("Altura Traseira", 40, 60, int(get_value("Altura Traseira", 50)))

    with col3:
        titulo_setup_com_info("Freios")
        bal_freio   = st.slider("Balanceamento Dianteiro", 50, 70, int(get_value("Balanceamento De Freios Dianteiro", 50)), step=1)
        press_freio = st.slider("Pressão dos Freios"     , 80, 100, int(get_value("Pressão Dos Freios", 95)))

        titulo_setup_com_info("Pneus")
        press_dd = st.slider("Dianteiro Direito",  22.5, 29.5, float(get_value("Pressão Dianteiro Direito", 26.0)), step=0.5)
        press_de = st.slider("Dianteiro Esquerdo", 22.5, 29.5, float(get_value("Pressão Dianteiro Esquerdo", 26.0)), step=0.5)
        press_td = st.slider("Traseiro Direito" ,  20.5, 26.5, float(get_value("Pressão Traseiro Direito", 23.5)), step=0.5)
        press_te = st.slider("Traseiro Esquerdo",  20.5, 26.5, float(get_value("Pressão Traseiro Esquerdo", 23.5)), step=0.5)

# ======================= SALVAR ALTERAÇÕES =======================
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
        salvar_setup(nova_linha)
        st.success("✅ Setup salvo com sucesso!")
        st.balloons()
        time.sleep(2)
        st.rerun()
    else:
        st.warning("⚠️ O nome do setup é obrigatório para salvar.")
