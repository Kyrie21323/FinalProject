import requests
from bs4 import BeautifulSoup
import csv
import os
import urllib.parse
import time

def scrape_tmz():
    base_url = "https://www.tmz.com/search/?q="
    celebrities = [
        "Taylor Swift", "Kanye West", "MrBeast", "The Weeknd", "Justin Bieber",
        "Jake Paul", "Cardi B", "Drake", "P Diddy", "Rihanna", "Billie Eilish",
        "Will Smith", "Dwayne Johnson", "Elon Musk", "Kim Kardashian",
        "Mark Wahlberg", "Joe Rogan", "Chris Brown", "Lady Gaga", "Kai Cenat"
    ]
    
    articles = []
    
    for celebrity in celebrities:
        search_url = base_url + urllib.parse.quote(celebrity)
        response = requests.get(search_url)
        if response.status_code != 200:
            print(f"Failed to retrieve search results for {celebrity}")
            continue
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for articles in search results
        for item in soup.select('a.gridler__card-link'):
            title_tag = item.select_one('h4.gridler__card-title')
            title = title_tag.get_text(strip=True) if title_tag else "No title"
            
            link = item['href']
            if not link.startswith('http'):
                link = "https://www.tmz.com" + link

            # Fetch the body content of the article
            content = fetch_article_content(link)
            
            # Append the article data
            articles.append((title, link, celebrity, content))
            
            # Brief pause to avoid overwhelming the server
            time.sleep(1)
    
    return articles

def fetch_article_content(url):
    """Fetches and returns the main content of an article given its URL."""
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return "Failed to retrieve content"
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Locate paragraphs within the specified class for article body content
        content_div = soup.find(class_="canvas-block canvas-block-permalink canvas-text-block canvas-text-block-permalink canvas-text-block--default")
        content_paragraphs = content_div.find_all('p') if content_div else []
        content = " ".join(paragraph.get_text(strip=True) for paragraph in content_paragraphs)
        
        return content if content else "No content found"
    except Exception as e:
        print(f"Error fetching article content from {url}: {e}")
        return "Error retrieving content"

def save_to_csv(articles, filename="celebrity_scraped.csv"):
    save_path = os.path.join(os.getcwd(), filename)
    
    existing_titles = set()
    if os.path.exists(save_path):
        with open(save_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            existing_titles = {row[1].strip().lower() for row in reader}
            print(f"existing titles are", existing_titles)
    new_articles = [article for article in articles if article not in existing_titles]
    print(f"new articles are:",new_articles)
    #append only new articles

    if new_articles:
        try:
            with open(save_path, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
            for article in articles:
                writer.writerow(article)
            print(f"TMZ data appended to {save_path} with {len(new_articles)} new entries.")
        except OSError as e:
            print(f"Error saving data: {e}")
    else:
        print("No new articles to add.")

def main():
    articles = scrape_tmz()
    save_to_csv(articles)

if __name__ == "__main__":
    main()
