import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import io
import requests
import json

# Configuração da página e layout expandido
st.set_page_config(layout="wide", page_title="Minha Secretária Virtual - Helena")

# Inicialização do estado interno da aplicação
if "agenda_compromissos" not in st.session_state:
    st.session_state.agenda_compromissos = pd.DataFrame(columns=["Data/Hora", "Compromisso", "Prioridade"])

# 1. BARRA LATERAL - CONFIGURAÇÃO DA USEONEAI
st.sidebar.title("🏢 Painel de Controle")
st.sidebar.subheader("Conexão UseOneAI")

api_key = st.sidebar.text_input("Sua UseOneAI API Key:", type="password")
endpoint_url = st.sidebar.text_input("Base URL da UseOneAI:", value="https://useoneai.app")
modelo_ia = st.sidebar.text_input("ID do Modelo:", value="chatgpt-5.6-terra")

st.sidebar.write("---")
st.sidebar.info("**Agente Ativo:** Helena - Secretária Executiva\n\nResponsável pela organização da sua agenda de compromissos, triagem de horários e lembretes estruturados.")

# 2. TELA CENTRAL - CENÁRIO INTERATIVO 3D + CAPTURA DE VOZ CONTÍNUA
st.title("🖥️ Helena — Sua Secretária Executiva Virtual")

html_voice_and_3d = f"""
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <style>
        body {{ margin: 0; overflow: hidden; background-color: #111; font-family: sans-serif; }}
        canvas {{ width: 100%; height: 260px; display: block; }}
        #status {{ position: absolute; top: 10px; left: 10px; color: #aa00ff; font-size: 12px; background: rgba(0,0,0,0.6); padding: 5px 10px; border-radius: 4px; font-weight: bold; }}
    </style>
    <script src="https://cloudflare.com"></script>
</head>
<body>
    <div id="status">🎙️ Helena está ouvindo... (Diga "Helena..." para agendar)</div>
    <script>
        const scene = new THREE.Scene(); scene.background = new THREE.Color(0x0a0a0a);
        const camera = new THREE.PerspectiveCamera(45, window.innerWidth / 260, 0.1, 1000);
        camera.position.set(0, 8, 16); camera.lookAt(0, 0, 0);
        const renderer = new THREE.WebGLRenderer({{ antialias: true }});
        renderer.setSize(window.innerWidth, 260); document.body.appendChild(renderer.domElement);
        scene.add(new THREE.AmbientLight(0xffffff, 0.8));
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
        // Apenas a Helena (Roxa) ativa no cenário
        const helena = criarRobo(0xaa00ff, 0, 0);

        function animar() {{
            requestAnimationFrame(animate = () => {{
                requestAnimationFrame(animate);
                helena.userData.mudar++;
                if(helena.userData.mudar > 150) {{ helena.userData.velX = (Math.random()-0.5)*0.03; helena.userData.velZ = (Math.random()-0.5)*0.03; helena.userData.mudar = 0; }}
                helena.position.x += helena.userData.velX; helena.position.z += helena.userData.velZ;
                if(helena.position.x > 13 || helena.position.x < -13) helena.userData.velX *= -1;
                if(helena.position.z > 8 || helena.position.z < -8) helena.userData.velZ *= -1;
                if(helena.userData.pulando) {{ helena.userData.tempoPulo += 0.2; helena.position.y = Math.abs(Math.sin(helena.userData.tempoPulo)) * 1.5; if(helena.userData.tempoPulo > Math.PI) {{ helena.userData.pulando = false; helena.position.y = 0; }} }}
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
                if (textoMinusculo.startsWith("helena")) {{ 
                    helena.userData.pulando = true; helena.userData.tempoPulo = 0;
                    window.parent.postMessage({{type: 'streamlit:setComponentValue', value: resultado}}, '*'); 
                }}
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

# --- FUNÇÃO DE PROCESSAMENTO EXCLUSIVA ---
def processar_helena(resposta_ia):
    try:
        texto_limpo = resposta_ia.strip().replace("```json", "").replace("```", "")
        dados_agenda = json.loads(texto_limpo)
        novos_eventos = pd.DataFrame(dados_agenda["Compromissos"])
        st.session_state.agenda_compromissos = pd.concat([st.session_state.agenda_compromissos, novos_eventos], ignore_index=True)
        st.success("📅 Helena agendou o compromisso!")
    except:
        st.info(f"💁‍♀️ **Helena:** {resposta_ia}")

# Caixa de Entrada por Texto (ou comando de voz capturado)
comando_final = st.text_input("Fale ou digite uma ordem para a Helena:")

if comando_final:
    st.write("---")
    st.subheader("💬 Resposta de Helena")
    prompt = "Você é a Helena, minha secretária executiva privada. O usuário vai ditar compromissos ou horários. Você deve processar o texto e retornar obrigatoriamente um objeto JSON puro no formato: {\"Compromissos\": [{\"DataHora\": \"DD/MM AAAA - HH:MM\", \"Compromisso\": \"Descrição\", \"Prioridade\": \"Alta/Média/Baixa\"}]}"
    resposta = chamar_modelo_useoneai(prompt, comando_final)
    processar_helena(resposta)

# RENDERIZAÇÃO DA AGENDA (HELENA)
if len(st.session_state.agenda_compromissos) > 0:
    st.write("---")
    st.subheader("📅 Sua Agenda de Compromissos Atualizada")
    st.dataframe(st.session_state.agenda_compromissos, use_container_width=True)
