import requests
from bs4 import BeautifulSoup
import time
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import re

# Configuración inicial
MARCA = "GNB Sudameris"  # Reemplaza con el nombre de tu marca
PALABRAS_CLAVE = [MARCA.lower(), MARCA.replace(" ", "").lower()]  # Variaciones del nombre
CORREO_ALERTAS = "monitoreognbsuda@gmail.com"  # Correo para recibir alertas
INTERVALO_BUSQUEDA = 60  # 24 horas en segundos (ajusta según necesites)

# Lista de sitios para monitorear
FUENTES = {
    "Google Noticias": f"https://news.google.com/search?q={MARCA.replace(' ', '+')}",
    "Twitter": f"https://twitter.com/search?q={MARCA.replace(' ', '%20')}",
    "Facebook": f"https://www.facebook.com/public/{MARCA.replace(' ', '-')}",
    "Instagram": f"https://www.instagram.com/explore/tags/{MARCA.replace(' ', '')}/",
    # Cambiado para buscar en Google de forma general, donde podrían aparecer anuncios
    "Google Search (Ads/Web)": f"https://www.google.com/search?q={MARCA.replace(' ', '+')}"
}

# Configuración de email
def enviar_alerta(asunto, cuerpo):
    try:
        # Configura estos valores con tu servidor SMTP
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        # Asegúrate que este usuario sea una cuenta real de Hotmail/Outlook y que la contraseña sea correcta
        # Si tienes 2FA, usa una contraseña de aplicación.
        smtp_user = "monitoreognbsuda@gmail.com" # <--- ¡IMPORTANTE! Asegúrate que sea tu correo de Hotmail real
        smtp_pass = "TU_CONTRASEÑA_DE_HOTMAIL_O_APLICACION" # <--- ¡PÓN AQUÍ LA CONTRASEÑA REAL Y SEGURA!

        msg = MIMEText(cuerpo, 'html')
        msg['Subject'] = asunto
        msg['From'] = smtp_user
        msg['To'] = CORREO_ALERTAS

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, [CORREO_ALERTAS], msg.as_string())
        print("Alerta enviada por correo")
    except smtplib.SMTPAuthenticationError as e:
        print(f"Error de autenticación SMTP: {e}. Revisa el usuario y la contraseña (especialmente si usas 2FA).")
    except smtplib.SMTPException as e:
        print(f"Error SMTP general al enviar email: {e}")
    except Exception as e:
        print(f"Error inesperado enviando email: {e}")

# Función para buscar en Google Search (donde podrían aparecer anuncios)
def buscar_en_Google Search():
    print("\nBuscando en Google Search (posibles anuncios o menciones)...")
    try:
        url = FUENTES["Google Search (Ads/Web)"]
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'} # User-Agent más común
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            hallazgos = set()
            
            # Google usa diferentes selectores para anuncios y resultados orgánicos.
            # Los anuncios suelen tener un "Ad" o "Anuncio" al lado.
            # Esto es un intento de capturar enlaces y textos relevantes.
            
            # Buscar anuncios (estos selectores pueden cambiar con el tiempo)
            for ad_div in soup.select('div[data-text-ad], div[data-ad-module]'): # Ejemplos de selectores de anuncios
                title_tag = ad_div.find('span', role='text') # Puede variar
                link_tag = ad_div.find('a', href=True)
                
                if title_tag and link_tag:
                    title = title_tag.get_text().strip()
                    link = link_tag['href']
                    if any(palabra in title.lower() for palabra in PALABRAS_CLAVE) or any(palabra in link.lower() for palabra in PALABRAS_CLAVE):
                        hallazgos.add(f"AD: <a href='{link}'>{title}</a>")

            # Buscar resultados orgánicos que mencionen la marca
            for link_div in soup.select('div.g'): # Contenedor típico de resultados de búsqueda
                title_tag = link_div.select_one('h3')
                link_tag = link_div.select_one('a')
                
                if title_tag and link_tag:
                    title = title_tag.get_text().strip()
                    link = link_tag['href']
                    if any(palabra in title.lower() for palabra in PALABRAS_CLAVE) or any(palabra in link.lower() for palabra in PALABRAS_CLAVE):
                         # Evitar duplicados si ya fue encontrado como anuncio o si es el propio sitio oficial
                        if MARCA.lower() not in title.lower() and MARCA.lower() not in link.lower():
                            hallazgos.add(f"WEB: <a href='{link}'>{title}</a>")

            if hallazgos:
                mensaje = f"<h2>Menciones en Google Search (incl. posibles anuncios):</h2><ul>"
                for hallazgo in hallazgos:
                    mensaje += f"<li>{hallazgo}</li>"
                mensaje += "</ul>"
                enviar_alerta(f"🔍 Menciones de {MARCA} en Google Search", mensaje)
                return mensaje
            else:
                return "<p>No se encontraron menciones sospechosas en Google Search.</p>"
        else:
            return f"<p>Error al buscar en Google Search: Código {response.status_code}. Podría ser un bloqueo.</p>"
    except Exception as e:
        return f"<p>Error buscando en Google Search: {str(e)}</p>"

# Función para monitorear fuentes (la misma que tenías, pero ahora Google Search se maneja aparte)
def monitorear_fuentes():
    resultados = []
    
    for fuente, url in FUENTES.items():
        if fuente == "Google Search (Ads/Web)": # Ya lo manejamos separadamente
            continue 
            
        print(f"\nMonitoreando {fuente}...")
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                menciones = []
                
                # Buscar menciones según la fuente
                if fuente == "Google Noticias":
                    for article in soup.select('article'):
                        title_link_element = article.find('a')
                        if title_link_element:
                            title = title_link_element.get_text().lower()
                            link = title_link_element['href']
                            if any(palabra in title for palabra in PALABRAS_CLAVE):
                                menciones.append(f"<li><a href='https://news.google.com{link}'>{title[:100]}...</a></li>")
                
                elif fuente == "Twitter":
                    # El scraping de Twitter es muy complejo y usualmente requiere una API key
                    # para obtener resultados fiables sin bloqueos.
                    # Este selector puede no funcionar constantemente.
                    for tweet in soup.select('[data-testid="tweetText"]'): # Intento de selector más específico
                        text = tweet.get_text().lower()
                        if any(palabra in text for palabra in PALABRAS_CLAVE):
                            menciones.append(f"<li>{text[:200]}...</li>")
                
                elif fuente == "Facebook":
                    # El scraping de Facebook es aún más complejo y casi siempre bloqueado sin una API.
                    # Esta URL es de resultados públicos, pero el contenido es muy dinámico.
                    pass # Dejamos sin implementar lógica específica aquí por la dificultad.
                
                elif fuente == "Instagram":
                    # El scraping de Instagram requiere inicio de sesión y es fuertemente protegido.
                    # Esta URL solo muestra el feed de un hashtag, pero es difícil extraer data sin JS.
                    pass # Dejamos sin implementar lógica específica aquí por la dificultad.
                
                if menciones:
                    resultados.append(f"<h3>{fuente}:</h3><ul>{''.join(menciones[:5])}</ul>")
                else:
                    resultados.append(f"<p>No hay menciones recientes en {fuente}.</p>")
            else:
                resultados.append(f"<p>Error al monitorear {fuente}: Código {response.status_code}.</p>")
        except Exception as e:
            resultados.append(f"<p>Error monitoreando {fuente}: {str(e)}</p>")
    
    return "\n".join(resultados)

# Función principal
def main():
    print(f"Iniciando monitoreo de marca para: {MARCA}")
    print(f"Intervalo de búsqueda: {INTERVALO_BUSQUEDA/3600} horas")
    
    while True:
        print(f"\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Ejecutando búsqueda...")
        
        # Obtener resultados
        reporte_fuentes = monitorear_fuentes()
        reporte_Google Search = buscar_en_Google Search() # Ahora maneja Google Search

        # Crear reporte completo
        reporte_completo = f"""
        <html>
            <body>
                <h1>Reporte de Monitoreo de Marca: {MARCA}</h1>
                <h2>Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</h2>
                {reporte_fuentes}
                {reporte_Google Search}
                <hr>
                <p>Este es un reporte automático. Configuración actual: cada {INTERVALO_BUSQUEDA/3600} horas.</p>
                <p>Nota: El monitoreo de redes sociales y Google Ads mediante scraping es limitado y puede no ser fiable debido a protecciones anti-bot y contenido dinámico.</p>
            </body>
        </html>
        """
        
        # Guardar reporte en archivo
        with open(f"reporte_marca_{datetime.now().strftime('%Y%m%d_%H%M')}.html", "w", encoding="utf-8") as f:
            f.write(reporte_completo)
        
        # Enviar por correo si hay menciones o "hallazgos" en Google Search
        # Simplificamos la condición ya que reporte_fuentes siempre tendrá algo, y buscamos hallazgos específicos
        if "<li>" in reporte_Google Search or "menciones" in reporte_fuentes.lower():
            enviar_alerta(f"🔍 Reporte de marca: {MARCA}", reporte_completo)
        
        # Esperar para la próxima búsqueda
        print(f"\nEsperando {INTERVALO_BUSQUEDA/3600} horas para la próxima búsqueda...")
        time.sleep(INTERVALO_BUSQUEDA)

if __name__ == "__main__":
    main()
