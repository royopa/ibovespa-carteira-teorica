# -*- coding: utf-8 -*-
import sys
import time
from datetime import datetime

from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from bs4 import BeautifulSoup


def get_webdriver():
    options = FirefoxOptions()
    options.add_argument("--headless")

    driver = webdriver.Firefox(
        firefox_options=options,
        executable_path=r'drivers/geckodriver',
    )

    # Seleciona a página de extrato
    index_url = 'http://bvmf.bmfbovespa.com.br/indices/ResumoCarteiraTeorica.aspx?Indice=IBOV&idioma=pt-br'
    driver.get(index_url)
    time.sleep(2)
    return driver


def fetch_portfolio_composition(table_content):
    index_members = {}
    data = BeautifulSoup(table_content, 'lxml')

    for tr in data.find_all('tr'):
        try:
            col_vle = [member.text.strip() for member in tr.find_all('span')]
            col_desc = ['symbol', 'name', 'type', 'qty', 'part']
            symbol = col_vle[0]

            for i, (value, desc) in enumerate(zip(col_vle, col_desc)):
                if i == 0:
                    if not symbol.startswith('Quantidade'):
                        index_members[symbol] = {}

                index_members[symbol][desc] = value
        except (KeyError, ValueError, IndexError) as e:
            print("WARN: could not be able to parse data {}".format(e))
            continue
    
    return index_members.items()


def main():
    webdriver = get_webdriver()
    data = webdriver.find_element_by_id("ctl00_contentPlaceHolderConteudo_lblTitulo").text
    data = data.split('Carteira Teórica do Ibovespa válida para ')[1]
    date_object = datetime.strptime(data, '%d/%m/%y').date()
    print(date_object)

    table_content = webdriver.find_element_by_id(
        'ctl00_contentPlaceHolderConteudo_grdResumoCarteiraTeorica_ctl00'
    ).get_attribute('innerHTML')

    # Fecha navegador
    webdriver.quit()

    dados = fetch_portfolio_composition(table_content)
    for row in dados:
        print(row[1])
  

if __name__ == '__main__':
    main()
