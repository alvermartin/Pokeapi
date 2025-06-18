import requests
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz # Para instalar: pip install fuzzywuzzy python-Levenshtein

def get_page_content(url):
    """Descarga el contenido HTML de una URL y extrae el texto principal."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Lanza una excepción para códigos de estado de error (4xx o 5xx)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Intenta extraer el texto del cuerpo principal o de elementos comunes de contenido
        # Esto puede requerir ajustes dependiendo de la estructura de tu sitio
        main_content = soup.find('body') # Empieza por el body
        if main_content:
            # Elimina scripts y estilos para limpiar el texto
            for script_or_style in main_content(['script', 'style', 'header', 'footer', 'nav']):
                script_or_style.extract()
            text = main_content.get_text(separator='\n', strip=True)
            return text
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error al acceder a {url}: {e}")
        return None

def compare_content(original_text, suspected_text, threshold=80):
    """
    Compara dos textos y devuelve la puntuación de similitud.
    Devuelve True si la similitud está por encima del umbral.
    """
    if not original_text or not suspected_text:
        return 0, False

    # fuzz.ratio compara la similitud de las cadenas completas
    # fuzz.partial_ratio es útil si el texto copiado es un fragmento de tu original
    similarity_score = fuzz.ratio(original_text, suspected_text)
    # También puedes probar con fuzz.token_sort_ratio o fuzz.token_set_ratio para más robustez

    print(f"Similitud de contenido: {similarity_score}%")
    return similarity_score, similarity_score >= threshold

# --- Parte principal del script ---
if __name__ == "__main__":
    your_website_url = "https://www.gnbsudameris.com.co" # ¡Reemplaza con tu URL!
    # Opcional: una URL de un sitio que sospeches que te copió
    suspected_copy_url = "https://personas.sudamerignb.fun" # ¡Reemplaza si tienes una sospecha!

    print(f"Obteniendo contenido de tu sitio: {your_website_url}")
    your_content = get_page_content(your_website_url)

    if your_content:
        # Puedes tomar un fragmento más pequeño y representativo para la búsqueda
        # Por ejemplo, los primeros 200 caracteres de un párrafo clave
        search_snippet = your_content[100:300] # Ajusta los índices según tu contenido
        print(f"\nFragmento para búsqueda (ejemplo): '{search_snippet}'")

        # --- Parte más desafiante: Automatizar búsqueda en Google ---
        # Opción 1: Usar una API de búsqueda (recomendado para fiabilidad, pero de pago)
        # from serpapi import GoogleSearch
        # params = {
        #     "q": f'"{search_snippet}" -site:{your_website_url}', # Excluye tu propio sitio
        #     "api_key": "TU_API_KEY_SERPAPI" # Regístrate en serpapi.com para una clave
        # }
        # search = GoogleSearch(params)
        # results = search.get_dict()
        # if 'organic_results' in results:
        #     for result in results['organic_results']:
        #         print(f"Posible copia encontrada en Google: {result['link']}")
        #         # Luego, descarga y compara el contenido de result['link']

        # Opción 2: Raspado web manual (muy propenso a ser bloqueado por Google)
        print("\n--- Simulación de detección de copia (manual) ---")
        if suspected_copy_url:
            print(f"Obteniendo contenido del sitio sospechoso: {suspected_copy_url}")
            suspected_content = get_page_content(suspected_copy_url)

            if suspected_content:
                score, is_similar = compare_content(your_content, suspected_content, threshold=75) # Umbral ajustable
                if is_similar:
                    print(f"\n¡ALERTA! Posible copia detectada en {suspected_copy_url} con un {score}% de similitud.")
                else:
                    print(f"\nNo se detectó una copia significativa en {suspected_copy_url} (similitud: {score}%).")
            else:
                print(f"No se pudo obtener el contenido de {suspected_copy_url}.")
        else:
            print("No se proporcionó una URL sospechosa para comparar directamente.")
            print("Para un monitoreo real, necesitarías una forma automática de obtener URLs sospechosas (ej. Google Search API).")

    else:
        print(f"No se pudo obtener el contenido de tu sitio: {your_website_url}")
