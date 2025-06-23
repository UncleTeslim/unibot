import requests
from bs4 import BeautifulSoup
from collections import deque
import time
from urllib.parse import urljoin, urlparse, urldefrag
import urllib.robotparser as robotparser
from playwright.sync_api import sync_playwright, Playwright
import os # For creating a directory for PDFs
# Optional: For better PDF text extraction, uncomment later
# from pypdf import PdfReader # pip install pypdf

# --- Helper Functions ---

def get_base_domain(url):
    """Extracts the base domain from a URL."""
    parsed_url = urlparse(url)
    return parsed_url.netloc

def can_fetch(rp, user_agent, url):
    """Checks if a URL can be fetched according to robots.txt."""
    if rp is None:
        return True # No robots.txt, assume allowed
    return rp.can_fetch(user_agent, url)

def normalize_url(url):
    """Removes fragment (#...) from a URL for consistent tracking."""
    return urldefrag(url).url

# --- Main Scraper Function ---

def scrape_university(start_url: str, output_text_file="university_data.txt",
                      output_pdf_urls_file="university_pdf_urls.txt",
                      max_pages: int = 500,
                      politeness_delay: float = 1.0):
    """
    Crawl a university website, extract text content, and collect PDF URLs.
    Handles dynamic content via Playwright and focuses on robust text extraction
    even with inconsistent HTML structures.
    """
    base_domain = get_base_domain(start_url)
    if not base_domain:
        print(f"Error: Invalid start URL provided: {start_url}")
        return

    rp = robotparser.RobotFileParser()
    robots_url = urljoin(start_url, '/robots.txt')
    try:
        rp.set_url(robots_url)
        rp.read()
        print(f"Loaded robots.txt from: {robots_url}")
    except Exception as e:
        print(f"Warning: Could not load robots.txt for {robots_url}: {e}. Proceeding without it.")
        rp = None

    to_visit = deque([normalize_url(start_url)])
    visited_html_urls = set()
    pdf_urls_found = set()

    page_count = 0
    user_agent = "Mozilla/5.0 (compatible; MyUniversityQAScraper/1.0; +https://yourwebsite.com/about-your-project)"

    print(f"\n--- Starting University Web Crawl ---")
    print(f"Start URL: {start_url}")
    print(f"Targeting Domain: {base_domain}")
    print(f"Max HTML Pages to Crawl: {max_pages}")
    print(f"Politeness Delay: {politeness_delay} seconds")
    print(f"Saving text to: {output_text_file}")
    print(f"Saving PDF URLs to: {output_pdf_urls_file}")
    print(f"-------------------------------------\n")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context(user_agent=user_agent, ignore_https_errors=True)
            page_playwright = context.new_page()

            with open(output_text_file, 'w', encoding='utf-8') as text_f:
                while to_visit and page_count < max_pages:
                    current_url = to_visit.popleft()
                    normalized_current_url = normalize_url(current_url)

                    if normalized_current_url in visited_html_urls:
                        continue

                    if get_base_domain(normalized_current_url) != base_domain:
                        visited_html_urls.add(normalized_current_url)
                        continue

                    if not can_fetch(rp, user_agent, normalized_current_url):
                        print(f"Skipping {normalized_current_url} due to robots.txt DISALLOW rule.")
                        visited_html_urls.add(normalized_current_url)
                        continue

                    print(f"Crawling ({page_count + 1}/{max_pages}): {normalized_current_url}")
                    visited_html_urls.add(normalized_current_url)

                    try:
                        page_playwright.goto(normalized_current_url, wait_until="domcontentloaded", timeout=60000)
                        response_text = page_playwright.content()
                        soup = BeautifulSoup(response_text, 'html.parser')

                        # --- Extract Title ---
                        page_title = "No Title"
                        title_tag = soup.find('title')
                        if title_tag:
                            page_title = title_tag.get_text(strip=True)

                        # --- Aggressive Noise Removal before content extraction ---
                        # These are common elements that often contain navigation, footers, etc.
                        # Decompose them to remove from the soup tree before extracting main text.
                        # You might need to customize this list heavily based on UWE's specific site.
                        elements_to_remove = [
                            # Common boilerplate
                            {'tag': 'nav'}, {'tag': 'footer'}, {'tag': 'header'},
                            {'tag': 'aside'}, {'tag': 'form'}, {'tag': 'style'}, {'tag': 'script'},
                            {'tag': 'noscript'}, {'tag': 'iframe'},
                            # Common IDs/Classes for non-content areas
                            {'class': 'sidebar'}, {'class': 'navigation'}, {'class': 'site-header'},
                            {'class': 'site-footer'}, {'class': 'menu'}, {'class': 'breadcrumb'},
                            {'class': 'meta'}, {'class': 'social-share'}, {'class': 'advertisement'},
                            {'class': 'cookie-banner'}, {'class': 'modal-dialog'},
                            {'id': 'navbar'}, {'id': 'footer'}, {'id': 'header'},
                            {'id': 'skip-to-content'}, {'id': 'sidebar'}, {'id': 'utility-nav'},
                            {'id': 'site-navigation'}, {'id': 'search-form'}, {'id': 'cookie-notice'},
                        ]

                        for item in elements_to_remove:
                            if 'tag' in item:
                                for tag_found in soup.find_all(item['tag']):
                                    tag_found.decompose()
                            elif 'class' in item:
                                for tag_found in soup.find_all(class_=item['class']):
                                    tag_found.decompose()
                            elif 'id' in item:
                                for tag_found in soup.find_all(id=item['id']):
                                    tag_found.decompose()

                        # --- Generic Content Extraction from the remaining body ---
                        page_text_elements = []
                        # Focus on common textual tags. Avoid too many 'div' or 'span' alone
                        # as they might be layout elements without semantic text.
                        for element in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'blockquote', 'td']):
                            text = element.get_text(separator=' ', strip=True)
                            if text and len(text) > 10: # Filter out very short or empty strings (e.g., empty <li>)
                                page_text_elements.append(text)

                        # Concatenate and clean up whitespace
                        full_page_content = "\n".join(page_text_elements)
                        full_page_content = os.linesep.join([s for s in full_page_content.splitlines() if s.strip()]) # Remove empty lines

                        # Write extracted data to the text file
                        text_f.write(f"--- URL: {normalized_current_url} ---\n")
                        text_f.write(f"--- Title: {page_title} ---\n")
                        text_f.write(full_page_content)
                        text_f.write("\n\n---\n\n") # Separator for different pages

                        page_count += 1

                        # --- Find new links ---
                        for link_tag in soup.find_all('a', href=True):
                            href = link_tag['href']
                            absolute_url = urljoin(normalized_current_url, href)
                            normalized_absolute_url = normalize_url(absolute_url)
                            parsed_link = urlparse(normalized_absolute_url)

                            # Ensure it's the same domain
                            if parsed_link.netloc == base_domain:
                                if normalized_absolute_url.endswith('.pdf'):
                                    pdf_urls_found.add(normalized_absolute_url)
                                elif not any(normalized_absolute_url.endswith(ext) for ext in ['.zip', '.doc', '.docx', '.jpg', '.jpeg', '.png', '.gif', '.mp4', '.mp3', '.avi', '.mov', '.webp']):
                                    if normalized_absolute_url not in visited_html_urls and normalized_absolute_url not in to_visit:
                                        to_visit.append(normalized_absolute_url)

                        # Be polite
                        time.sleep(politeness_delay)

                    except Exception as e:
                        print(f"Error processing {normalized_current_url}: {e}")

            browser.close()
    except Playwright as e:
        print(f"Playwright initialization error: {e}. Make sure 'playwright install' was run.")
        return
    except Exception as e:
        print(f"An unhandled error occurred during crawl: {e}")
        return

    print(f"\n--- Crawl Finished ---")
    print(f"Total HTML pages scraped: {page_count}")
    print(f"Total unique URLs considered (visited + failed + skipped): {len(visited_html_urls) + len(to_visit)}")
    print(f"Data saved to: {output_text_file}")

    # Save collected PDF URLs to a separate file
    with open(output_pdf_urls_file, 'w', encoding='utf-8') as pdf_f:
        for pdf_url in sorted(list(pdf_urls_found)):
            pdf_f.write(f"{pdf_url}\n")
    print(f"Collected {len(pdf_urls_found)} PDF URLs (saved to: {output_pdf_urls_file})")
    print(f"---------------------\n")

# --- Main Execution Block ---
if __name__ == "__main__":
    university_homepage = "https://www.uwe.ac.uk/"
    max_pages_to_crawl = 3000 # Set higher for more comprehensive crawl
    request_delay = 2.5

    output_html_content_file = "uwe_university_html_content.txt"
    output_pdf_links_file = "uwe_university_pdf_links.txt"

    scrape_university(
        start_url=university_homepage,
        output_text_file=output_html_content_file,
        output_pdf_urls_file=output_pdf_links_file,
        max_pages=max_pages_to_crawl,
        politeness_delay=request_delay
    )

    print("\n--- Next Steps ---")
    print(f"1. Review '{output_html_content_file}' for extracted text content. This is your primary RAG data.")
    print(f"2. Review '{output_pdf_links_file}' for collected PDF URLs.")
    print("3. **Crucial:** Implement a separate script to **download and extract text from the PDF URLs.** (This is often best done as a separate, robust process).")
    print("4. Further pre-process the extracted text (chunking, cleaning, metadata association) for your RAG system.")
    print("   - You'll want to break the long text files into smaller, semantically meaningful chunks.")
    print("   - Add the URL as metadata to each chunk for attribution.")
    print("   - Consider using NLTK or spaCy for more advanced text cleaning (e.g., removing boilerplate sentences).")