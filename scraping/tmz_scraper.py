import requests
from bs4 import BeautifulSoup
import csv
import os

def scrape_tmz():
    url = "https://www.tmz.com/"
    response = requests.get(url)
    if response.status_code != 200:
        print("Failed to retrieve the webpage")
        return []
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    articles = []
    # Look for all article headers
    for item in soup.select('.article__header'):
        # Find the anchor tag and check if it's present
        link_tag = item.find('a', class_='article__header-link')
        if link_tag and 'href' in link_tag.attrs:
            link = link_tag['href']
            if not link.startswith('http'):
                link = url + link  # Prepend base URL if the link is relative
        else:
            link = "No link available"

        # Extract different headline fragments (celebrity name, title parts)
        celebrity_name_tag = item.select_one('.article__header--hf1.text-uppercase.h3')
        title_part1 = item.select_one('.article__header--hf2.text-uppercase.h1')
        title_part2 = item.select_one('.article__header--hf3.text-titlecase.h2')

        # Get the text if present, or use a default value
        celebrity_name = celebrity_name_tag.get_text(strip=True) if celebrity_name_tag else "Unknown"
        title1 = title_part1.get_text(strip=True) if title_part1 else ""
        title2 = title_part2.get_text(strip=True) if title_part2 else ""
        
        # Combine the title parts with a space between them
        title = f"{title1} {title2}".strip()
        
        # Add to the articles list
        articles.append((celebrity_name, title, link))
    
    return articles

def save_to_csv(articles, filename="celebrity_scraped.csv"):
    # Check if the current working directory is writable
    try:
        save_path = os.path.join(os.getcwd(), filename)
        with open(save_path, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            #append each article row with a null comment
            for article in articles:
                writer.writerow(article)
        print(f"TMZ data appended to {save_path}")
    except OSError as e:
        print(f"Error saving data: {e}")

def main():
    articles = scrape_tmz()
    if articles:
        save_to_csv(articles)

if __name__ == "__main__":
    main()
