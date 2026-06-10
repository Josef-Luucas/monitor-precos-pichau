import setuptools
import undetected_chromedriver as uc #importando essa biblioteca para o cloudfare não bloquear o acesso
import time
import random
from selenium.webdriver.common.by import By  #importando o by para dizer para procurar pelo nome da classe
import telebot
import sqlite3 #integrando banco de dados para ver se houve alteração de preço
import os
from dotenv import load_dotenv

load_dotenv()

token = os.getenv('TELEGRAM_TOKEN')
chat_id = os.getenv('TELEGRAM_CHAT_ID')
bot = telebot.TeleBot(token)

def extrair_link_e_preco(elemento):
    """
    Recebe o elemento HTML do preço, localiza o link correspondente,
    faz a limpeza do texto e retorna (url, texto_original, preco_float).
    """
    #pegando o link subindo até a tag <a>
    link_elemento = elemento.find_element(By.XPATH, "./ancestor::a")
    url_produto = link_elemento.get_attribute("href")
    
    #pegando o texto do preço original
    text_preco = elemento.text
    
    #fazendo a limpeza e conversão matemática do preço
    limpo = text_preco.replace("R$", "").replace(".", "").replace(" ", "").strip()
    preco_float = float(limpo.replace(",", "."))
    
    return url_produto, text_preco, preco_float


# ==================== CONFIGURAÇÃO DO BANCO DE DADOS ====================

def iniciar_banco():
    conn = sqlite3.connect('precos.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            link TEXT PRIMARY KEY,
            preco REAL,
            data_atualizacao TEXT
        )
    ''')
    conn.commit()
    conn.close()

def verificar_e_atualizar_preco(link_produto, preco_atual):
    conn = sqlite3.connect('precos.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT preco FROM produtos WHERE link = ?', (link_produto,))
    resultado = cursor.fetchone()
    agora = time.strftime('%Y-%m-%d %H:%M:%S')
    
    if resultado is None:
        cursor.execute('INSERT INTO produtos (link, preco, data_atualizacao) VALUES (?, ?, ?)', 
                       (link_produto, preco_atual, agora))
        conn.commit()
        conn.close()
        return True
    
    preco_antigo = resultado[0]
    
    if preco_atual != preco_antigo:
        cursor.execute('UPDATE produtos SET preco = ?, data_atualizacao = ? WHERE link = ?', 
                       (preco_atual, agora, link_produto))
        conn.commit()
        conn.close()
        return True
    
    conn.close()
    return False

iniciar_banco()

options = uc.ChromeOptions() 
navegador = uc.Chrome(options=options , version_main = 148) #configurando o navegador para ser o chrome versão 148

link = "https://www.pichau.com.br/hardware/placa-m-e?product_category=6460&marcas=121%2C34%2C35%2C36&socket=539&sort=price-asc"
navegador.get(link)

time.sleep(random.uniform(3, 5)) 
motherboard = navegador.find_elements(By.CLASS_NAME, "mui-12athy2-price_vista")
#usando o for para percorrer a lista
print(f"Foram encontrados {len(motherboard)} preços:")
#usando o enumarete para ver qual foi cada produto
for i, elemento in enumerate(motherboard):
    try:
        #chamando a nova função que isola a extração
        url_produto, text_preco, preco_float = extrair_link_e_preco(elemento)
        
        if preco_float < 500.00:
            
            #validando com o banco de dados
            if verificar_e_atualizar_preco(url_produto, preco_float):
                print(f"Produto {i+1}: {text_preco} - Alteração detectada! Enviando...")
                
                mensagem = f"🚀 **Alerta de Preço!**\n\n" \
                           f"💰 Preço Atual: {text_preco}\n" \
                           f"🔗 Link: {url_produto}"
                
                bot.send_message(chat_id, mensagem, parse_mode="Markdown")
                time.sleep(1)
            else:
                print(f"Produto {i+1}: Sem alterações no preço (R$ {preco_float}).")
                
    except Exception as e:
        print(f"Erro no produto {i+1}: {e}")

time.sleep(6)
navegador.quit()