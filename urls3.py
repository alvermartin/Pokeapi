import requests
import json # Para imprimir JSON de forma legible (útil para depurar)
import time # Para añadir retrasos entre solicitudes

# --- Configuración ---
# IMPORTANTE: Reemplaza con tu clave API de SerpApi real
SERPAPI_API_KEY = "9b87fea62f2dfe5b31a9b98bf674fc086167a9d1f1d01be54b9e8430d3bcc26c"

# IMPORTANTE: Reemplaza con el/los dominio(s) oficial(es) de tu empresa
# Usa una lista si tienes varios dominios oficiales
DOMINIOS_OFICIALES = [
    "www.gnbsudameris.com.co",
    "servicios.sudameris.com.co",
    "www.servibanca.com.co",
     "www.gnbsudameris.com"
]

# Palabras clave a buscar en Google Ads
# Piensa en lo que tus clientes escribirían para encontrarte o para iniciar sesión.
CONSULTAS_DE_BUSQUEDA = [
    "gnbbank.com",
    "GnbSudameris",
    "LognGNBsudameris",
    "GNBAPP",
    "Servicio al cliente GNB sudameris",
    "www.gnbsudameris.com.co",
    "GNB Sudameris empresas"
]

# --- Funciones ---
def verificar_anuncios_phishing(consulta):
    """
    Realiza una búsqueda en Google usando SerpApi y verifica si hay anuncios sospechosos.
    """
    print(f"\n--- Buscando en Google por: '{consulta}' ---")
    
    params = {
        "engine": "google",
        "q": consulta,
        "api_key": SERPAPI_API_KEY,
        "num": 100 # Solicita más resultados, ya que los anuncios pueden aparecer más abajo
        # Puedes añadir otros parámetros como 'location', 'gl', 'hl' para geolocalización
        # "location": "Bogota, Bogota, Colombia" # Ejemplo: apuntar a una ubicación específica
    }

    try:
        response = requests.get("https://serpapi.com/search", params=params)
        response.raise_for_status() # Lanza una excepción para errores HTTP (4xx o 5xx)
        data = response.json()

        # Verificar anuncios en la respuesta
        if "ads" in data:
            print(f"  Se encontraron {len(data['ads'])} anuncio(s) para '{consulta}':")
            anuncio_encontrado = False
            for i, ad in enumerate(data["ads"]):
                enlace_ad = ad.get("link")
                enlace_visible = ad.get("displayed_link")
                titulo_ad = ad.get("title")
                
                es_sospechoso = True # Asumir sospechoso hasta que se demuestre lo contrario
                
                # Verificar si el enlace del anuncio (URL final) contiene alguno de los dominios oficiales
                if enlace_ad:
                    for dominio in DOMINIOS_OFICIALES:
                        if dominio in enlace_ad:
                            es_sospechoso = False
                            break # Se encontró un dominio oficial, por lo tanto, no es sospechoso según la URL final
                
                # Si no es sospechoso por la URL final, también verificar el enlace visible (lo que el usuario ve)
                if es_sospechoso and enlace_visible:
                     for dominio in DOMINIOS_OFICIALES:
                        if dominio in enlace_visible:
                            es_sospechoso = False
                            break # Se encontró un dominio oficial, por lo tanto, no es sospechoso según el enlace visible

                print(f"    Anuncio {i+1}:")
                print(f"      Título: {titulo_ad}")
                print(f"      Enlace visible: {enlace_visible}")
                print(f"      URL final (vía SerpApi): {enlace_ad}")
                
                if es_sospechoso:
                    print("      *** ¡POSIBLE ANUNCIO DE PHISHING DETECTADO! ***")
                    print("      El enlace de este anuncio NO contiene tu dominio oficial.")
                    # Aquí podrías activar una alerta: enviar un correo electrónico, SMS, registrar en un archivo, etc.
                    # Ejemplo: enviar_correo_alerta(titulo_ad, enlace_visible, enlace_ad)
                else:
                    print("      Parece un anuncio oficial.")
                print("-" * 40)
                anuncio_encontrado = True
            if not anuncio_encontrado:
                print("  No se encontraron anuncios para esta consulta.")
        else:
            print("  No se encontraron anuncios en los resultados de búsqueda para esta consulta.")

    except requests.exceptions.RequestException as e:
        print(f"  Error al consultar SerpApi para '{consulta}': {e}")
    except json.JSONDecodeError:
        print(f"  Error al decodificar la respuesta JSON para '{consulta}'. Verifica tu clave API o consulta.")
    except Exception as e:
        print(f"  Ocurrió un error inesperado para '{consulta}': {e}")

# --- Ejecución Principal ---
if __name__ == "__main__":
    print("Iniciando Script de Monitoreo de Phishing en Google Ads...\n")
    print(f"Monitoreando para los dominios: {', '.join(DOMINIOS_OFICIALES)}")

    for consulta in CONSULTAS_DE_BUSQUEDA:
        verificar_anuncios_phishing(consulta)
        time.sleep(5) # Sé educado con la API, añade un retraso entre solicitudes

    print("\nMonitoreo completado. Recuerda verificar manualmente los enlaces sospechosos y reportarlos.")
    print("Si encontraste un posible phishing, sigue estos pasos:")
    print("  1. Reporta el anuncio directamente en los resultados de búsqueda de Google (haz clic en ⋮ junto al anuncio).")
    print("  2. Reporta el sitio de phishing a la Navegación Segura de Google: https://safeBrowse.google.com/safeBrowse/report_phish/")
    print("  3. Encuentra el registrador del dominio (usando who.is) y reporta el abuso a ellos.")
