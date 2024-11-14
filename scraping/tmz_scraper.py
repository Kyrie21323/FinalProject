import requests
from bs4 import BeautifulSoup
import csv
import os
import urllib.parse

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
        for item in soup.select('.article__header'):
            # Find the anchor tag and check if it's present
            link_tag = item.find('a', class_='article__header-link')
            if link_tag and 'href' in link_tag.attrs:
                link = link_tag['href']
                if not link.startswith('http'):
                    link = "https://www.tmz.com" + link
            else:
                link = "No link available"
            
            # Extract the headline fragments
            celebrity_name_tag = item.select_one('.article__header--hf1.text-uppercase.h3')
            title_part1 = item.select_one('.article__header--hf2.text-uppercase.h1')
            title_part2 = item.select_one('.article__header--hf3.text-titlecase.h2')

            # Get text if present, else default to the celebrity name
            celebrity_name = celebrity_name_tag.get_text(strip=True) if celebrity_name_tag else celebrity
            title1 = title_part1.get_text(strip=True) if title_part1 else ""
            title2 = title_part2.get_text(strip=True) if title_part2 else ""
            
            # Combine the title parts with a space
            title = f"{title1} {title2}".strip()

            # Fetch the article content
            content = fetch_article_content(link) if link != "No link available" else "Content not available"
            
            # Add to the articles list
            articles.append((celebrity_name, title, link, content))
    
    return articles

def fetch_article_content(url):
    """Fetches and returns the main content of an article given its URL."""
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return "Failed to retrieve content"
        
        soup = BeautifulSoup(response.content, 'html.parser')
        # Find the content of the article (assuming it's within a specific class)
        content_paragraphs = soup.select('.article__content p')
        content = " ".join(paragraph.get_text(strip=True) for paragraph in content_paragraphs)
        return content if content else "No content found"
    except Exception as e:
        print(f"Error fetching article content from {url}: {e}")
        return "Error retrieving content"

def save_to_csv(articles, filename="celebrity_scraped.csv"):
    # Define the CSV path
    save_path = os.path.join(os.getcwd(), filename)
    
    # Load existing titles to avoid duplicates
    existing_titles = set()
    if os.path.exists(save_path):
        with open(save_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            # Add existing article titles to the set for duplicate checking
            existing_titles = {row[1].strip().lower() for row in reader}
            print("Existing titles loaded.")

    # Filter new articles that are not already in the CSV
    new_articles = [article for article in articles if article[1].strip().lower() not in existing_titles]
    print("New articles:", new_articles)

    # Append only new articles to the CSV
    if new_articles:
        try:
            with open(save_path, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                # Append each new article row with article content as the comment
                for article in new_articles:
                    writer.writerow(article)
            print(f"TMZ data appended to {save_path} with {len(new_articles)} new entries.")
        except OSError as e:
            print(f"Error saving data: {e}")
    else:
        print("No new articles to add.")

def main():
    articles = scrape_tmz()
    if articles:
        save_to_csv(articles)

if __name__ == "__main__":
    main()
