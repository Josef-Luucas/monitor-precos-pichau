🕵️‍♂️ Monitor Inteligente de Preços - Pichau & KaBuM

Este é um projeto desenvolvido com o objetivo de monitorizar automaticamente os preços de componentes de hardware (placas-mãe, processadores, placas de vídeo e fontes) nos sites da Pichau e da KaBuM. O sistema realiza a raspagem de dados (web scraping), filtra as melhores ofertas de acordo com um orçamento definido, gerencia um histórico de preços local para evitar notificações duplicadas e envia alertas em tempo real via Telegram.

O projeto foi estruturado aplicando boas práticas de Engenharia de Software, modularização e segurança da informação, sendo excelente para compor meu portfólio acadêmico em Ciência da Computação.

🛠️ Tecnologias e Bibliotecas Utilizadas

Python 3 (Linguagem base do projeto)

Selenium & Undetected-Chromedriver: Para automação e navegação simulada, contornando proteções anti-bot rigorosas (Cloudflare).

SQLite3: Banco de dados relacional leve e nativo para persistência e comparação do histórico de preços.

PyTelegramBotAPI (telebot): Integração com a API do Telegram para bot interativo com comandos e alertas automáticos.

Python-Dotenv: Gerenciamento de variáveis de ambiente para proteção de credenciais sensíveis (Tokens e IDs).

🧠 Arquitetura e Lógica do Sistema

O script foi modularizado para garantir um código limpo (Clean Code) e de fácil manutenção:

Isolamento de Extração e Filtro de Preços: Função dedicada para sanitizar strings de moeda (R$, ., ,) e convertê-las para float. Conta com filtros ativos que descartam badges promocionais (%, desconto) e parcelamentos (x de), garantindo a captura estrita do valor à vista real.

Navegação Off-Screen: Utiliza posicionamento de janela fora da área visível do monitor (--window-position=-2000,0), mantendo a renderização ativa exigida pela Pichau sem interferir na área de trabalho do usuário.

Memória do Sistema (SQLite): Realiza uma consulta SELECT antes de notificar:

Produto novo: Salva o registro no banco de dados e dispara o alerta.

Preço inalterado: Ignora o envio, prevenindo spam.

Preço alterado: Executa UPDATE no banco e envia o alerta da variação.

Resiliência e Encerrando Limpo: Tratamento de exceções com blocos try...finally garantindo que instâncias do Chrome sejam finalizadas (navegador.quit()) em caso de interrupção abrupta (Ctrl + C).

🚀 Como Configurar e Executar

1. Clonar o Repositório

git clone https://github.com/Josef-Luucas/monitor-precos-pichau.git
cd monitor-precos-pichau


2. Instalação das Dependências

Com o seu ambiente virtual (venv) ativo, instale os pacotes necessários:

pip install undetected-chromedriver pyTelegramBotAPI python-dotenv selenium


3. Configuração de Variáveis de Ambiente

Crie um arquivo chamado .env na raiz do projeto (este arquivo é ignorado pelo Git por razões de segurança):

TELEGRAM_TOKEN=seu_token_aqui
TELEGRAM_CHAT_ID=seu_chat_id_aqui


4. Executando o Bot

Para iniciar o monitoramento em segundo plano e a escuta de comandos no Telegram:

python "monitor de preço.py"


Para interromper a execução do script com segurança a qualquer momento, pressione Ctrl + C no terminal.

🎮 Comandos do Bot no Telegram

/categorias ou /menu: Abre o menu interativo com botões para disparar buscas manuais por categoria a qualquer momento.

👤 Autor

Desenvolvido por Josef Lucas no âmbito de estudos em Ciência da Computação.