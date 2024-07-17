import requests

import os
import csv
from shared import open_browser, load_page, close_driver


def scraped_company_urls(soup):
    
    # Find all <h3> elements and their subsequent <table> siblings
    h3_elements = soup.find_all('h3', class_='text-center')
    results = []

    for h3 in h3_elements:
        title = h3.get_text(strip=True)
        
        # Replace titles based on conditions
        if "names are no longer used on beer in production" in title:
            title = "Name is no longer used on beer in production"
        elif "Breweries who do not own a brewery" in title:
            title = "Do not own a brewery"
        elif "Breweries in production" in title:
            title = "In production"

        next_table = h3.find_next('table')
        if next_table:
            links = next_table.find_all('a', href=lambda href: href and href.startswith('http://www.quaffale.org.uk/php/brewery/'))
            for link in links:
                link_url = link['href']
                results.append({'status': title, 'link': link_url})

    return results
    

def write_to_csv(data, filename='results.csv'):
    file_exists = os.path.isfile(filename)

    # Read existing links to avoid duplicates
    existing_links = set()
    if file_exists:
        with open(filename, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader, None)  # Skip header if file is not empty
            existing_links = {row[1] for row in reader}  # Collect existing links

    # Write new rows
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        # Write header only if the file did not exist
        if not file_exists:
            writer.writerow(['Status', 'Link', 'Title', 'Address', 'Phone', 'Web', 'Email', 'Social Media', 'Ceremonial', 'Shire', 'Local Authority', 'Map','Image'])

        # Write new data, avoid duplicates
        for entry in data:
            if entry['link'] not in existing_links:
                writer.writerow([
                    entry.get('status', ''), 
                    entry['link'], 
                    entry.get('title', ''), 
                    entry.get('address', ''), 
                    entry.get('phone', ''), 
                    entry.get('web', ''), 
                    entry.get('email', ''), 
                    entry.get('social_media', ''), 
                    entry.get('ceremonial', ''), 
                    entry.get('shire', ''), 
                    entry.get('local_authority', ''), 
                    entry.get('map', ''), 
                    entry.get('image', '')
                ])

menus = [
    "a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z"
]

driver = open_browser()

for menu in menus:

    menu_url = "https://www.quaffale.org.uk/php/menu/"+menu
    soup = load_page(driver, menu_url, 'h3.text-center')
    scraped_company_urls_data = scraped_company_urls(soup)

    write_to_csv(scraped_company_urls_data)

close_driver(driver)