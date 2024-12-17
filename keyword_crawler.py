import csv
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Funzione per leggere il file CSV e ottenere la lista di siti web
def read_websites(file_path):
    """Legge il file CSV e restituisce una lista di tuple (nome azienda, homepage)."""
    websites = []
    with open(file_path, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            company_name = row["Company Name"]
            homepage = row["Homepage"]
            if homepage:  # Aggiungi solo i siti con URL validi
                # Assicurati che l'URL abbia il prefisso https://
                if not homepage.startswith("http"):
                    homepage = "https://" + homepage
                websites.append((company_name, homepage))
    return websites

# Funzione per effettuare il crawling di un sito
def crawl_website(company_name, homepage, keywords, max_pages=5):
    """Crawla un sito web, cercando parole chiave nell'HTML fino a un massimo di pagine."""
    visited_urls = set()  # Tiene traccia degli URL visitati
    pages_to_visit = [homepage]  # Lista di pagine da visitare
    
    while pages_to_visit and len(visited_urls) < max_pages:
        url = pages_to_visit.pop(0)
        if url in visited_urls:
            continue
        
        try:
            print(f"Accesso a {url}...")
            response = requests.get(url, timeout=5)  # Scarica la pagina HTML
            if response.status_code != 200:
                print(f"Errore {response.status_code} per {url}")
                continue

            # Analizza il contenuto HTML
            soup = BeautifulSoup(response.text, "html.parser")
            text = soup.get_text().lower()

            # Cerca le parole chiave nel testo
            if any(keyword in text for keyword in keywords):
                print(f"Parola chiave trovata in {url} per {company_name}")
                return (company_name, homepage)  # Ritorna risultato positivo
            
            # Aggiungi nuovi link alla lista di pagine da visitare
            visited_urls.add(url)
            for link in soup.find_all("a", href=True):
                absolute_url = urljoin(url, link["href"])
                if absolute_url not in visited_urls and absolute_url.startswith(homepage):
                    pages_to_visit.append(absolute_url)

        except Exception as e:
            print(f"Errore durante il crawling di {url}: {e}")
    
    return None  # Nessuna parola chiave trovata

# Funzione principale
def main():
    input_file = "/Users/andreaardito/Desktop/lspd_894132/complete_websites.csv"  # Percorso del file CSV in input
    output_file = "/Users/andreaardito/Desktop/lspd_894132/websites_with_keywords.csv"  # File CSV di output
    keywords = ['pannello solare', 'solare', 'fotovoltaico', 'pannelli fotovoltaici', 'fotovoltaici']

    print("Lettura del file CSV...")
    websites = read_websites(input_file)
    
    results = []  # Lista per salvare i risultati
    print("Inizio crawling dei siti web...")
    
    for company_name, homepage in websites:
        print(f"Verifica per {company_name}: {homepage}")
        result = crawl_website(company_name, homepage, keywords)
        if result:
            results.append(result)  # Aggiungi risultato positivo
    
    # Salvataggio dei risultati in un nuovo file CSV
    print("Salvataggio dei risultati...")
    with open(output_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Company Name", "Homepage"])
        writer.writerows(results)

    print(f"Completato! I risultati sono stati salvati in {output_file}.")

if __name__ == "__main__":
    main()
