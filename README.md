# 🕵️‍♂️ Monitor Inteligente de Preços - Pichau

Este é um projeto desenvolvido com o objetivo de monitorar automaticamente os preços de componentes de hardware (focado inicialmente em placas-mãe) no site da Pichau. O sistema realiza a raspagem de dados (web scraping), filtra as melhores ofertas de acordo com um orçamento definido, gerencia um histórico de preços local para evitar notificações duplicadas e envia alertas em tempo real via Telegram.

O projeto foi estruturado aplicando boas práticas de Engenharia de Software, modularização e segurança da informação, sendo excelente para compor meu portfólio acadêmico em Ciência da Computação.

---

## 🛠️ Tecnologias e Bibliotecas Utilizadas

* **Python 3** (Linguagem base do projeto)
* **Selenium & Undetected-Chromedriver:** Para automação e navegação simulada, contornando bloqueios comuns de plataformas como o Cloudflare.
* **SQLite3:** Banco de dados relacional leve e nativo para persistência e comparação do histórico de preços.
* **PyTelegramBotAPI (telebot):** Integração com a API de Bots do Telegram para envio das notificações.
* **Python-Dotenv:** Gerenciamento de variáveis de ambiente para proteção de credenciais sensíveis (Tokens e IDs).

---

## 🧠 Arquitetura e Lógica do Sistema

O script foi modularizado para garantir um código limpo (*Clean Code*) e de fácil manutenção:

1.  **Isolamento de Extração:** Uma função dedicada extrai o HTML do card, limpa os caracteres de moeda (`R$`, `.`, `,`) e converte os valores para tipo numérico (`float`).
2.  **Memória do Sistema (SQLite):** O sistema realiza uma consulta `SELECT` antes de notificar. 
    * Se o produto for novo, ele salva no banco e envia o alerta.
    * Se o preço for igual ao da última busca, ele ignora (evitando spam).
    * Se o preço mudou, ele atualiza o registro (`UPDATE`) e envia o alerta de variação.

---

## 🚀 Como Configurar e Executar

### 1. Pré-requisitos
Certifique-se de ter o Google Chrome instalado no seu Linux e o ambiente virtual (`venv`) configurado.

### 2. Instalação das Dependências
Com a sua `venv` ativa, instale os pacotes necessários:
```bash
pip install undetected-chromedriver pyTelegramBotAPI python-dotenv