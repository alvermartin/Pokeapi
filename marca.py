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
CORREO_ALERTAS = "alrubiano4@poligran.edu.co"  # Correo para recibir alertas
INTERVALO_BUSQUEDA = 86400  # 24 horas en segundos (ajusta según necesites)

# Lista de sitios para monitorear
FUENTES = {
    "Google Noticias": f"https://news.google.com/search?q={MARCA.replace(' ', '+')}",
    "Twitter": f"https://twitter.com/search?q={MARCA.replace(' ', '%20')}",
    "Facebook": f"https://www.facebook.com/public/{MARCA.replace(' ', '-')}",
    "Instagram": f"https://www.instagram.com/explore/tags/{MARCA.replace(' ', '')}/",
    "Dominios similares": f"https://www.google.com/search?q=site%3A*{MARCA.replace(' ', '')}*"
}

# Configuración de email (opcional)
def enviar_alerta(asunto, cuerpo):
    try:
        # Configura estos valores con tu servidor SMTP
        smtp_server = "smtp.poligran.edu.co"
        smtp_port = 587
        smtp_user = "alrubiano4@poligran.edu.co"
        smtp_pass = "Alver007."

        msg = MIMEText(cuerpo, 'html')
        msg['Subject'] = asunto
        msg['From'] = smtp_user
        msg['To'] = CORREO_ALERTAS

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, [CORREO_ALERTAS], msg.as_string())
        print("Alerta enviada por correo")
    except Exception as e:
        print(f"Error enviando email: {e}")

# Función para buscar clones de marca
def buscar_clones():
    print("\nBuscando posibles clones o dominios similares...")
    try:
        url = FUENTES["Dominios similares"]
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            dominios = set()
            
            # Buscar enlaces que podrían ser dominios similares
            for link in soup.find_all('a', href=True):
                href = link['href']
                if 'url?q=' in href:
                    dominio = href.split('url?q=')[1].split('&')[0]
                    if any(palabra in dominio.lower() for palabra in PALABRAS_CLAVE):
                        if MARCA.lower() not in dominio.lower() and dominio not in dominios:
                            dominios.add(dominio)
            
            if dominios:
                mensaje = f"<h2>Posibles clones o dominios similares encontrados:</h2><ul>"
                for dominio in dominios:
                    mensaje += f"<li><a href='{dominio}'>{dominio}</a></li>"
                mensaje += "</ul>"
                enviar_alerta(f"⚠️ Posibles clones de {MARCA} detectados", mensaje)
                return mensaje
            else:
                return "<p>No se encontraron dominios sospechosos.</p>"
        else:
            return f"<p>Error al buscar dominios: Código {response.status_code}</p>"
    except Exception as e:
        return f"<p>Error buscando clones: {str(e)}</p>"

# Función para monitorear fuentes
def monitorear_fuentes():
    resultados = []
    
    for fuente, url in FUENTES.items():
        if fuente == "Dominios similares":
            continue  # Ya lo manejamos separadamente
            
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
                        title = article.get_text().lower()
                        if any(palabra in title for palabra in PALABRAS_CLAVE):
                            link = article.find('a')['href']
                            menciones.append(f"<li><a href='https://news.google.com{link}'>{title[:100]}...</a></li>")
                
                elif fuente == "Twitter":
                    for tweet in soup.select('[data-testid="tweet"]'):
                        text = tweet.get_text().lower()
                        if any(palabra in text for palabra in PALABRAS_CLAVE):
                            menciones.append(f"<li>{text[:200]}...</li>")
                
                # Podrías añadir más lógica para otras fuentes aquí
                
                if menciones:
                    resultados.append(f"<h3>{fuente}:</h3><ul>{''.join(menciones[:5])}</ul>")
                else:
                    resultados.append(f"<p>No hay menciones recientes en {fuente}.</p>")
            else:
                resultados.append(f"<p>Error al monitorear {fuente}: Código {response.status_code}</p>")
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
        reporte_clones = buscar_clones()
        
        # Crear reporte completo
        reporte_completo = f"""
        <html>
            <body>
                <h1>Reporte de Monitoreo de Marca: {MARCA}</h1>
                <h2>Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</h2>
                {reporte_fuentes}
                {reporte_clones}
                <hr>
                <p>Este es un reporte automático. Configuración actual: cada {INTERVALO_BUSQUEDA/3600} horas.</p>
            </body>
        </html>
        """
        
        # Guardar reporte en archivo
        with open(f"reporte_marca_{datetime.now().strftime('%Y%m%d_%H%M')}.html", "w", encoding="utf-8") as f:
            f.write(reporte_completo)
        
        # Enviar por correo si hay menciones o clones
        if "menciones" in reporte_fuentes.lower() or "clones" in reporte_clones.lower():
            enviar_alerta(f"🔍 Reporte de marca: {MARCA}", reporte_completo)
        
        # Esperar para la próxima búsqueda
        print(f"\nEsperando {INTERVALO_BUSQUEDA/3600} horas para la próxima búsqueda...")
        time.sleep(INTERVALO_BUSQUEDA)

if __name__ == "__main__":
    main()
