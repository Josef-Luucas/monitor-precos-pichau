import time
import random
import threading
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3
import os
from dotenv import load_dotenv
import undetected_chromedriver as uc

load_dotenv()

token = os.getenv('TELEGRAM_TOKEN')
chat_id = os.getenv('TELEGRAM_CHAT_ID')
bot = telebot.TeleBot(token)

#lista de produtos compartilhada para o bot saber o que buscar quando solicitado
produts_para_monitorar = [
    {
        "id": "placa_mae",
        "categoria": "Placa Mãe",
        "preco_alvo": 600.00,
        "link": (
            "https://www.pichau.com.br/hardware/placa-m-e?marcas=121,34,35,36&product_category=6460&sort=price-asc&socket=539,6526,6689,7251,7685,7793,854",
            "https://www.kabum.com.br/hardware/placas-mae?page_number=1&page_size=60&facet_filters=eyJTb2NrZXQiOlsiQU00IiwiQU01IiwiTEdBIDExNTAiLCJMR0EgMTE1MSIsIkxHQSAxMjAwIiwiTEdBIDE3MDAiLCJMR0EgMTg1MSJdLCJwcmljZSI6eyJtaW4iOjIwMCwibWF4IjoxNzM4Mi4zNn0sIm1hbnVmYWN0dXJlciI6WyJBU1JvY2siLCJBU1VTIiwiQmlvc3RhciIsIkR1ZXgiLCJkdWV4IiwiR2lnYWJ5dGUiLCJNU0kiLCJBaXRlayIsIkFsbHRlayIsIkFya3RlayJdfQ==&sort=price",
        )
    },
    {
        "id": "ryzen",
        "categoria": "Processadores Ryzen",
        "preco_alvo": 800.00,
        "link": (
            "https://www.pichau.com.br/hardware/processadores/amd?sort=price-asc&socket=539,6539,6689", #am4 e am5
            "https://www.kabum.com.br/hardware/processadores/processador-amd/ryzen?page_number=1&page_size=60&facet_filters=eyJTb2NrZXQiOlsiQU01IiwiQU00Il19&sort=price" #am4 e am5
        )
    },
    {
        "id": "intel",
        "categoria": "Processadores Intel",
        "preco_alvo": 750.00,
        "link": (
            "https://www.pichau.com.br/hardware/processadores?marcas=117&sort=price-asc",#todos da pichau
            "https://www.kabum.com.br/hardware/processadores?page_number=1&page_size=60&facet_filters=eyJtYW51ZmFjdHVyZXIiOlsiSW50ZWwiXSwiU29ja2V0IjpbIkxHQSAxMTUxIl0sInByaWNlIjp7Im1pbiI6MTAwLCJtYXgiOjE2NzkuODJ9fQ==&sort=price",#intel da 6° a 9°
            "https://www.kabum.com.br/hardware/processadores/processador-intel?page_number=1&page_size=60&facet_filters=eyJTb2NrZXQiOlsiTEdBIDExNTAiXX0=&sort=price",#intel da 4° e 5°
            "https://www.kabum.com.br/hardware/processadores?page_number=1&page_size=60&facet_filters=eyJtYW51ZmFjdHVyZXIiOlsiSW50ZWwiXSwiU29ja2V0IjpbIkxHQSAxMjAwIl0sInByaWNlIjp7Im1pbiI6MTAwLCJtYXgiOjE2NzkuODJ9fQ==&sort=price", #intel da 10° e 11°
            "https://www.kabum.com.br/hardware/processadores?page_number=1&page_size=60&facet_filters=eyJtYW51ZmFjdHVyZXIiOlsiSW50ZWwiXSwiU29ja2V0IjpbIkxHQSAxNzAwIl0sInByaWNlIjp7Im1pbiI6MTAwLCJtYXgiOjE2NzkuODJ9fQ==&sort=price", #intel da 12° a 14°
        )
    },
    {
        "id": "gpu",
        "categoria": "Placas de Vídeos",
        "preco_alvo": 2000.00,
        "link": (
            "https://www.pichau.com.br/hardware/placa-de-video?forca=367&sort=price-asc&price=1000_10000",#placas de vídeo AMD
            "https://www.pichau.com.br/hardware/placa-de-video/nvidia?sort=price-asc&price=1000_*",#placas de vídeo NVIDIA
            "https://www.pichau.com.br/hardware/placa-de-video?placadevideo=6708&sort=price-asc",#placas de vídeo Intel
            "https://www.kabum.com.br/hardware/placa-de-video-vga/placa-de-video-amd?page_number=1&page_size=60&facet_filters=eyJwcmljZSI6eyJtaW4iOjAsIm1heCI6MTM3OTl9LCJSYWRlb24gUlggNzAwMCBTZXJpZXMiOlsiUlggNzYwMCJdfQ==&sort=price",#rx 7000 series
            "https://www.kabum.com.br/hardware/placa-de-video-vga?page_number=1&page_size=60&facet_filters=eyJHZUZvcmNlIFJUWCBTw6lyaWUgNTAiOlsiUlRYIDUwNTAiLCJSVFggNTA2MCJdfQ==&sort=price", #rtx 5000 series
            "https://www.kabum.com.br/hardware/placa-de-video-vga?page_number=1&page_size=60&facet_filters=eyJHZUZvcmNlIFJUWCBTw6lyaWUgMzAiOlsiUlRYIDUwNTAiLCJSVFggNTA2MCIsIlJUWCAzMDYwIFRpIl19&sort=price",#rtx 3000 series
            "https://www.kabum.com.br/hardware/placa-de-video-vga?page_number=1&page_size=60&facet_filters=eyJSYWRlb24gUlggU8OpcmllIDUwMCI6WyJSWCA1ODAiXSwibWFudWZhY3R1cmVyIjpbIkJpb3N0YXIiLCJBaXRlayJdfQ==&sort=price",#rx 580
        )
    },
    {
        "id": "fontes",
        "categoria": "Fontes",
        "preco_alvo": 450.00,
        "link": (
            "https://www.pichau.com.br/hardware/fonte?eficiencia_fonte=7597,7599,7600,7601&sort=price-asc&potencia_fonte=6483,6484,6485",
            "https://www.kabum.com.br/hardware/fontes?page_number=1&page_size=60&facet_filters=eyI4MCBQbHVzIjpbIkdvbGQiLCJQbGF0aW51bSIsIlRpdGFuaXVtIl0sInByaWNlIjp7Im1pbiI6MTIwLCJtYXgiOjE5OTkuOTl9fQ==&sort=price"
        )
    }
]

def extrair_dados(elemento):
    text_preco = elemento.text
    
    #ignora se for selo de desconto, percentagem, juros ou parcelamento
    if '%' in text_preco.lower() or 'desconto' in text_preco.lower() or 'juros' in text_preco.lower() or 'x de' in text_preco.lower():
        raise ValueError("Elemento ignorado por ser badge ou preço parcelado")

    try:
        link_elemento = elemento.find_element(By.XPATH, "./ancestor::a")
        url_produto = link_elemento.get_attribute("href")
    except:
        url_produto = "Link não encontrado"

    nome_produto = "Hardware / Peça em Promoção"         #classes dos sites como preço,titulo etc
    selectors_titulo = [
        ".mui-7xt5d3-product_info_title-noMarginBottom", 
        "h2.MuiTypography-root.MuiTypography-h6", 
        ".text-sm.text-left.text-gray-800",
        "h2", 
        "h3", 
        "span"
    ]
    #sequencia de testes para saber se cada classe pode ser encontrada, caso não seja encontrada, passa para a próxima
    for sel in selectors_titulo:
        try:
            titulo_el = link_elemento.find_element(By.CSS_SELECTOR, sel)
            texto_encontrado = titulo_el.text.strip()
            if texto_encontrado and len(texto_encontrado) > 3 and '%' not in texto_encontrado:
                nome_produto = texto_encontrado
                break
        except:
            continue

    url_imagem = None
    try:
        img_elemento = link_elemento.find_element(By.CSS_SELECTOR, ".mui-rfxowm-media, img")
        url_imagem = img_elemento.get_attribute("src")
    except:
        try:
            card_pai = elemento.find_element(By.XPATH, "./ancestor::div[contains(@class, 'product') or ancestor::div[contains(@class, 'sc-')] or self::div]")
            img_elemento = card_pai.find_element(By.TAG_NAME, "img")
            url_imagem = img_elemento.get_attribute("src")
        except:
            pass
    
    try:
        limpo = text_preco.replace("R$", "").replace(".", "").replace(" ", "").strip()
        limpo = ''.join(c for c in limpo if c.isdigit() or c == ',')
        preco_float = float(limpo.replace(",", "."))
    except:
        preco_float = 99999.0
    
    return url_produto, nome_produto, url_imagem, text_preco, preco_float

def iniciar_banco():
    conn = sqlite3.connect('precos.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            link TEXT PRIMARY KEY,
            nome TEXT,
            preco REAL,
            data_atualizacao TEXT
        )
    ''')
    conn.commit()
    conn.close()

def verificar_e_atualizar_preco(link_produto, nome_produto, preco_atual):
    conn = sqlite3.connect('precos.db')
    cursor = conn.cursor()
    cursor.execute('SELECT preco FROM produtos WHERE link = ?', (link_produto,))
    resultado = cursor.fetchone()
    agora = time.strftime('%Y-%m-%d %H:%M:%S')
    
    if resultado is None:
        cursor.execute('INSERT INTO produtos (link, nome, preco, data_atualizacao) VALUES (?, ?, ?, ?)', 
                       (link_produto, nome_produto, preco_atual, agora))
        conn.commit()
        conn.close()
        return True
    
    preco_antigo = resultado[0]
    if preco_atual != preco_antigo:
        cursor.execute('UPDATE produtos SET nome = ?, preco = ?, data_atualizacao = ? WHERE link = ?', 
                       (nome_produto, preco_atual, agora, link_produto))
        conn.commit()
        conn.close()
        return True
    
    conn.close()
    return False

def enviar_alerta_telegram(chat_destino, categoria, nome_produto, text_preco, url_produto, url_imagem=None):
    mensagem = f"🚀 *Alerta de {categoria}!*\n\n" \
               f"📦 *{nome_produto}*\n\n" \
               f"💰 *Preço Atual:* {text_preco}\n" \
               f"🔗 *Link:* {url_produto}"
               
    if url_imagem:
        try:
            bot.send_photo(chat_destino, url_imagem, caption=mensagem, parse_mode="Markdown")
        except Exception:
            bot.send_message(chat_destino, mensagem, parse_mode="Markdown", disable_web_page_preview=True)
    else:
        bot.send_message(chat_destino, mensagem, parse_mode="Markdown", disable_web_page_preview=True)
        
def buscar_categoria_especifica(chat_id_destino, categoria_id):
    item_alvo = None
    for item in produts_para_monitorar:
        if item["id"] == categoria_id:
            item_alvo = item
            break
            
    if not item_alvo:
        bot.send_message(chat_id_destino, "❌ Categoria não encontrada.")
        return

    bot.send_message(chat_id_destino, f"🔍 Buscando preços atuais para *{item_alvo['categoria']}*, aguarde...", parse_mode="Markdown")
    
    navegador = None
    try:
        options = uc.ChromeOptions() 
        options.add_argument("--disable-gpu")
        options.add_argument("--window-position=-2000,0")  #mantém fora do ecrã visível
        navegador = uc.Chrome(options=options)

        encontrou_algum = False
        links_processados_nesta_busca = set()

        for link_atual in item_alvo["link"]:
            try:
                navegador.get(link_atual)
                
                seletor_css = ".mui-12athy2-price_vista, .text-base.font-semibold.text-gray-800"
                try:
                    WebDriverWait(navegador, 15).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, seletor_css))
                    )
                except:
                    pass

                elemento_preco = navegador.find_elements(By.CSS_SELECTOR, seletor_css)
                
                for elemento in elemento_preco:
                    try:
                        url_produto, nome_produto, url_imagem, text_preco, preco_float = extrair_dados(elemento)
                    
                        if url_produto != "Link não encontrado" and url_produto not in links_processados_nesta_busca:
                            if preco_float <= item_alvo["preco_alvo"] and preco_float > 10.0:
                                links_processados_nesta_busca.add(url_produto)
                                encontrou_algum = True
                                enviar_alerta_telegram(chat_id_destino, f"{item_alvo['categoria']} (Manual)", nome_produto, text_preco, url_produto, url_imagem)
                                time.sleep(1)
                    except:
                        continue
            except Exception as e:
                print(f"Erro no link: {e}")
                
        if not encontrou_algum:
            bot.send_message(chat_id_destino, f"⚠️ Nenhum produto abaixo de R$ {item_alvo['preco_alvo']} encontrado no momento para {item_alvo['categoria']}.")
        else:
            bot.send_message(chat_id_destino, f"✅ Busca manual de *{item_alvo['categoria']}* concluída!", parse_mode="Markdown")

    except Exception as e:
        bot.send_message(chat_id_destino, f"❌ Erro ao abrir navegador na busca manual: {e}")
    finally:
        if navegador:
            try:
                navegador.quit()
            except:
                pass

@bot.message_handler(commands=['categorias', 'buscar', 'menu'])
def enviar_menu_categorias(message):
    markup = InlineKeyboardMarkup()
    for item in produts_para_monitorar:
        botao = InlineKeyboardButton(text=item["categoria"], callback_data=f"cat_{item['id']}")
        markup.add(botao)
    
    bot.send_message(message.chat.id, "🎛 *Escolha a categoria que deseja buscar agora:*", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith('cat_'))
def callback_query(call):
    categoria_id = call.data.replace('cat_', '')
    bot.answer_callback_query(call.id, text="Iniciando busca...")
    threading.Thread(target=buscar_categoria_especifica, args=(call.message.chat.id, categoria_id)).start()

def loop_monitoramento_automatico():
    print("🤖 Loop automático de monitoramento iniciado em segundo plano.")
    while True:
        navegador = None
        try:
            options = uc.ChromeOptions() 
            options.add_argument("--disable-gpu")
            options.add_argument("--window-position=-2000,0")  #mantém fora do ecrã visível
            navegador = uc.Chrome(options=options)

            for item in produts_para_monitorar:
                categoria_atual = item["categoria"]
                preco_limite = item["preco_alvo"]
                links_processados_nesta_busca = set()
                
                for link_atual in item["link"]:
                    try:
                        navegador.get(link_atual)
                        
                        seletor_css = ".mui-12athy2-price_vista, .text-base.font-semibold.text-gray-800"
                        try:
                            WebDriverWait(navegador, 15).until(
                                EC.presence_of_all_elements_located((By.CSS_SELECTOR, seletor_css))
                            )
                        except:
                            pass

                        elemento_preco = navegador.find_elements(By.CSS_SELECTOR, seletor_css)
                        
                        for elemento in elemento_preco:
                            try:
                                url_produto, nome_produto, url_imagem, text_preco, preco_float = extrair_dados(elemento)
                            
                                if url_produto != "Link não encontrado" and url_produto not in links_processados_nesta_busca:
                                    if preco_float < preco_limite and preco_float > 10.0:
                                        links_processados_nesta_busca.add(url_produto)
                                        if verificar_e_atualizar_preco(url_produto, nome_produto, preco_float):
                                            enviar_alerta_telegram(chat_id, categoria_atual, nome_produto, text_preco, url_produto, url_imagem)
                                            time.sleep(1)
                            except:
                                continue
                    except:
                        pass

                time.sleep(random.uniform(3, 5))        
            
            if navegador:
                navegador.quit()
            time.sleep(900)  #aguardando 15 minutos
            
        except Exception as e:
            print(f"Erro no loop automático: {e}")
            if navegador:
                try:
                    navegador.quit()
                except:
                    pass
            time.sleep(300)

if __name__ == "__main__":
    iniciar_banco()
    
    t_monitor = threading.Thread(target=loop_monitoramento_automatico, daemon=True)
    t_monitor.start()
    
    print("🤖 Bot do Telegram escutando comandos (/categorias)... Pressione Ctrl+C para sair.")
    try:
        bot.infinity_polling()
    except KeyboardInterrupt:
        print("\n🛑 Bot encerrado pelo utilizador (Ctrl+C). A limpar processos e a sair...")