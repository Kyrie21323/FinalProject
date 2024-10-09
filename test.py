import requests
from bs4 import BeautifulSoup
import csv

def scrape_tmz():
    url = "https://www.tmz.com/"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    articles = []
    for item in soup.select('.article__title'):  # Adjust the selector to match the title elements
        title = item.get_text(strip=True)
        link = item.find('a')['href']
        celebrity_name = item.find_next_sibling('a').get_text(strip=True) if item.find_next_sibling('a') else "Unknown"
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
    save_to_csv(articles)

if __name__ == "__main__":
    main()
