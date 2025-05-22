import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from collections import deque
import time

# CONFIGURATION
START_URLS = [
    "https://www.allrecipes.com/"
]
ALLOWED_DOMAIN = "allrecipes.com"
OUTPUT_FILE = r"C:\Users\Dell\Documents\recipes.txt"

visited = set()
recipes = {}

def is_valid_recipe_url(url):
    return (
        url and
        ALLOWED_DOMAIN in url and
        '/recipe/' in url and
        '?' not in url and
        '#' not in url
    )

def fetch_links(url):
    try:
        time.sleep(1)  # Be polite
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return []
        soup = BeautifulSoup(response.content, "html.parser")
        links = [a.get("href") for a in soup.find_all("a", href=True)]
        return links
    except Exception as e:
        print(f"❌ Error fetching {url}: {e}")
        return []

def extract_recipe_title_and_content(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return "Unknown Title", []

        soup = BeautifulSoup(response.content, "html.parser")
        title_tag = soup.find("h1")
        title = title_tag.get_text(strip=True) if title_tag else "No Title Found"

        paragraphs = soup.find_all('p')
        content_sections = []
        current_heading = "No Heading"

        for p in paragraphs:
            heading_tag = p.find_previous('h2')
            if heading_tag:
                heading_text = heading_tag.get_text(strip=True)
                if heading_text != current_heading:
                    current_heading = heading_text
                    content_sections.append(f"=== {current_heading} ===")

            text = p.get_text(strip=True)
            if text:
                sentences = [s.strip() for s in text.split('.') if s.strip()]
                for sentence in sentences:
                    content_sections.append(sentence + '.')
                content_sections.append("")

        return title, content_sections

    except Exception as e:
        return f"Failed to load ({e})", []

def crawl_recipes(start_urls, max_recipes):
    queue = deque(start_urls)

    while queue and len(recipes) < max_recipes:
        current_url = queue.popleft()
        if current_url in visited:
            continue
        visited.add(current_url)

        print(f"\n🔍 Crawling: {current_url}")
        links = fetch_links(current_url)

        for link in links:
            full_url = urljoin(current_url, link)
            if is_valid_recipe_url(full_url) and full_url not in recipes:
                title, content_sections = extract_recipe_title_and_content(full_url)
                recipes[full_url] = (title, content_sections)
                print(f"\n✅ {title} - {full_url}\n")

                # 💬 Print all paragraph lines to console
                for line in content_sections:
                    print(line)

                print("\n" + "=" * 80 + "\n")

                if len(recipes) >= max_recipes:
                    break
                queue.append(full_url)

    return recipes

def save_to_txt(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        for url, (title, content) in data.items():
            f.write(f"{title}\n{url}\n\n")
            for line in content:
                f.write(line + "\n")
            f.write("\n" + "="*50 + "\n\n")
    print(f"\n📝 Saved {len(data)} recipes to {filename}\n")

if __name__ == "__main__":
    while True:
        try:
            max_recipes = int(input("Enter the number of recipes to crawl: "))
            if max_recipes <= 0:
                print("Please enter a positive integer.")
                continue
            break
        except ValueError:
            print("Invalid input. Please enter a valid integer.")

    results = crawl_recipes(START_URLS, max_recipes)
    save_to_txt(results, OUTPUT_FILE)
