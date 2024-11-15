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
        
        # Counter to limit the articles to the first 10 for each celebrity
        count = 0

        # Look for articles in search results
        for item in soup.select('a.gridler__card-link.gridler__card-link--default.js-track-link.js-click-article'):
            if count >= 10:
                break  # Stop after the first 10 articles

            # Extract the title within the link
            title_tag = item.select_one('h4.gridler__card-title.gridler__card-title--default')
            title = title_tag.get_text(strip=True) if title_tag else "No title"
            
            # Get the link from the 'href' attribute
            link = item['href']
            if not link.startswith('http'):
                link = "https://www.tmz.com" + link

            print(f"Celebrity: {celebrity}, Title: {title}, Link: {link}")  # Debugging print
            
            # Fetch the body content of the article
            content = fetch_article_content(link)
            print(f"Content for {title}: {content[:100]}...")  # Preview content for debugging
            
            # Append the article data with the celebrity name
            articles.append((celebrity, title, link, content))
            
            count += 1  # Increment the count for each article processed
            time.sleep(1)  # Brief pause to avoid overwhelming the server
    
    return articles

def fetch_article_content(url):
    """Fetches and returns the main content of an article given its URL."""
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to retrieve content from {url}")
            return "Failed to retrieve content"
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Locate the section with the article content by the specified attributes
        content_section = soup.find('section', id=lambda x: x and x.startswith("cb-"), attrs={'data-context': '{"section":"permalink","name":"text_block"}'})
        if not content_section:
            print(f"Content section not found for {url}")
            return "Content section not found"
        
        # Extract the text within <p> tags inside the section
        content_paragraphs = content_section.find_all('p')
        content = " ".join(paragraph.get_text(strip=True) for paragraph in content_paragraphs)
        
        return content if content else "No content found"
    except Exception as e:
        print(f"Error fetching article content from {url}: {e}")
        return "Error retrieving content"

def save_to_csv(articles, filename="celebrity_scraped.csv"):
    save_path = os.path.join(os.getcwd(), filename)
    
    # Load existing titles to avoid duplicates
    existing_titles = set()
    if os.path.exists(save_path):
        with open(save_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            existing_titles = {row[1].strip().lower() for row in reader}
            print("Existing titles loaded:", existing_titles)
    
    # Filter new articles based on titles not in existing_titles
    new_articles = [article for article in articles if article[1].strip().lower() not in existing_titles]
    print("New articles:", new_articles)
    
    # Append only new articles to the CSV
    if new_articles:
        try:
            with open(save_path, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                for article in new_articles:
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
