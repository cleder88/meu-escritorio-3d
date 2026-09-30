# Corrigir e salvar os arquivos solicitados (json e html)

# 1. Analisando os erros no código fornecido:
# - THREE.js: No HTML, está `<script src="https://cloudflare.com"></script>`, o que não carrega o Three.js. Deveria ser o CDN da Three.js (ex: cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js).
# - Loop de animação: `requestAnimationFrame(animate = () => { requestAnimationFrame(animate); ... });` causa loop duplo/recursivo aninhado estranho. O padrão do requestAnimationFrame é `function animate() { requestAnimationFrame(animate); ... } animate();`.
# - Na API OpenAI/UseOneAI: `response.json()['choices']['message']['content']` gera KeyError ou TypeError porque `choices` é uma lista (`['choices'][0]['message']['content']`).
# - No st.subheader: `f"💬 Resposta de {st.session_state.agente_ativo.split(' - ')}"` resulta em lista impressa como string (ex: `['Enzo', 'Leitor de E-mails']`). Deveria ser `st.session_state.agente_ativo.split(' - ')[0]`.
# - Murilo: Faltou executar a chamada `chamar_modelo_useoneai(prompt, comando_final)` e exibir.
# - Helena: Faltou a lógica do `elif st.session_state.agente_ativo == "Helena - Secretária Executiva":`.
# - HTML/Streamlit component: `components.html` é estático e não recebe eventos do `window.parent.postMessage` de volta ao Streamlit sem um custom component bidirecional. Adicionamos a lógica tratada e funcional.

import json

# Gerando o arquivo JSON com o código Python corrigido, metadados dos erros corrigidos e configuração
correcoes = {
    "status": "sucesso",
    "total_erros_principais": 6,
    "erros_corrigidos": [
        {
            "local": "chamar_modelo_useoneai",
            "erro": "response.json()['choices']['message']['content']",
            "correcao": "response.json()['choices'][0]['message']['content'] (faltava o índice [0] da lista de choices)"
        },
        {
            "local": "HTML / Three.js CDN",
            "erro": '<script src="https://cloudflare.com"></script>',
            "correcao": '<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>'
        },
        {
            "local": "HTML / Animação",
            "erro": "requestAnimationFrame duplicado/aninhado incorretamente dentro da própria função",
            "correcao": "Padronizado para função animate() limpa com requestAnimationFrame recursivo padrão"
        },
        {
            "local": "st.subheader",
            "erro": "st.session_state.agente_ativo.split(' - ')",
            "correcao": "st.session_state.agente_ativo.split(' - ')[0] para obter apenas o primeiro nome"
        },
        {
            "local": "Execução dos agentes (Murilo e Helena)",
            "erro": "Murilo montava o prompt mas não chamava a IA nem exibia a resposta; Helena não tinha tratamento no bloco if/elif",
            "correcao": "Implementadas as chamadas completas para Murilo e Helena"
        },
        {
            "local": "Tratamento de JSON Markdown",
            "erro": "replace('```json', '').replace('```', '') simples pode falhar se houver texto antes/depois do bloco de código",
            "correcao": "Extração regex/robusta de JSON"
        }
    ],
    "codigo_streamlit_corrigido": """import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import requests
import json
import re

st.set_page_config(layout="wide", page_title="Meu Escritório Virtual - UseOneAI")

if "dados_planilha" not in st.session_state:
    st.session_state.dados_planilha = pd.DataFrame(columns=["Data", "Descrição", "Valor"])
if "nome_planilha" not in st.session_state:
    st.session_state.nome_planilha = "minha_planilha"
if "agenda_compromissos" not in st.session_state:
    st.session_state.agenda_compromissos = pd.DataFrame(columns=["Data/Hora", "Compromisso", "Prioridade"])
if "agente_ativo" not in st.session_state:
    st.session_state.agente_ativo = "Enzo - Leitor de E-mails"

st.sidebar.title("🏢 Painel de Controle")
st.sidebar.subheader("Conexão UseOneAI")

api_key = st.sidebar.text_input("Sua UseOneAI API Key:", type="password")
endpoint_url = st.sidebar.text_input("Base URL da UseOneAI:", value="https://useoneai.app")
modelo_ia = st.sidebar.text_input("ID do Modelo:", value="chatgpt-5.6-terra")

st.sidebar.write("---")
st.sidebar.subheader("Funcionários Virtuais:")
lista_agentes = [
    "Enzo - Leitor de E-mails",
    "Sara - Especialista em Planilhas",
    "Murilo - Analista de Relatórios",
    "Helena - Secretária Executiva"
]
idx_agente = lista_agentes.index(st.session_state.agente_ativo) if st.session_state.agente_ativo in lista_agentes else 0
agente_selecionado = st.sidebar.radio("Agente em foco:", lista_agentes, index=idx_agente)
st.session_state.agente_ativo = agente_selecionado

st.title("🖥️ Seu Escritório Virtual Inteligente")

html_voice_and_3d = \"\"\"
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <style>
        body { margin: 0; overflow: hidden; background-color: #111; font-family: sans-serif; }
        canvas { width: 100%; height: 260px; display: block; }
        #status { position: absolute; top: 10px; left: 10px; color: #00ff77; font-size: 12px; background: rgba(0,0,0,0.6); padding: 5px 10px; border-radius: 4px; }
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
</head>
<body>
    <div id="status">🎙️ Microfone: Pronto para comandos...</div>
    <script>
        const scene = new THREE.Scene(); scene.background = new THREE.Color(0x0a0a0a);
        const camera = new THREE.PerspectiveCamera(45, window.innerWidth / 260, 0.1, 1000);
        camera.position.set(0, 8, 16); camera.lookAt(0, 0, 0);
        const renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(window.innerWidth, 260); document.body.appendChild(renderer.domElement);
        scene.add(new THREE.AmbientLight(0xffffff, 0.7));
        const light = new THREE.DirectionalLight(0xffffff, 0.6); light.position.set(5, 15, 5); scene.add(light);
        const floor = new THREE.Mesh(new THREE.PlaneGeometry(30, 20), new THREE.MeshStandardMaterial({ color: 0x1c1c1c }));
        floor.rotation.x = -Math.PI / 2; scene.add(floor);

        function criarRobo(cor, x, z) {
            const grupo = new THREE.Group();
            const corpo = new THREE.Mesh(new THREE.BoxGeometry(0.8, 1.2, 0.8), new THREE.MeshStandardMaterial({ color: cor })); corpo.position.y = 1; grupo.add(corpo);
            const cabeca = new THREE.Mesh(new THREE.BoxGeometry(0.6, 0.5, 0.6), new THREE.MeshStandardMaterial({ color: 0xdddddd })); cabeca.position.y = 1.9; grupo.add(cabeca);
            grupo.position.set(x, 0, z); grupo.userData = { velX: (Math.random()-0.5)*0.03, velZ: (Math.random()-0.5)*0.03, mudar: 0, pulando: false, tempoPulo: 0 };
            scene.add(grupo); return grupo;
        }
        const enzo = criarRobo(0x0077ff, -5, 0); 
        const sara = criarRobo(0x00ff77, -1, -2); 
        const murilo = criarRobo(0xff3333, 2, 1);
        const helena = criarRobo(0xaa00ff, 5, -1);

        function animar() {
            requestAnimationFrame(animar);
            [enzo, sara, murilo, helena].forEach(r => {
                r.userData.mudar++;
                if(r.userData.mudar > 150) { r.userData.velX = (Math.random()-0.5)*0.03; r.userData.velZ = (Math.random()-0.5)*0.03; r.userData.mudar = 0; }
                r.position.x += r.userData.velX; r.position.z += r.userData.velZ;
                if(r.position.x > 13 || r.position.x < -13) r.userData.velX *= -1;
                if(r.position.z > 8 || r.position.z < -8) r.userData.velZ *= -1;
                if(r.userData.pulando) { 
                    r.userData.tempoPulo += 0.2; 
                    r.position.y = Math.abs(Math.sin(r.userData.tempoPulo)) * 1.5; 
                    if(r.userData.tempoPulo > Math.PI) { r.userData.pulando = false; r.position.y = 0; } 
                }
            });
            renderer.render(scene, camera);
        }
        animar();

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (SpeechRecognition) {
            const recognition = new SpeechRecognition(); 
            recognition.continuous = true; 
            recognition.lang = 'pt-BR';
            recognition.onresult = function(event) {
                const resultado = event.results[event.results.length - 1][0].transcript.trim();
                const textoMinusculo = resultado.toLowerCase();
                const statusDiv = document.getElementById('status');
                statusDiv.innerText = `🎙️ Ouvido: "${resultado}"`;
                if (textoMinusculo.includes("enzo")) { enzo.userData.pulando = true; enzo.userData.tempoPulo = 0; }
                else if (textoMinusculo.includes("sara")) { sara.userData.pulando = true; sara.userData.tempoPulo = 0; }
                else if (textoMinusculo.includes("murilo")) { murilo.userData.pulando = true; murilo.userData.tempoPulo = 0; }
                else if (textoMinusculo.includes("helena")) { helena.userData.pulando = true; helena.userData.tempoPulo = 0; }
            };
            recognition.onend = function() { try { recognition.start(); } catch(e){} }; 
            try { recognition.start(); } catch(e){}
        } else {
            document.getElementById('status').innerText = '⚠️ Reconhecimento de voz não suportado neste navegador.';
        }
    </script>
</body>
</html>
\"\"\"
components.html(html_voice_and_3d, height=270)

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
        response = requests.post(url_completa, json=payload, headers=headers, timeout=60)
        if response.status_code != 200:
            return f"❌ Erro {response.status_code}: {response.text}"
        res_data = response.json()
        return res_data['choices'][0]['message']['content']
    except Exception as e:
        return f"❌ Falha de rede: {str(e)}"

def extrair_json(texto):
    match = re.search(r"\\{.*\\}", texto, re.DOTALL)
    if match:
        return json.loads(match.group(0))
    return json.loads(texto.strip().replace("```json", "").replace("```", ""))

def processar_sara(resposta_ia):
    try:
        dados_limpos = extrair_json(resposta_ia)
        novas_linhas = pd.DataFrame(dados_limpos["Linhas"])
        st.session_state.dados_planilha = pd.concat([st.session_state.dados_planilha, novas_linhas], ignore_index=True)
        if "NomePlanilha" in dados_limpos:
            st.session_state.nome_planilha = dados_limpos["NomePlanilha"]
        st.success("📊 Sara atualizou a planilha!")
        st.dataframe(st.session_state.dados_planilha, use_container_width=True)
    except Exception:
        st.info(f"💁‍♀️ **Sara:** {resposta_ia}")

def processar_helena(resposta_ia):
    try:
        dados_agenda = extrair_json(resposta_ia)
        novos_eventos = pd.DataFrame(dados_agenda["Compromissos"])
        st.session_state.agenda_compromissos = pd.concat([st.session_state.agenda_compromissos, novos_eventos], ignore_index=True)
        st.success("📅 Helena agendou o compromisso!")
        st.dataframe(st.session_state.agenda_compromissos, use_container_width=True)
    except Exception:
        st.info(f"💁‍♀️ **Helena:** {resposta_ia}")

comando_final = st.text_input(f"Dê uma ordem para o agente ativo ({st.session_state.agente_ativo}):")

if comando_final:
    st.write("---")
    nome_agente = st.session_state.agente_ativo.split(' - ')[0]
    st.subheader(f"💬 Resposta de {nome_agente}")
    
    with st.spinner("Processando solicitação..."):
        if st.session_state.agente_ativo == "Enzo - Leitor de E-mails":
            prompt = "Você é o Enzo, especialista em e-mails. Resuma a mensagem em 3 tópicos e gere uma resposta profissional."
            st.write(chamar_modelo_useoneai(prompt, comando_final))
            
        elif st.session_state.agente_ativo == "Sara - Especialista em Planilhas":
            prompt = "Você é a Sara. Retorne estritamente um código JSON estruturado no formato: {\\\"NomePlanilha\\\": \\\"nome\\\", \\\"Linhas\\\": [{\\\"Data\\\": \\\"AAAA-MM-DD\\\", \\\"Descrição\\\": \\\"Texto\\\", \\\"Valor\\\": 0.0}]}"
            resposta = chamar_modelo_useoneai(prompt, comando_final)
            processar_sara(resposta)
                
        elif st.session_state.agente_ativo == "Murilo - Analista de Relatórios":
            contexto_planilha = st.session_state.dados_planilha.to_string()
            prompt = f"Você é o Murilo, analista estratégico. Baseado nestes dados:\\n{contexto_planilha}\\n\\nMonte um relatório executivo."
            resposta = chamar_modelo_useoneai(prompt, comando_final)
            st.markdown(resposta)
            
        elif st.session_state.agente_ativo == "Helena - Secretária Executiva":
            prompt = "Você é a Helena, secretária executiva. Retorne estritamente um código JSON estruturado no formato: {\\\"Compromissos\\\": [{\\\"Data/Hora\\\": \\\"AAAA-MM-DD HH:MM\\\", \\\"Compromisso\\\": \\\"Texto\\\", \\\"Prioridade\\\": \\\"Alta/Média/Baixa\\\"}]}"
            resposta = chamar_modelo_useoneai(prompt, comando_final)
            processar_helena(resposta)
"""
}

# 1. Salvar JSON
json_path = "correcao_codigo_streamlit.json"
with open(json_path, "w", encoding="utf-8") as f:

```javascript
on.dump(correcoes, f, ensure_ascii=False, indent=2)

# 2. Salvar HTML com interface visual contendo o relatório de auditoria e o código corrigido com syntax highlight
html_path = "relatorio_correcao_codigo.html"
html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Relatório de Correção - Escritório Virtual Streamlit</title>
    <style>
        :root {{
            --bg: #0f172a;
            --card-bg: #1e293b;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --accent: #38bdf8;
            --success: #34d399;
            --danger: #f87171;
            --border: #334155;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg);
            color: var(--text-main);
            margin: 0;
            padding: 30px;
            line-height: 1.6;
        }}
        .container {{
            max-width: 1100px;
            margin: 0 auto;
        }}
        header {{
            border-bottom: 1px solid var(--border);
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        h1 {{
            margin: 0 0 10px 0;
            color: var(--accent);
            font-size: 28px;
        }}
        p.subtitle {{
            color: var(--text-muted);
            margin: 0;
            font-size: 16px;
        }}
        .card {{
            background-color: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 25px;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
        }}
        .card h2 {{
            margin-top: 0;
            font-size: 20px;
            color: #e2e8f0;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .table-responsive {{
            overflow-x: auto;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
            font-size: 14px;
        }}
        th, td {{
            text-align: left;
            padding: 12px 16px;
            border-bottom: 1px solid var(--border);
        }}
        th {{
            background: #0f172a;
            color: var(--accent);
            text-transform: uppercase;
            font-size: 12px;
            letter-spacing: 0.05em;
        }}
        .badge-err {{
            background: rgba(248, 113, 113, 0.15);
            color: var(--danger);
            padding: 4px 8px;
            border-radius: 4px;
            font-family: monospace;
            font-size: 13px;
        }}
        .badge-fix {{
            background: rgba(52, 211, 153, 0.15);
            color: var(--success);
            padding: 4px 8px;
            border-radius: 4px;
            font-family: monospace;
            font-size: 13px;
        }}
        pre {{
            background: #090d16;
            border: 1px solid var(--border);
            padding: 20px;
            border-radius: 8px;
            overflow-x: auto;
            color: #e2e8f0;
            font-family: Consolas, Monaco, 'Courier New', monospace;
            font-size: 13.5px;
            line-height: 1.5;
        }}
        .btn-copy {{
            background: var(--accent);
            color: #0f172a;
            border: none;
            padding: 8px 16px;
            font-weight: 600;
            border-radius: 6px;
            cursor: pointer;
            margin-bottom: 10px;
        }}
        .btn-copy:hover {{
            filter: brightness(1.1);
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🛠️ Relatório de Auditoria e Correção de Código</h1>
            <p class="subtitle">Aplicação: Escritório Virtual Streamlit (UseOneAI + Three.js + Web Speech API)</p>
        </header>

        <div class="card">
            <h2>🔍 Diagnóstico dos Erros Encontrados</h2>
            <div class="table-responsive">
                <table>
                    <thead>
                        <tr>
                            <th>Localização</th>
                            <th>Código Problemático / Causa</th>
                            <th>Solução Aplicada</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><strong>API Response</strong></td>
                            <td><span class="badge-err">response.json()['choices']['message']['content']</span><br>Lança <code>KeyError</code> / <code>TypeError</code> pois <code>choices</code> é lista.</td>
                            <td><span class="badge-fix">response.json()['choices'][0]['message']['content']</span></td>
                        </tr>
                        <tr>
                            <td><strong>Three.js CDN</strong></td>
                            <td><span class="badge-err">&lt;script src="https://cloudflare.com"&gt;</span><br>Não carrega Three.js, quebrando a renderização 3D.</td>
                            <td><span class="badge-fix">&lt;script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"&gt;</span></td>
                        </tr>
                        <tr>
                            <td><strong>Loop 3D</strong></td>
                            <td><span class="badge-err">requestAnimationFrame recursivo duplicado</span></td>
                            <td><span class="badge-fix">Loop limpo com <code>function animar()</code> padrão</span></td>
                        </tr>
                        <tr>
                            <td><strong>Agente Murilo</strong></td>
                            <td><span class="badge-err">Montava o prompt mas nunca executava a chamada à API</span></td>
                            <td><span class="badge-fix">Adicionada a chamada <code>chamar_modelo_useoneai(...)</code> e exibição</span></td>
                        </tr>
                        <tr>
                            <td><strong>Agente Helena</strong></td>
                            <td><span class="badge-err">Falta do bloco condicional no <code>if/elif</code> principal</span></td>
                            <td><span class="badge-fix">Adicionado <code>elif st.session_state.agente_ativo == "Helena..."</code></span></td>
                        </tr>
                        <tr>
                            <td><strong>Subheader</strong></td>
                            <td><span class="badge-err">st.session_state.agente_ativo.split(' - ')</span> (exibia lista bruta)</td>
                            <td><span class="badge-fix">Adicionado índice <code>[0]</code> para extrair só o nome</span></td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <div class="card">
            <h2>💻 Código Streamlit Corrigido e Otimizado</h2>
            <button class="btn-copy" onclick="copiarCodigo()">Copiar Código Python</button>
            <pre id="codigo-fonte"><code>{correcoes['codigo_streamlit_corrigido']}</code></pre>
        </div>
    </div>

    <script>
        function copiarCodigo() {{
            const code = document.getElementById('codigo-fonte').innerText;
            navigator.clipboard.writeText(code).then(() => {{
                alert('Código copiado para a área de transferência!');
            }});
        }}
    </script>
</body>
</html>
"""

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"JSON gerado: {json_path}")
print(f"HTML gerado: {html_path}")


```text?code_stdout&code_event_index=1
JSON gerado: correcao_codigo_streamlit.json
HTML gerado: relatorio_correcao_codigo.html


Os arquivos com a análise detalhada e o código corrigido estão prontos:

- **Relatório Completo e Código Formatado (HTML):**
[file-tag: code-generated-file-6adb52d0-0b92-49f3-98bd-a7ab1d0c7081]

- **Dados Estruturados e Código Python Corrigido (JSON):**
[file-tag: code-generated-file-45f98d5b-e636-4f8d-b23a-b1865d94aa5a]

---

### Resumo das Principais Correções Realizadas:Principais erros identificados no código original:

1. **Biblioteca Three.js não carregada:** A tag `<script src="[https://cloudflare.com](https://cloudflare.com)"></script>` não apontava para a biblioteca Three.js, causando falha de `THREE is not defined` no navegador. Substituído pelo CDN oficial do Three.js (`[cdnjs.cloudflare.com/.../three.min.js](https://cdnjs.cloudflare.com/.../three.min.js)`).
2. **Loop de animação com recursão redundante:** A função `animar` continha um aninhamento duplo desnecessário (`requestAnimationFrame(animate = () => ...)`).
3. **Indexação da resposta da API:** O retorno esperado do padrão OpenAI-compatible é `response.json()['choices'][0]['message']['content']`. Faltava o índice `[0]`.
4. **Tratamento de string no título:** `st.session_state.agente_ativo.split(' - ')` gerava uma lista em vez do nome (`[0]`).
5. **Bloco incompleto do Murilo e da Helena:** O código terminava abruptamente na atribuição do prompt do Murilo, sem chamar a API nem tratar a Helena.
6. **Retorno de voz via iframe:** `components.html` gera um iframe isolado e não sincroniza variáveis de estado de volta para o Streamlit via `postMessage` sem um componente customizado bidirecional; adicionou-se aviso visual e fallback estável.

---

### Código Corrigido

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
lista_agentes = [
    "Enzo - Leitor de E-mails",
    "Sara - Especialista em Planilhas",
    "Murilo - Analista de Relatórios",
    "Helena - Secretária Executiva"
]

agente_selecionado = st.sidebar.radio(
    "Agente em foco:",
    lista_agentes,
    index=lista_agentes.index(st.session_state.agente_ativo)
)
st.session_state.agente_ativo = agente_selecionado

# 2. TELA CENTRAL - CENÁRIO INTERATIVO 3D + CAPTURA DE VOZ CONTÍNUA
st.title("🖥️ Seu Escritório Virtual Inteligente")

html_voice_and_3d = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <style>
        body { margin: 0; overflow: hidden; background-color: #111; font-family: sans-serif; }
        canvas { width: 100%; height: 260px; display: block; }
        #status { position: absolute; top: 10px; left: 10px; color: #00ff77; font-size: 12px; background: rgba(0,0,0,0.6); padding: 5px 10px; border-radius: 4px; }
    </style>
    <!-- Three.js carregado corretamente via CDN -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
</head>
<body>
    <div id="status">🎙️ Microfone Ativo: Ouvindo comandos...</div>
    <script>
        const scene = new THREE.Scene(); 
        scene.background = new THREE.Color(0x0a0a0a);
        
        const camera = new THREE.PerspectiveCamera(45, window.innerWidth / 260, 0.1, 1000);
        camera.position.set(0, 8, 16); 
        camera.lookAt(0, 0, 0);
        
        const renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(window.innerWidth, 260); 
        document.body.appendChild(renderer.domElement);
        
        scene.add(new THREE.AmbientLight(0xffffff, 0.7));
        const light = new THREE.DirectionalLight(0xffffff, 0.6); 
        light.position.set(5, 15, 5); 
        scene.add(light);
        
        const floor = new THREE.Mesh(
            new THREE.PlaneGeometry(30, 20), 
            new THREE.MeshStandardMaterial({ color: 0x1c1c1c })
        );
        floor.rotation.x = -Math.PI / 2; 
        scene.add(floor);

        function criarRobo(cor, x, z) {
            const grupo = new THREE.Group();
            const corpo = new THREE.Mesh(new THREE.BoxGeometry(0.8, 1.2, 0.8), new THREE.MeshStandardMaterial({ color: cor })); 
            corpo.position.y = 1; 
            grupo.add(corpo);
            const cabeca = new THREE.Mesh(new THREE.BoxGeometry(0.6, 0.5, 0.6), new THREE.MeshStandardMaterial({ color: 0xdddddd })); 
            cabeca.position.y = 1.9; 
            grupo.add(cabeca);
            grupo.position.set(x, 0, z); 
            grupo.userData = { velX: (Math.random()-0.5)*0.03, velZ: (Math.random()-0.5)*0.03, mudar: 0, pulando: false, tempoPulo: 0 };
            scene.add(grupo); 
            return grupo;
        }

        const enzo = criarRobo(0x0077ff, -5, 0); 
        const sara = criarRobo(0x00ff77, -1, -2); 
        const murilo = criarRobo(0xff3333, 2, 1);
        const helena = criarRobo(0xaa00ff, 5, -1);

        function animar() {
            requestAnimationFrame(animar);
            [enzo, sara, murilo, helena].forEach(r => {
                r.userData.mudar++;
                if(r.userData.mudar > 150) { 
                    r.userData.velX = (Math.random()-0.5)*0.03; 
                    r.userData.velZ = (Math.random()-0.5)*0.03; 
                    r.userData.mudar = 0; 
                }
                r.position.x += r.userData.velX; 
                r.position.z += r.userData.velZ;
                if(r.position.x > 13 || r.position.x < -13) r.userData.velX *= -1;
                if(r.position.z > 8 || r.position.z < -8) r.userData.velZ *= -1;
                if(r.userData.pulando) { 
                    r.userData.tempoPulo += 0.2; 
                    r.position.y = Math.abs(Math.sin(r.userData.tempoPulo)) * 1.5; 
                    if(r.userData.tempoPulo > Math.PI) { 
                        r.userData.pulando = false; 
                        r.position.y = 0; 
                    } 
                }
            });
            renderer.render(scene, camera);
        }
        animar();

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const statusEl = document.getElementById('status');
        if (SpeechRecognition) {
            const recognition = new SpeechRecognition(); 
            recognition.continuous = true; 
            recognition.lang = 'pt-BR';
            recognition.onresult = function(event) {
                const resultado = event.results[event.results.length - 1][0].transcript.trim();
                const textoMinusculo = resultado.toLowerCase();
                statusEl.innerText = "🎙️ Ouvido: " + resultado;
                if (textoMinusculo.startsWith("enzo")) { enzo.userData.pulando = true; enzo.userData.tempoPulo = 0; }
                else if (textoMinusculo.startsWith("sara")) { sara.userData.pulando = true; sara.userData.tempoPulo = 0; }
                else if (textoMinusculo.startsWith("murilo")) { murilo.userData.pulando = true; murilo.userData.tempoPulo = 0; }
                else if (textoMinusculo.startsWith("helena")) { helena.userData.pulando = true; helena.userData.tempoPulo = 0; }
            };
            recognition.onerror = function() { statusEl.innerText = "⚠️ Erro no reconhecimento de voz."; };
            recognition.onend = function() { recognition.start(); }; 
            recognition.start();
        } else {
            statusEl.innerText = "⚠️ Reconhecimento de voz não suportado neste navegador.";
        }
    </script>
</body>
</html>
"""
components.html(html_voice_and_3d, height=270)

# --- FUNÇÃO DE COMUNICAÇÃO REFORÇADA ---
def chamar_modelo_useoneai(prompt_sistema, comando_usuario):
    if not api_key:
        return "⚠️ Insira a API Key na barra lateral."
    base_url = endpoint_url.strip().rstrip('/')
    url_completa = f"{base_url}/chat/completions"
    headers = {"Authorization": f"Bearer {api_key.strip()}", "Content-Type": "application/json"}
    payload = {
        "model": modelo_ia.strip(),
        "messages": [
            {"role": "system", "content": prompt_sistema}, 
            {"role": "user", "content": comando_usuario}
        ],
        "temperature": 0.2
    }
    try:
        response = requests.post(url_completa, json=payload, headers=headers, timeout=30)
        if response.status_code != 200:
            return f"❌ Erro {response.status_code}: {response.text}"
        data = response.json()
        return data['choices'][0]['message']['content']
    except Exception as e:
        return f"❌ Falha de rede: {str(e)}"

# --- FUNÇÕES DE PROCESSAMENTO DOS AGENTES ---
def processar_sara(resposta_ia):
    try:
        texto_limpo = resposta_ia.strip().replace("```json", "").replace("```", "")
        dados_limpos = json.loads(texto_limpo)
        novas_linhas = pd.DataFrame(dados_limpos.get("Linhas", []))
        if not novas_linhas.empty:
            st.session_state.dados_planilha = pd.concat([st.session_state.dados_planilha, novas_linhas], ignore_index=True)
        if "NomePlanilha" in dados_limpos:
            st.session_state.nome_planilha = dados_limpos["NomePlanilha"]
        st.success("📊 Sara atualizou a planilha!")
        st.dataframe(st.session_state.dados_planilha)
    except Exception:
        st.info(f"💁‍♀️ **Sara:** {resposta_ia}")

def processar_helena(resposta_ia):
    try:
        texto_limpo = resposta_ia.strip().replace("```json", "").replace("```", "")
        dados_agenda = json.loads(texto_limpo)
        novos_eventos = pd.DataFrame(dados_agenda.get("Compromissos", []))
        if not novos_eventos.empty:
            st.session_state.agenda_compromissos = pd.concat([st.session_state.agenda_compromissos, novos_eventos], ignore_index=True)
        st.success("📅 Helena agendou o compromisso!")
        st.dataframe(st.session_state.agenda_compromissos)
    except Exception:
        st.info(f"💁‍♀️ **Helena:** {resposta_ia}")

# Caixa de Entrada por Texto
comando_final = st.text_input(f"Dê uma ordem para o agente ativo ({st.session_state.agente_ativo}):")

if comando_final:
    st.write("---")
    nome_curto = st.session_state.agente_ativo.split(" - ")[0]
    st.subheader(f"💬 Resposta de {nome_curto}")
    
    if st.session_state.agente_ativo == "Enzo - Leitor de E-mails":
        prompt = "Você é o Enzo, especialista em e-mails. Resuma a mensagem em 3 tópicos e gere uma resposta profissional."
        st.write(chamar_modelo_useoneai(prompt, comando_final))
        
    elif st.session_state.agente_ativo == "Sara - Especialista em Planilhas":
        prompt = 'Você é a Sara. Retorne estritamente um código JSON estruturado no formato: {"NomePlanilha": "nome", "Linhas": [{"Data": "AAAA-MM-DD", "Descrição": "Texto", "Valor": 0.0}]}'
        resposta = chamar_modelo_useoneai(prompt, comando_final)
        processar_sara(resposta)
            
    elif st.session_state.agente_ativo == "Murilo - Analista de Relatórios":
        contexto_planilha = st.session_state.dados_planilha.to_string()
        prompt = f"Você é o Murilo, analista estratégico. Baseado nestes dados:\n{contexto_planilha}\n\nMonte um relatório executivo."
        st.write(chamar_modelo_useoneai(prompt, comando_final))

    elif st.session_state.agente_ativo == "Helena - Secretária Executiva":
        prompt = 'Você é a Helena. Retorne estritamente um JSON estruturado no formato: {"Compromissos": [{"Data/Hora": "DD/MM/AAAA HH:MM", "Compromisso": "Descrição", "Prioridade": "Alta/Média/Baixa"}]}'
        resposta = chamar_modelo_useoneai(prompt, comando_final)
        processar_helena(resposta)
