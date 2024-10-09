import requests
from bs4 import BeautifulSoup
import csv

def scrape_tmz():
    url = "https://www.tmz.com/"
    response = requests.get(url)
    if response.status_code != 200:
        print("Failed to retrieve the webpage")
        return []
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    articles = []
    for item in soup.select('.article__header--hf2, .article__header--hf3.text-titlecase.h2.text-uppercase.h1'):
        title = item.get_text(strip=True)
        link = item.find('a')['href']
        if not link.startswith('http'):
            link = url + link  # Prepend base URL if the link is relative
        celebrity_name_tag = item.find_previous_sibling(class_='article__header--hf1.text-uppercase.h3')
        celebrity_name = celebrity_name_tag.get_text(strip=True) if celebrity_name_tag else "Unknown"
        articles.append((title, link, celebrity_name))
    
    return articles

def save_to_csv(articles, filename="tmz_headlines.csv"):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Title", "Link", "Celebrity Name"])
        writer.writerows(articles)
    print(f"Data saved to {filename}")

def main():
    articles = scrape_tmz()
    if articles:
        save_to_csv(articles)

if __name__ == "__main__":
    main()
