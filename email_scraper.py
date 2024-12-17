import csv
import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Funzione per leggere il file CSV con siti web verificati
def read_websites(file_path):
    """Legge il file CSV e restituisce una lista di tuple (nome azienda, homepage)."""
    websites = []
    with open(file_path, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            company_name = row["Company Name"]
            homepage = row["Homepage"]
            if homepage:
                websites.append((company_name, homepage))
    return websites

# Funzione per trovare un indirizzo email in una pagina HTML
def find_email_in_html(html):
    """Cerca indirizzi email nel contenuto HTML usando un'espressione regolare."""
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, html)
    return emails[0] if emails else None

# Funzione per dare priorità ai link contenenti 'contatti' o 'contact'
def prioritize_contact_links(links):
    """Ordina i link dando priorità a quelli che contengono 'contatti' o 'contact'."""
    contact_keywords = ["contatti", "contact"]
    prioritized = []
    others = []

    for link in links:
        if any(keyword in link.lower() for keyword in contact_keywords):
            prioritized.append(link)
        else:
            others.append(link)

    return prioritized + others  # Link prioritari prima, poi gli altri

# Funzione per effettuare il crawling e trovare l'email di contatto
def crawl_for_email(company_name, homepage, max_pages=15):
    """Effettua il crawling del sito web alla ricerca di un indirizzo email, dando priorità ai link 'contatti'."""
    visited_urls = set()  # Tiene traccia degli URL visitati
    pages_to_visit = [homepage]  # Lista delle pagine da visitare

    while pages_to_visit and len(visited_urls) < max_pages:
        url = pages_to_visit.pop(0)
        if url in visited_urls:
            continue
        
        try:
            print(f"Accesso a {url} per {company_name}...")
            response = requests.get(url, timeout=5)
            if response.status_code != 200:
                print(f"Errore {response.status_code} per {url}")
                continue

            # Analizza il contenuto HTML
            soup = BeautifulSoup(response.text, "html.parser")
            email = find_email_in_html(response.text)
            if email:
                print(f"Email trovata per {company_name}: {email}")
                return email  # Ritorna l'email trovata
            
            # Aggiungi nuovi link interni alla lista delle pagine da visitare
            visited_urls.add(url)
            all_links = [urljoin(url, link["href"]) for link in soup.find_all("a", href=True)]
            filtered_links = [link for link in all_links if link.startswith(homepage)]
            prioritized_links = prioritize_contact_links(filtered_links)

            pages_to_visit.extend([link for link in prioritized_links if link not in visited_urls])

        except Exception as e:
            print(f"Errore durante il crawling di {url}: {e}")
    
    print(f"Nessuna email trovata per {company_name}.")
    return None

# Funzione principale
def main():
    input_file = "/Users/andreaardito/Desktop/lspd_894132/websites_with_keywords.csv"  # File CSV di input
    output_file = "websites_with_emails.csv"  # File CSV di output

    print("Lettura del file CSV...")
    websites = read_websites(input_file)

    results = []  # Lista per salvare i risultati
    print("Inizio ricerca delle email...")
    
    for company_name, homepage in websites:
        email = crawl_for_email(company_name, homepage)
        results.append((company_name, homepage, email if email else "Nessuna email trovata"))

    # Salvataggio dei risultati in un nuovo file CSV
    print("Salvataggio dei risultati...")
    with open(output_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Company Name", "Homepage", "Email"])
        writer.writerows(results)

    print(f"Completato! I risultati sono stati salvati in {output_file}.")

if __name__ == "__main__":
    main()
