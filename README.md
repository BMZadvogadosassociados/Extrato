# Extrato

✅ Resumo Técnico – Projeto: Envio de Holerites por Discord via PDF
👨‍💻 Autor: Eduardo Sochodolak – BMZ Advogados Associados
🗓️ Concluído em: Maio de 2025
📌 Objetivo
Receber um PDF contendo vários holerites, separá-los por funcionário, permitir revisão manual e, após confirmação, enviar automaticamente o PDF de cada funcionário via DM no Discord, utilizando um bot autenticado.

🧱 Estrutura do sistema
🌐 Site Flask (Render)
Upload de PDF principal contendo vários holerites.

Processamento com PyPDF → separa por nome usando regex.

Interface de revisão com botões "Confirmar" ou "Corrigir".

Ao confirmar, envia um webhook com:

nome

arquivo

discord_id

url_pdf (link público para o PDF)

⚠️ Arquivos ficam acessíveis apenas temporariamente via https://extrato-bclc.onrender.com/static/holerites/...

🧰 Make (Integromat)
Webhook (entrada) → recebe JSON com url_pdf, nome, discord_id

HTTP > Get a file → baixa o PDF usando o url_pdf

HTTP > Criar canal de DM

POST para https://discord.com/api/v10/users/@me/channels

Autorizado com Bot <TOKEN_DO_BOT>

Envia { "recipient_id": "{{discord_id}}" }

HTTP > Enviar mensagem e anexo

POST para https://discord.com/api/v10/channels/{{id}}/messages

Body: multipart/form-data

payload_json com mensagem

files[0] com PDF (usando parseBase64() se for via base64, ou Get a file > data direto)

🤖 Bot Discord
Criado no Discord Developer Portal

Com permissões:

Send Messages

Attach Files

Adicionado ao servidor via Guild Install

Token protegido via Secrets no Make e/ou variável no Render

🔒 Considerações de segurança
Nenhum token é exposto em código-fonte.

Webhook do Make recebe dados diretamente do site com validação de nome e ID.

Uploads são temporários no Render (pode ser evoluído para S3, Drive ou Firebase).

✅ Resultado
Fluxo 100% automatizado de envio de holerites personalizados via DM no Discord.

Visual limpo e integração estável entre Flask, Make e Discord.

