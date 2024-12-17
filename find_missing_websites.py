import xml.etree.ElementTree as ET
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from googlesearch import search
import csv
import time

# Funzione per leggere il file XML e ottenere nomi aziende e homepage
def parse_xml(file_path):
    """Legge il file XML e restituisce una lista di tuple (nome azienda, homepage)."""
    tree = ET.parse(file_path)
    root = tree.getroot()
    namespace = {"ns": "http://www.bvdep.com/schemas/RemoteAccessDataResults.xsd"}
    
    companies = []
    for record in root.findall("ns:record", namespace):
        company_name = record.find("ns:item[@field='RAGSOC']", namespace).text
        homepage_field = record.find("ns:item[@field='HOMEPAGE']", namespace)
        homepage = homepage_field.text if homepage_field.text else None
        companies.append((company_name, homepage))
    return companies

# Funzione per cercare siti web mancanti con Google Search
def find_website(company_name):
    """Cerca il sito web di un'azienda usando Google Search."""
    query = f"{company_name} site:.it"
    try:
        for result in search(query, num_results=1, lang="it"):
            return result  # Restituisce il primo risultato trovato
    except Exception as e:
        print(f"Errore nella ricerca per {company_name}: {e}")
        return None

# Funzione principale
def main():
    input_file = "/Users/andreaardito/Desktop/lspd_894132/targeted_lead.xml"  # Percorso file XML
    output_file = "/Users/andreaardito/Desktop/lspd_894132/complete_websites.csv"  # Output CSV

    print("Parsing XML...")
    companies = parse_xml(input_file)  # Parsing XML iniziale

    # Configurazione del WebDriver Selenium
    service = Service()  # Imposta il percorso di ChromeDriver se necessario
    options = Options()
    options.add_argument("--headless")  # Esegui Chrome in background
    browser = webdriver.Chrome(service=service, options=options)

    results = []  # Lista per salvare i risultati
    print("Verifica e ricerca dei siti web...")

    # Loop per ciascuna azienda
    for company, homepage in companies:
        if homepage:  # Se il sito web è già presente
            print(f"Homepage già presente per {company}: {homepage}")
            results.append((company, homepage))
        else:  # Se manca la homepage, esegue la ricerca
            print(f"Ricerca sito web per: {company}")
            website = find_website(company)
            if website:
                print(f"Homepage trovata per {company}: {website}")
                results.append((company, website))
            else:
                print(f"Nessuna homepage trovata per {company}.")
                results.append((company, None))

            time.sleep(1)  # Evita di sovraccaricare Google Search con richieste troppo veloci

    browser.quit()  # Chiude il browser Chrome

    # Salvataggio dei risultati in CSV
    print("Salvataggio dei risultati...")
    with open(output_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Company Name", "Homepage"])
        writer.writerows(results)

    print(f"Completato! I risultati sono stati salvati in {output_file}.")

if __name__ == "__main__":
    main()
