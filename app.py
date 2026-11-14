import os
import streamlit as st
import google.generativeai as genai

# Configuração inicial da página
st.set_page_config(
    page_title="Plataforma Cuidado Materno — Plano de Parto",
    page_icon="👶",
    layout="centered",
)

# ⚠️ Alerta de Segurança: Configuração segura da Chave de API
try:
  if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
  else:
    api_key = os.getenv("GEMINI_API_KEY")

  if not api_key:
    st.error(
        "Chave de API do Gemini não encontrada! Configure o st.secrets no"
        " Streamlit Cloud ou a variável de ambiente local."
    )
  else:
    genai.configure(api_key=api_key)
except Exception as e:
    st.error(f"Erro ao configurar a API: {e}")

# [DADO OFICIAL] Função de RAG Local: Lê a base de diretrizes oficiais do Ministério da Saúde e OMS
def carregar_base_conhecimento():
    caminho = "base_conhecimento/diretrizes_oficiais.txt"
    if os.path.exists(caminho):
        with open(caminho, "r", encoding="utf-8") as f:
            return f.read()
    else:
        return """
        [DADO OFICIAL] Lei Federal nº 11.108/2005: Direito a 1 acompanhante de livre escolha.
        [DADO OFICIAL] Diretrizes da OMS: Liberdade de posição, proibição da manobra de Kristeller, consentimento informado obrigatório e contato pele a pele imediato.
        """

# System Instructions rigorosas para o modelo
SYSTEM_INSTRUCTION = """
Você é uma inteligência artificial especialista em direitos reprodutivos, obstetrícia humanizada e políticas públicas de saúde no Brasil. 
Sua função exclusiva é redigir um documento formal, respeitoso e humanizado chamado **Plano de Parto**, com base estritamente nas preferências informadas pela gestante e em conformidade absoluta com as legislações vigentes e diretrizes oficiais recuperadas da base de conhecimento (RAG).
Nunca invente artigos de lei ou diretrizes médicas que não estejam presentes na base oficial fornecida.
"""

# Configuração do modelo Gemini
model = genai.GenerativeModel(
    model_name="gemini-3.8-flash",
    system_instruction=SYSTEM_INSTRUCTION,
    generation_config={
        "temperature": 0.3,
        "max_output_tokens": 2000,
    },
)

# Criação de Abas na Plataforma (Portal de Informações + Gerador)
st.title("👶 Plataforma de Direitos e Plano de Parto Humanizado")
st.markdown(
    "Um espaço seguro para gestantes conhecerem seus direitos e criarem "
    "seu Plano de Parto fundamentado nas diretrizes oficiais da OMS."
)

aba1, aba2 = st.tabs(["📖 Conheça Seus Direitos", "✍️ Gerador de Plano de Parto"])

with aba1:
    st.header("Informações Oficiais para a Gestante")
    st.markdown("""
    Esta plataforma foi desenvolvida para apoiar você e sua família durante a gestação e o parto.
    
    ### 🛡️ Direitos Garantidos por Lei:
    1. **Direito a Acompanhante:** Conforme a **Lei Federal nº 11.108/2005 [DADO OFICIAL]**, toda gestante tem direito a 1 acompanhante de sua livre escolha durante todo o período de internação (pré-parto, parto e pós-parto).
    2. **Consentimento Informado:** Nenhum procedimento (como toque vaginal excessivo, raspagem de pelos, lavagem intestinal ou rompimento artificial da bolsa) pode ser feito sem a explicação prévia e o seu consentimento.
    3. **Liberdade de Posição:** A **OMS [DADO OFICIAL]** recomenda que a mulher adote a posição que preferir no nascimento, evitando a imobilização obrigatória nahorizontal (litotomia).
    4. **Proibição de Práticas Nocivas:** A manobra de Kristeller (pressionar o fundo do útero) é formalmente rejeitada pelas evidências científicas.
    """)

with aba2:
    st.header("Gerador Automatizado de Plano de Parto")
    st.markdown("Preencha as suas preferências abaixo para gerar o seu documento personalizado.")

    with st.form("plano_parto_form"):
        st.subheader("1. Identificação")
        nome = st.text_input("Primeiro Nome ou Apelido (Por segurança, evite nome completo):")
        # [AJUSTE SOLICITADO]: Permitir desde o início da gestação (4 semanas) até o termo (42 semanas)
        semanas = st.number_input("Idade Gestacional (Semanas):", min_value=4, max_value=42, value=32)
        acompanhante = st.text_input("Acompanhante escolhido(a) por lei:")

        st.subheader("2. Ambiência e Conforto")
        ambiente = st.multiselect(
            "Preferências de ambiente:",
            [
                "Luz baixa/suave",
                "Controle de temperatura/ar-condicionado",
                "Música ambiente",
                "Aromaterapia",
                "Privacidade e liberdade para caminhar",
            ]
        )

        st.subheader("3. Intervenções e Procedimentos")
        posicao = st.selectbox(
            "Preferência de posição para o nascimento:",
            [
                "Posições verticalizadas / cócoras / de quatro",
                "Sentada / semi-sentada",
                "Liberdade para mudar de posição conforme o conforto",
            ]
        )
        intervencoes = st.multiselect(
            "Preferências sobre intervenções:",
            [
                "Evitar manobra de Kristeller (pressão na barriga)",
                "Evitar episiotomia de rotina (corte no períneo)",
                "Consentimento informado prévio para qualquer procedimento",
                "Monitoramento fetal intermitente (se sem riscos)",
                "Ingestão de líquidos claros e alimentos leves",
            ]
        )

        st.subheader("4. Cuidados com o Recém-Nascido")
        bebe_cuidados = st.multiselect(
            "Preferências para os primeiros minutos e pós-parto:",
            [
                "Contato pele a pele imediato",
                "Clampeamento tardio do cordão umbilical (1 a 3 minutos)",
                "Início da amamentação na primeira hora de vida",
                "Adiar o primeiro banho do bebê (24 horas ou mais)",
            ]
        )

        submitted = st.form_submit_button("Gerar Meu Plano de Parto")

    if submitted:
        if not nome:
            st.warning("Por favor, preencha ao menos o seu nome ou apelido.")
        else:
            with st.spinner("Consultando base oficial e redigindo seu Plano de Parto..."):
                base_oficial = carregar_base_conhecimento()

                prompt_usuario = f"""
                [DADOS INFORMADOS PELA GESTANTE]
                - Nome/Apelido: {nome}
                - Idade Gestacional: {semanas} semanas
                - Acompanhante: {acompanhante}
                - Ambiência: {', '.join(ambiente)}
                - Posição para o nascimento: {posicao}
                - Intervenções: {', '.join(intervencoes)}
                - Cuidados com o recém-nascido: {', '.join(bebe_cuidados)}

                [BASE DE CONHECIMENTO OFICIAL (RAG)]
                {base_oficial}

                Com base exclusivamente nos dados da gestante e nas diretrizes oficiais recuperadas acima, gere um documento formal, humanizado e estruturado em seções claras, citando de forma elegante as normativas legais aplicáveis.
                """

                try:
                    response = model.generate_content(prompt_usuario)
                    st.success("Plano de Parto gerado com sucesso!")
                    st.markdown("---")
                    st.markdown(response.text)
                    st.markdown("---")
                    st.info(
                        "💡 Dica: Você pode copiar este texto ou imprimi-lo para apresentar "
                        "à equipe médica da maternidade."
                    )
                except Exception as e:
                    st.error(f"Ocorreu um erro ao gerar o plano: {e}")
