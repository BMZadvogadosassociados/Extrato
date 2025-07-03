document.addEventListener('DOMContentLoaded', function() {
    // Mostrar o nome do arquivo selecionado
    const fileInput = document.getElementById('fileInput');
    const fileNameDisplay = document.getElementById('fileName');
    const uploadForm = document.getElementById('uploadForm');
    const processingSection = document.getElementById('processingSection');

    fileInput.addEventListener('change', function() {
        if (this.files.length > 0) {
            fileNameDisplay.textContent = this.files[0].name;
            fileNameDisplay.style.color = '#2980b9';
        } else {
            fileNameDisplay.textContent = 'Nenhum arquivo selecionado';
            fileNameDisplay.style.color = '#666';
        }
    });

    // Exibir indicador de carregamento ao enviar o formulário
    uploadForm.addEventListener('submit', function(e) {
        // Verificar se um arquivo foi selecionado
        if (fileInput.files.length === 0) {
            e.preventDefault();
            showToast('Por favor, selecione um arquivo PDF');
            return;
        }

        // Verificar se o arquivo é PDF
        const fileName = fileInput.files[0].name;
        if (!fileName.toLowerCase().endsWith('.pdf')) {
            e.preventDefault();
            showToast('Por favor, selecione um arquivo no formato PDF');
            return;
        }

        // Mostrar animação de carregamento
        processingSection.style.display = 'block';
        
        // Rolar para o indicador de processamento
        setTimeout(() => {
            processingSection.scrollIntoView({ behavior: 'smooth' });
        }, 100);
    });

    function confirmar(arquivo) {
        fetch("/confirmar", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                arquivo: arquivo,
                acao: "confirmar"
            })
        }).then(res => res.json())
          .then(data => {
              console.log("Resposta do servidor:", data);
              alert("✅ Confirmado: " + data.arquivo);
          });
    }

    function corrigir(arquivo) {
        fetch("/confirmar", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                arquivo: arquivo,
                acao: "corrigir"
            })
        }).then(res => res.json())
          .then(data => {
              console.log("Resposta do servidor:", data);
              alert("❌ Corrigir: " + data.arquivo);
          });
    }

    // Função para mostrar mensagens de toast
    function showToast(message) {
        // Criar elemento para o toast
        const toast = document.createElement('div');
        toast.className = 'toast';
        toast.textContent = message;
        
        // Estilizar o toast
        toast.style.position = 'fixed';
        toast.style.bottom = '20px';
        toast.style.left = '50%';
        toast.style.transform = 'translateX(-50%)';
        toast.style.backgroundColor = '#e74c3c';
        toast.style.color = 'white';
        toast.style.padding = '12px 20px';
        toast.style.borderRadius = '5px';
        toast.style.boxShadow = '0 2px 10px rgba(0,0,0,0.2)';
        toast.style.zIndex = '1000';
        
        // Adicionar ao corpo do documento
        document.body.appendChild(toast);
        
        // Animar entrada
        toast.style.opacity = '0';
        toast.style.transition = 'opacity 0.3s ease-in-out';
        
        setTimeout(() => {
            toast.style.opacity = '1';
        }, 10);
        
        // Remover após alguns segundos
        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => {
                document.body.removeChild(toast);
            }, 300);
        }, 3000);
    }

    // Adicionar efeitos de hover extras para melhorar a experiência do usuário
    const hoverElements = document.querySelectorAll('.upload-card, .intro');
    
    hoverElements.forEach(element => {
        element.addEventListener('mouseenter', function() {
            this.style.borderLeft = '5px solid #3498db';
        });
        
        element.addEventListener('mouseleave', function() {
            this.style.borderLeft = 'none';
        });
    });
});
