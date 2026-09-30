import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import io
import requests
import json

# Configuração da página e layout expandido
st.set_page_config(layout="wide", page_title="Meu Escritório Virtual - UseOneAI")

# Inicialização do estado interno da aplicação
if "dados_planilha" not in st.session_state:
    st.session_state.dados_planilha = pd.DataFrame(columns=["Data", "Descrição", "Valor"])
if "nome_planilha" not in st.session_state:
    st.session_state.nome_planilha = "minha_planilha"
if "agenda_compromissos" not in st.session_state:
    st.session_state.agenda_compromissos = pd.DataFrame(columns=["Data/Hora", "Compromisso", "Prioridade"])
if "agente_ativo" not in st.session_state:
    st.session_state.agente_ativo = "Enzo - Leitor de E-mails"

# 1. BARRA LATERAL - CONFIGURAÇÃO DA USEONEAI
st.sidebar.title("🏢 Painel de Controle")
st.sidebar.subheader("Conexão UseOneAI")

api_key = st.sidebar.text_input("Sua UseOneAI API Key:", type="password")
endpoint_url = st.sidebar.text_input("Base URL da UseOneAI:", value="https://useoneai.app")
modelo_ia = st.sidebar.text_input("ID do Modelo:", value="chatgpt-5.6-terra")

st.sidebar.write("---")
st.sidebar.subheader("Funcionários Virtuais:")
agente_selecionado = st.sidebar.radio(
    "Agente em foco:",
    ["Enzo - Leitor de E-mails", "Sara - Especialista em Planilhas", "Murilo - Analista de Relatórios", "Helena - Secretária Executiva"],
    index=["Enzo - Leitor de E-mails", "Sara - Especialista em Planilhas", "Murilo - Analista de Relatórios", "Helena - Secretária Executiva"].index(st.session_state.agente_ativo)
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
        const enzo = criarRobo(0x0077ff, -5, 0); 
        const sara = criarRobo(0x00ff77, -1, -2); 
        const murilo = criarRobo(0xff3333, 2, 1);
        const helena = criarRobo(0xaa00ff, 5, -1);

        function animar() {{
            requestAnimationFrame(animate = () => {{
                requestAnimationFrame(animate);
                [enzo, sara, murilo, helena].forEach(r => {{
                    r.userData.mudar++;
                    if(r.userData.mudar > 150) {{ r.userData.velX = (Math.random()-0.5)*0.03; r.userData.velZ = (Math.random()-0.5)*0.03; r.userData.mudar = 0; }}
                    r.position.x += r.userData.velX; r.position.z += r.userData.velZ;
                    if(r.position.x > 13 || r.position.x < -13) r.userData.velX *= -1;
                    if(r.position.z > 8 || r.position.z < -8) r.userData.velZ *= -1;
                    if(r.userData.pulando) {{ r.userData.tempoPulo += 0.2; r.position.y = Math.abs(Math.sin(r.userData.tempoPulo)) * 1.5; if(r.userData.tempoPulo > Math.PI) {{ r.userData.pulando = false; r.position.y = 0; }} }}
                }});
                renderer.render(scene, camera);
            }});
        }}
        animar();

        const SpeechRecognition = window.StrawberrySpeech || window.SpeechRecognition || window.webkitSpeechRecognition;
        if (SpeechRecognition) {{
            const recognition = new SpeechRecognition(); recognition.continuous = true; recognition.lang = 'pt-BR';
            recognition.onresult = function(event) {{
                const resultado = event.results[event.results.length - 1].transcript.trim();
                const textoMinusculo = resultado.toLowerCase();
                let agenteDetectado = "";
                if (textoMinusculo.startsWith("enzo")) {{ agenteDetectado = "Enzo - Leitor de E-mails"; enzo.userData.pulando = true; enzo.userData.tempoPulo = 0; }}
                else if (textoMinusculo.startsWith("sara")) {{ agenteDetectado = "Sara - Especialista em Planilhas"; sara.userData.pulando = true; sara.userData.tempoPulo = 0; }}
                else if (textoMinusculo.startsWith("murilo")) {{ agenteDetectado = "Murilo - Analista de Relatórios"; murilo.userData.pulando = true; murilo.userData.tempoPulo = 0; }}
                else if (textoMinusculo.startsWith("helena")) {{ agenteDetectado = "Helena - Secretária Executiva"; helena.userData.pulando = true; helena.userData.tempoPulo = 0; }}
                if (agenteDetectado !== "") {{ window.parent.postMessage({{type: 'streamlit:setComponentValue', value: {{ agente: agenteDetectado, comando: resultado }}}}, '*'); }}
            }};
            recognition.onend = function() {{ recognition.start(); }}; recognition.start();
        }}
    </script>
</body>
</html>
"""
components.html(html_voice_and_3d, height=270)

# --- REQUISIÇÃO PARA O GATEWAY USEONEAI ---
def chamar_modelo_useoneai(prompt_sistema, comando_usuario):
    if not api_key:
        return "⚠️ Insira a API Key na barra lateral."
    base_url = endpoint_url.strip().rstrip('/')
    url_completa = f"{base_url}/chat/completions"
    headers = {"Authorization": f"Bearer {api_key.strip()}", "Content-Type": "application/json"}
    payload = {
        "model": modelo_ia.strip(),
        "messages": [{"role": "system", "content": prompt_sistema}, {"role": "user", "content": comando_usuario}],
        "temperature": 0.2
    }
    try:
        response = requests.post(url_completa, json=payload, headers=headers)
        if response.status_code != 200:
            return f"❌ Erro {response.status_code}: {response.text}"
        return response.json()['choices']['message']['content']
    except Exception as e:
        return f"❌ Falha de rede: {str(e)}"

# Caixa de Entrada por Texto
comando_final = st.text_input(f"Dê uma ordem para o agente ativo ({st.session_state.agente_ativo}):")

if comando_final:
    st.write("---")
    st.subheader(f"💬 Resposta de {st.session_state.agente_ativo.split(' - ')[0]}")
    
    # Execução do Enzo
    if st.session_state.agente_ativo == "Enzo - Leitor de E-mails":
        prompt = "Você é o Enzo, especialista em e-mails. Resuma a mensagem em 3 tópicos e gere uma resposta profissional."
        st.write(chamar_modelo_useoneai(prompt, comando_final))
        
    # Execução da Sara
    if st.session_state.agente_ativo == "Sara - Especialista em Planilhas":
        prompt = "Você é a Sara. Retorne estritamente um código JSON estruturado no formato: {\"NomePlanilha\": \"nome\", \"Linhas\": [{\"Data\": \"AAAA-MM-DD\", \"Descrição\": \"Texto\", \"Valor\": 0.0}]}"
        resposta_bruta = chamar_modelo_useoneai(prompt, comando_final)
        try:
            texto_limpo = resposta_bruta.strip().replace("```json", "").replace("```", "")
            dados_limpos = json.loads(texto_limpo)
            novas_linhas = pd.DataFrame(dados_limpos["Linhas"])
            st.session_state.dados_planilha = pd.concat([st.session_state.dados_planilha, novas_linhas], ignore_index=True)
            if "NomePlanilha" in dados_limpos: 
                st.session_state.nome_planilha = dados_limpos["NomePlanilha"]
            st.success("📊 Sara atualizou a planilha!")
        except:
            st.info(f"💁‍♀️ **Sara:** {resposta_bruta}")
            
    # Execução do Murilo
    if st.session_state.agente_ativo == "Murilo - Analista de Relatórios":
        contexto_planilha = st.session_state.dados_planilha.to_string()
        prompt = f"Você é o Murilo, analista estratégico. Baseado nestes dados:\n{contexto_planilha}\n\nMonte um relatório executivo."
        st.write(chamar_modelo_useoneai(prompt, comando_final))

    # Execução da Helena
    if st.session_state.agente_ativo == "Helena - Secretária Executiva":
        prompt = "Você é a Helena, secretária executiva. Retorne obrigatoriamente um objeto JSON puro no formato: {\"Compromissos\": [{\"DataHora\": \"DD/MM AAAA - HH:MM\", \"Compromisso\": \"Descrição\", \"Prioridade\": \"Alta/Média/Baixa\"}]}"
        resposta_bruta = chamar_modelo_useoneai(prompt, comando_final)
        try:
