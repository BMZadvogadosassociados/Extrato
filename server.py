from flask import Flask, request, send_file, render_template, url_for, redirect 
import requests
from pypdf import PdfReader, PdfWriter
import re, os, io
from zipfile import ZipFile
import csv
import base64

WEBHOOK_URL = "https://hook.us1.make.com/d7km249aggme5icqoq8t8a5urtj9nie8"

# Carrega os IDs do CSV na inicialização
discord_ids = {}

with open('Banco_de_Dados_de_IDs_do_Discord.csv', newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        nome_norm = row['Nome'].strip().lower().replace(" ", "_")
        discord_ids[nome_norm] = row['ID Discord']

app = Flask(__name__)

def extrair_nome_funcionario(texto):
    padrao = r'Nome do funcionário C\.C:\s*\d+\s+([A-Z\s]+)\s+CBO'
    match = re.search(padrao, texto)
    if match:
        return match.group(1).strip().title()
    return None

def separar_pdf_em_holerites(pdf_stream):
    reader = PdfReader(pdf_stream)
    funcionarios_paginas = {}

    for i, page in enumerate(reader.pages):
        texto = page.extract_text()
        nome = extrair_nome_funcionario(texto)
        if nome:
            if nome not in funcionarios_paginas:
                funcionarios_paginas[nome] = []
            funcionarios_paginas[nome].append(i)

    arquivos = {}

    for nome, paginas in funcionarios_paginas.items():
        writer = PdfWriter()
        for pagina in paginas:
            writer.add_page(reader.pages[pagina])
        nome_arquivo = re.sub(r'[^\w\s-]', '', nome).replace(" ", "_") + ".pdf"
        buffer = io.BytesIO()
        writer.write(buffer)
        buffer.seek(0)
        arquivos[nome_arquivo] = buffer

    return arquivos

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'arquivo' not in request.files:
        return render_template('index.html', error='Nenhum arquivo foi enviado')
    
    file = request.files['arquivo']
    
    if file.filename == '':
        return render_template('index.html', error='Nenhum arquivo foi selecionado')
    
    if not file.filename.lower().endswith('.pdf'):
        return render_template('index.html', error='Por favor, envie um arquivo PDF')

    arquivos = separar_pdf_em_holerites(file.stream)

    pasta_saida = os.path.join(app.static_folder, 'holerites')
    os.makedirs(pasta_saida, exist_ok=True)

    # Limpa a pasta antes
    for f in os.listdir(pasta_saida):
        os.remove(os.path.join(pasta_saida, f))

    for nome, conteudo in arquivos.items():
        with open(os.path.join(pasta_saida, nome), 'wb') as f:
            f.write(conteudo.getvalue())

    return redirect(url_for('revisao'))

@app.route('/revisao', methods=['GET'])
def revisao():
    pasta_saida = os.path.join(app.static_folder, 'holerites')
    arquivos = os.listdir(pasta_saida)
    arquivos_pdf = sorted([f for f in arquivos if f.endswith('.pdf')])
    return render_template('revisao.html', arquivos=arquivos_pdf)

decisoes = {}  # Armazena as confirmações em memória

@app.route('/confirmar', methods=['POST'])
def confirmar_pdf():
    data = request.json
    nome_arquivo = data.get('arquivo')
    acao = data.get('acao')

    if nome_arquivo and acao in ['confirmar', 'corrigir']:
        nome_base = nome_arquivo.replace('.pdf', '').lower()
        discord_id = discord_ids.get(nome_base)
        nome_legivel = nome_base.replace('_', ' ').title()

        caminho_pdf = os.path.join(app.static_folder, 'holerites', nome_arquivo)
        try:
            with open(caminho_pdf, "rb") as f:
                pdf_base64 = base64.b64encode(f.read()).decode("utf-8")
        except Exception as e:
            print(f"Erro ao ler o PDF: {e}")
            return jsonify({'status': 'erro', 'detalhe': 'Falha ao ler o PDF'}), 500

        payload = {
            "arquivo": nome_arquivo,
            "acao": acao,
            "nome": nome_legivel,
            "discord_id": discord_id,
            "pdf_base64": pdf_base64
        }

        try:
            print("Enviando webhook:", payload)
            response = requests.post(WEBHOOK_URL, json=payload)
            return jsonify({'status': 'ok', 'enviado': payload})
        except Exception as e:
            print("Erro ao enviar webhook:", e)
            return jsonify({'status': 'erro', 'detalhe': str(e)}), 500

    return jsonify({'status': 'erro'}), 400


if __name__ == "__main__":
    os.makedirs(os.path.join(app.static_folder, 'css'), exist_ok=True)
    os.makedirs(os.path.join(app.static_folder, 'js'), exist_ok=True)
    os.makedirs(os.path.join(app.static_folder, 'holerites'), exist_ok=True)
    os.makedirs(os.path.join(app.root_path, 'templates'), exist_ok=True)

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
