import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import io
import requests

# Configuração da página e layout expandido
st.set_page_config(layout="wide", page_title="Meu Escritório Virtual - UseOneAI")

# Inicialização do estado interno da aplicação
if "dados_planilha" not in st.session_state:
    st.session_state.dados_planilha = pd.DataFrame(columns=["Data", "Descrição", "Valor"])
if "nome_planilha" not in st.session_state:
    st.session_state.nome_planilha = "minha_planilha"
if "agente_ativo" not in st.session_state:
    st.session_state.agente_ativo = "Enzo - Leitor de E-mails"

# 1. BARRA LATERAL - CONFIGURAÇÃO DA USEONEAI
st.sidebar.title("🏢 Painel de Controle")
st.sidebar.subheader("Conexão UseOneAI")

# Campos de autenticação da plataforma informada
api_key = st.sidebar.text_input("Sua UseOneAI API Key:", type="password", help="Insira a chave gerada no painel da UseOneAI.")
endpoint_url = st.sidebar.text_input("Endpoint API da UseOneAI:", value="https://useoneai.app", help="Ajuste o endereço de rota se a plataforma fornecer um link específico.")
modelo_ia = st.sidebar.text_input("ID do Modelo (ex: gpt-4o ou deepseek):", value="gpt-4o", help="Digite o identificador exato do modelo que deseja consumir dentro da UseOneAI.")

st.sidebar.write("---")
st.sidebar.subheader("Funcionários Virtuais:")
agente_selecionado = st.sidebar.radio(
    "Agente em foco:",
    ["Enzo - Leitor de E-mails", "Sara - Especialista em Planilhas", "Murilo - Analista de Relatórios"],
    index=["Enzo - Leitor de E-mails", "Sara - Especialista em Planilhas", "Murilo - Analista de Relatórios"].index(st.session_state.agente_ativo)
)
st.session_state.agente_ativo = agente_selecionado

# 2. TELA CENTRAL - CENÁRIO INTERATIVO 3D + CAPTURA DE VOZ CONTÍNUA
st.title("🖥️ Seu Escritório Virtual Inteligente")

html_voice_and_3d = f"""
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <style>
        body {{ margin: 0; overflow: hidden; background-color: #111; font-family: sans-serif; }}
        canvas {{ width: 100%; height: 260px; display: block; }}
        #status {{ position: absolute; top: 10px; left: 10px; color: #00ff77; font-size: 12px; background: rgba(0,0,0,0.6); padding: 5px 10px; border-radius: 4px; }}
    </style>
    <script src="https://cloudflare.com"></script>
</head>
<body>
    <div id="status">🎙️ Microfone Ativo: Ouvindo comandos...</div>
    <script>
        const scene = new THREE.Scene(); scene.background = new THREE.Color(0x0a0a0a);
        const camera = new THREE.PerspectiveCamera(45, window.innerWidth / 260, 0.1, 1000);
        camera.position.set(0, 8, 16); camera.lookAt(0, 0, 0);
        const renderer = new THREE.WebGLRenderer({{ antialias: true }});
        renderer.setSize(window.innerWidth, 260); document.body.appendChild(renderer.domElement);
        scene.add(new THREE.AmbientLight(0xffffff, 0.7));
        const light = new THREE.DirectionalLight(0xffffff, 0.6); light.position.set(5, 15, 5); scene.add(light);
        const floor = new THREE.Mesh(new THREE.PlaneGeometry(30, 20), new THREE.MeshStandardMaterial({{ color: 0x1c1c1c }}));
        floor.rotation.x = -Math.PI / 2; scene.add(floor);

        function criarRobo(cor, x, z) {{
            const grupo = new THREE.Group();
            const corpo = new THREE.Mesh(new THREE.BoxGeometry(0.8, 1.2, 0.8), new THREE.MeshStandardMaterial({{ color: cor }})); corpo.position.y = 1; grupo.add(corpo);
            const cabeca = new THREE.Mesh(new THREE.BoxGeometry(0.6, 0.5, 0.6), new THREE.MeshStandardMaterial({{ color: 0xdddddd }})); cabeca.position.y = 1.9; grupo.add(cabeca);
            grupo.position.set(x, 0, z); grupo.userData = {{ velX: (Math.random()-0.5)*0.03, velZ: (Math.random()-0.5)*0.03, mudar: 0, pulando: false, tempoPulo: 0 }};
            scene.add(grupo); return grupo;
        }}
        const enzo = criarRobo(0x0077ff, -4, 0); const sara = criarRobo(0x00ff77, 0, -2); const murilo = criarRobo(0xff3333, 4, 1);

        function animar() {{
            requestAnimationFrame(animar);
            [enzo, sara, murilo].forEach(r => {{
                r.userData.mudar++;
                if(r.userData.mudar > 150) {{ r.userData.velX = (Math.random()-0.5)*0.03; r.userData.velZ = (Math.random()-0.5)*0.03; r.userData.mudar = 0; }}
                r.position.x += r.userData.velX; r.position.z += r.userData.velZ;
                if(r.position.x > 13 || r.position.x < -13) r.userData.velX *= -1;
                if(r.position.z > 8 || r.position.z < -8) r.userData.velZ *= -1;
                if(r.userData.pulando) {{ r.userData.tempoPulo += 0.2; r.position.y = Math.abs(Math.sin(r.userData.tempoPulo)) * 1.5; if(r.userData.tempoPulo > Math.PI) {{ r.userData.pulando = false; r.position.y = 0; }} }}
            }});
            renderer.render(scene, camera);
        }}
        animar();

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (SpeechRecognition) {{
            const recognition = new SpeechRecognition(); recognition.continuous = true; recognition.lang = 'pt-BR';
            recognition.onresult = function(event) {{
                const resultado = event.results[event.results.length - 1].transcript.trim();
                const textoMinusculo = resultado.toLowerCase();
                let agenteDetectado = "";
                if (textoMinusculo.startsWith("enzo")) {{ agenteDetectado = "Enzo - Leitor de E-mails"; enzo.userData.pulando = true; enzo.userData.tempoPulo = 0; }}
                else if (textoMinusculo.startsWith("sara")) {{ agenteDetectado = "Sara - Especialista em Planilhas"; sara.userData.pulando = true; sara.userData.tempoPulo = 0; }}
                else if (textoMinusculo.startsWith("murilo")) {{ agenteDetectado = "Murilo - Analista de Relatórios"; murilo.userData.pulando = true; murilo.userData.tempoPulo = 0; }}
                if (agenteDetectado !== "") {{ window.parent.postMessage({{type: 'streamlit:setComponentValue', value: {{ agente: agenteDetectado, comando: resultado }}}}, '*'); }}
            }};
            recognition.onend = function() {{ recognition.start(); }}; recognition.start();
        }}
    </script>
</body>
</html>
"""
components.html(html_voice_and_3d, height=270)

# --- CHAMADA INTEGRADA VIA REQUISIÇÃO DE API (FORMATO PADRÃO OPENAI) ---
def chamar_modelo_useoneai(prompt_sistema, comando_usuario):
    if not api_key:
        return "⚠️ Insira os dados de autenticação da UseOneAI na barra lateral para ativar os robôs."
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": modelo_ia,
        "messages": [
            {"role": "system", "content": prompt_sistema},
            {"role": "user", "content": comando_usuario}
        ],
        "temperature": 0.3
    }
    try:
        response = requests.post(endpoint_url, json=payload, headers=headers)
        return response.json()['choices']['message']['content']
    except Exception as e:
        return f"❌ Conexão recusada com o gateway UseOneAI. Verifique a URL do endpoint e sua chave. ({str(e)})"

# Caixa de Entrada por Texto (Funciona igual ao comando capturado por voz)
comando_final = st.text_input(f"Dê uma ordem para o agente ativo ({st.session_state.agente_ativo}):")

if comando_final:
    st.write("---")
    st.subheader(f"💬 Resposta de {st.session_state.agente_ativo.split(' - ')[0]}")
    
    if st.session_state.agente_ativo == "Enzo - Leitor de E-mails":
        prompt = "Você é o Enzo, assistente especialista em ler e responder e-mails. Resuma a mensagem do usuário em 3 tópicos e gere um rascunho de resposta polida."
        resposta_enzo = chamar_modelo_useoneai(prompt, comando_final)
        st.write(resposta_enzo)
        
    elif st.session_state.agente_ativo == "Sara - Especialista em Planilhas":
        prompt = (
            "Você é a Sara, assistente especialista em dados. O usuário vai ditar entradas para uma planilha. "
            "Filtre os dados corporativos e monte obrigatoriamente um objeto JSON puro no formato: "
            '{"NomePlanilha": "nome_da_tabela", "Linhas": [{"Data": "AAAA-MM-DD", "Descrição": "Texto", "Valor": 0.0}]}. '
            "Não adicione textos explicativos fora do JSON."
        )
        resposta_json = chamar_modelo_useoneai(prompt, comando_final)
        try:
            import json
            dados_limpos = json.loads(resposta_json.strip().replace("```json", "").replace("```", ""))
            novas_linhas = pd.DataFrame(dados_limpos["Linhas"])
            st.session_state.dados_planilha = pd.concat([st.session_state.dados_planilha, novas_linhas], ignore_index=True)
            if "NomePlanilha" in dados_limpos: 
                st.session_state.nome_planilha = dados_limpos["NomePlanilha"]
            st.success("📊 Sara adicionou os novos dados à tabela!")
        except:
            st.info(f"💁‍♀️ **Sara:** {resposta_json}")
            
    elif st.session_state.agente_ativo == "Murilo - Analista de Relatórios":
        contexto_planilha = st.session_state.dados_planilha.to_string()
        prompt = f"Você é o Murilo, analista estratégico de negócios. Baseado nos dados vigentes da planilha:\n{contexto_planilha}\n\nAnalise o comando do usuário e elabore um relatório executivo apontando falhas e planos de ação."
        resposta_murilo = chamar_modelo_useoneai(prompt, comando_final)
        st.write(resposta_murilo)

# RENDERIZAÇÃO DA PLANILHA EM MEMÓRIA
if len(st.session_state.dados_planilha) > 0:
    st.write("---")
    st.subheader(f"📊 Planilha em Edição: `{st.session_state.nome_planilha}.xlsx`")
    st.dataframe(st.session_state.dados_planilha, use_container_width=True)
    
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
