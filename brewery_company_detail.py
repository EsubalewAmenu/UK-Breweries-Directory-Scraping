import os
import csv
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from shared import open_browser, load_page, close_driver

def scraped_company_data(soup, base_url):
    
    try:
        title = soup.find('h2', class_='text-secondary text-center font-weight-bold').text.strip()
    except AttributeError:
        title = None
    
    try:
        address = soup.find('th', text='Address').find_next('td').get_text(separator='\n', strip=True)
    except AttributeError:
        address = None

    try:
        phone = soup.find('th', text='Phone').find_next('td').text.strip()
    except AttributeError:
        phone = None

    try:
        web = soup.find('th', text='Web').find_next('a')['href']
    except (AttributeError, TypeError):
        web = None

    try:
        email = soup.find('th', text='e-mail').find_next('a').text.strip().replace(' -AT- ', '@')
    except AttributeError:
        email = None

    try:
        social_media_row = soup.find('th', text='Social Media').find_parent('tr')
        social_media_links = [a['href'] for a in social_media_row.find_all('a')]
    except AttributeError:
        social_media_links = None

    try:
        ceremonial = soup.find('th', text='County (see footnote)').find_next('a').text.strip()
    except AttributeError:
        ceremonial = None

    try:
        shire = soup.find('th', text='County (see footnote)').find_next('a').find_next('a').text.strip()
    except AttributeError:
        shire = None

    try:
        local_authority = soup.find('th', text='County (see footnote)').find_next('a').find_next('a').find_next('a').text.strip()
    except AttributeError:
        local_authority = None

    try:
        map_link = soup.find('a', text='Map')['href']
    except (AttributeError, TypeError):
        map_link = None

    try:
        image = soup.find('img', class_='img-fluid rounded mx-auto d-block')['src']
        image_url = urljoin(base_url, image)
    except (AttributeError, TypeError):
        image_url = None

    return {
        'title': title,
        'address': address,
        'phone': phone,
        'web': web,
        'email': email,
        'social_media_links': social_media_links,
        'ceremonial': ceremonial,
        'shire': shire,
        'local_authority': local_authority,
        'map_link': map_link,
        'image': image_url
    }
    
def read_and_process_csv(filename='results.csv'):
    with open(filename, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        headers = next(reader)  # Read the header
        rows = list(reader)  # Read the remaining rows

    driver = open_browser()

    updated_rows = []
    for row in rows:
        # Skip empty rows
        if not row or len(row) < 3:
            updated_rows.append(row)
            continue
        
        title = row[2]
        link = row[1]
        print("Scraping ", title, "started!")
        
        # Check if the Title column is empty
        if not title:
            # Call the scraping function
            soup = load_page(driver, link, 'h2.text-secondary.text-center.font-weight-bold')
            full_scraped_data = scraped_company_data(soup, link)

            # Update the row with the scraped data
            row[2] = full_scraped_data.get('title', '')
            row[3] = full_scraped_data.get('address', '')
            row[4] = full_scraped_data.get('phone', '')
            row[5] = full_scraped_data.get('web', '')
            row[6] = full_scraped_data.get('email', '')
            
            social_media_links = full_scraped_data.get('social_media_links', [])
            if isinstance(social_media_links, list):
                row[7] = ', '.join(social_media_links)
            else:
                row[7] = ''
            
            row[8] = full_scraped_data.get('ceremonial', '')
            row[9] = full_scraped_data.get('shire', '')
            row[10] = full_scraped_data.get('local_authority', '')
            row[11] = full_scraped_data.get('map_link', '')
            row[12] = full_scraped_data.get('image', '')
        
        updated_rows.append(row)

    close_driver(driver)

    # Write the updated rows back to the CSV file
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(updated_rows)

read_and_process_csv()
