mport requests
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
    "bank gnb",
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
    
    # --- Nueva Configuración de Geolocalización ---
# Puedes definir múltiples configuraciones de ubicación si quieres monitorear varias regiones.
UBICACIONES_MONITORIZAR = [
    {
        "location": "Bogota, Bogota, Colombia", # Ciudad, Departamento, País
        "gl": "co", # País de Google (Colombia)
        "hl": "es"  # Idioma de interfaz (Español)
    },
    {
        "location": "Miami, Florida, United States",
        "gl": "us",
        "hl": "en"
    },
    {
        "location": "Madrid, Community of Madrid, Spain",
        "gl": "es",
        "hl": "es"
    }
]

# --- Funciones (adaptadas para usar múltiples ubicaciones) ---
def verificar_anuncios_phishing(consulta, ubicacion_params):
    """
    Realiza una búsqueda en Google usando SerpApi con parámetros de ubicación.
    """
    print(f"\n--- Buscando en Google para: '{consulta}' en {ubicacion_params.get('location')} ---")
    
    # Construir los parámetros base
    params = {
        "engine": "google",
        "q": consulta,
        "api_key": SERPAPI_API_KEY,
        "num": 100 # Puedes ajustar este número, aunque 100 es un buen punto de partida para anuncios
    }
    
    # Añadir los parámetros de ubicación
    params.update(ubicacion_params) # Esto añade 'location', 'gl', 'hl' al diccionario params

    try:
        response = requests.get("https://serpapi.com/search", params=params)
        response.raise_for_status()
        data = response.json()

        if "ads" in data:
            print(f"  Se encontraron {len(data['ads'])} anuncio(s) para '{consulta}':")
            for i, ad in enumerate(data["ads"]):
                enlace_ad = ad.get("link")
                enlace_visible = ad.get("displayed_link")
                titulo_ad = ad.get("title")
                
                es_sospechoso = True
                
                if enlace_ad:
                    for dominio in DOMINIOS_OFICIALES:
                        if dominio in enlace_ad:
                            es_sospechoso = False
                            break
                
                if es_sospechoso and enlace_visible:
                     for dominio in DOMINIOS_OFICIALES:
                        if dominio in enlace_visible:
                            es_sospechoso = False
                            break

                print(f"    Anuncio {i+1}:")
                print(f"      Título: {titulo_ad}")
                print(f"      Enlace visible: {enlace_visible}")
                print(f"      URL final (vía SerpApi): {enlace_ad}")
                
                if es_sospechoso:
                    print("      *** ¡POSIBLE ANUNCIO DE PHISHING DETECTADO! ***")
                    print("      El enlace de este anuncio NO contiene tu dominio oficial.")
                    # Aquí es donde integrarías tu sistema de alertas (e.g., email, SMS)
                else:
                    print("      Parece un anuncio oficial.")
                print("-" * 40)
        else:
            print("  No se encontraron anuncios en los resultados para esta consulta/ubicación.")

    except requests.exceptions.RequestException as e:
        print(f"  Error al consultar SerpApi para '{consulta}' en {ubicacion_params.get('location')}: {e}")
    except json.JSONDecodeError:
        print(f"  Error al decodificar la respuesta JSON. Verifica clave API o consulta.")
    except Exception as e:
        print(f"  Ocurrió un error inesperado: {e}")

# --- Ejecución Principal ---
if __name__ == "__main__":
    print("Iniciando Script de Monitoreo de Phishing en Google Ads...\n")
    print(f"Monitoreando para los dominios: {', '.join(DOMINIOS_OFICIALES)}")

    for ubicacion in UBICACIONES_MONITORIZAR:
        for consulta in CONSULTAS_DE_BUSQUEDA:
            verificar_anuncios_phishing(consulta, ubicacion)
            time.sleep(7) # Aumentar el retraso para ser más amable con la API al hacer más solicitudes

    print("\nMonitoreo completado. Recuerda verificar manualmente y reportar.")
    print("Si encontraste un posible phishing, sigue estos pasos:")
    print("  1. Reporta el anuncio directamente en los resultados de búsqueda de Google (haz clic en ⋮ junto al anuncio).")
    print("  2. Reporta el sitio de phishing a la Navegación Segura de Google: https://safeBrowse.google.com/safeBrowse/report_phish/")
    print("  3. Encuentra el registrador del dominio (usando who.is) y reporta el abuso a ellos.")
