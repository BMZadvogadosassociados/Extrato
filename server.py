from flask import Flask, request, send_file, render_template, url_for
from pypdf import PdfReader, PdfWriter
import re, os, io
from zipfile import ZipFile
import os

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

    zip_buffer = io.BytesIO()
    with ZipFile(zip_buffer, 'w') as zip_file:
        for nome, conteudo in arquivos.items():
            zip_file.writestr(nome, conteudo.getvalue())

    zip_buffer.seek(0)
    return send_file(zip_buffer, mimetype='application/zip', download_name='holerites.zip', as_attachment=True)


if __name__ == "__main__":
    # Certifique-se de que as pastas necessárias existam
    os.makedirs(os.path.join(app.root_path, 'static', 'css'), exist_ok=True)
    os.makedirs(os.path.join(app.root_path, 'static', 'js'), exist_ok=True)
    os.makedirs(os.path.join(app.root_path, 'templates'), exist_ok=True)
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)