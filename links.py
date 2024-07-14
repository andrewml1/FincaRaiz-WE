from selenium import webdriver
from selenium.webdriver.common.by import By

def obtener_enlaces_totales(numpaginas):
    driver = webdriver.Chrome()

    enlaces_totales = []

    for pagina in range(1, numpaginas+1):  # Ajusta el rango según sea necesario
        url = f"https://www.fincaraiz.com.co/venta/apartamentos/el-poblado/suroriente/medellin/hasta-500000000/pagina{pagina}?&IDmoneda=4"
        driver.get(url)

        # Espera a que la página se cargue completamente
        # driver.implicitly_wait(10)

        try:
            # Encontrar el contenedor principal
            contenedor = driver.find_element(By.XPATH, '//*[@id="__next"]/div[3]/div/section')
            # Encontrar todas las tarjetas dentro del contenedor
            tarjetas = contenedor.find_elements(By.XPATH, './div')

            if not tarjetas:
                print("No se encontraron tarjetas dentro del contenedor.")
            else:
                print(f"Se encontraron {len(tarjetas)} tarjetas dentro del contenedor.")
                for tarjeta in tarjetas:
                    enlaces = tarjeta.find_elements(By.TAG_NAME, 'a')
                    for enlace in enlaces:
                        href = enlace.get_attribute("href")
                        enlaces_totales.append(href)
        except Exception as e:
            print(f"Error al buscar el contenedor o las tarjetas: {e}")

    driver.quit()

    return enlaces_totales
