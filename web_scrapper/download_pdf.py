import requests
import os
import time
from urllib.parse import urlparse, unquote # unquote to handle URL-encoded characters in filenames
import re # For sanitizing filenames

def sanitize_filename(url: str, default_name: str = "downloaded_pdf") -> str:
    """
    Generates a safe filename from a URL or its path, ensuring it's valid for filesystems.
    Removes potentially problematic characters and ensures a .pdf extension.
    """
    parsed_url = urlparse(url)
    # Get path from URL, unquote it, then get just the base filename part
    filename_from_path = os.path.basename(unquote(parsed_url.path))

    # Remove query parameters and fragments
    filename_from_path = filename_from_path.split('?')[0].split('#')[0]

    if not filename_from_path:
        # Fallback if path is empty or just a slash
        filename_from_path = default_name

    # Remove invalid characters for filenames (e.g., / \ : * ? " < > |)
    safe_filename = re.sub(r'[\\/:*?"<>|]', '', filename_from_path)
    # Also remove leading/trailing spaces or dots
    safe_filename = safe_filename.strip(' .')

    # Ensure it ends with .pdf
    if not safe_filename.lower().endswith('.pdf'):
        safe_filename += '.pdf'

    return safe_filename

def download_pdfs_from_urls(
    pdf_urls_file: str,
    output_directory: str = "downloaded_pdfs",
    politeness_delay: float = 0.5,
    max_retries: int = 3,
    retry_delay: float = 5.0
):
    """
    Downloads PDF files from a list of URLs to a local directory.

    Args:
        pdf_urls_file (str): Path to the text file containing PDF URLs, one per line.
        output_directory (str): The directory where PDFs will be saved.
        politeness_delay (float): Delay in seconds between each PDF download.
        max_retries (int): Maximum number of retries for failed downloads.
        retry_delay (float): Delay in seconds before retrying a failed download.
    """
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
        print(f"Created output directory: {output_directory}")

    try:
        with open(pdf_urls_file, 'r', encoding='utf-8') as f:
            pdf_urls = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: PDF URLs file '{pdf_urls_file}' not found.")
        return
    except Exception as e:
        print(f"Error reading PDF URLs file: {e}")
        return

    if not pdf_urls:
        print("No PDF URLs found in the file. Exiting.")
        return

    print(f"\n--- Starting PDF Download Process ---")
    print(f"Found {len(pdf_urls)} PDF URLs to download.")
    print(f"Saving to: {output_directory}")
    print(f"Politeness Delay: {politeness_delay} seconds per PDF")
    print(f"-------------------------------------\n")

    successful_downloads = 0
    failed_downloads = []

    for i, pdf_url in enumerate(pdf_urls):
        print(f"[{i+1}/{len(pdf_urls)}] Downloading: {pdf_url}")
        retries = 0
        while retries <= max_retries:
            try:
                # Sanitize filename to prevent issues with OS paths
                filename = sanitize_filename(pdf_url, default_name=f"downloaded_pdf_{i+1}")
                filepath = os.path.join(output_directory, filename)

                # Add a unique suffix if file already exists to prevent overwriting
                base_name, ext = os.path.splitext(filepath)
                counter = 1
                while os.path.exists(filepath):
                    filepath = f"{base_name}_{counter}{ext}"
                    counter += 1

                headers = {'User-Agent': 'Mozilla/5.0 (compatible; MyPDFDownloader/1.0)'}
                response = requests.get(pdf_url, stream=True, timeout=30, headers=headers)
                response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)

                # Check if the content type is actually PDF
                content_type = response.headers.get('Content-Type', '')
                if 'application/pdf' not in content_type and 'octet-stream' not in content_type:
                    print(f"  Warning: {pdf_url} is not a PDF (Content-Type: {content_type}). Skipping.")
                    failed_downloads.append({'url': pdf_url, 'reason': f"Not a PDF ({content_type})"})
                    break # Break from retry loop, move to next URL

                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk: # Filter out keep-alive new chunks
                            f.write(chunk)
                print(f"  Saved: {filepath}")
                successful_downloads += 1
                break # Break from retry loop on success

            except requests.exceptions.Timeout:
                print(f"  Timeout error for {pdf_url}. Retrying ({retries+1}/{max_retries})...")
            except requests.exceptions.ConnectionError:
                print(f"  Connection error for {pdf_url}. Retrying ({retries+1}/{max_retries})...")
            except requests.exceptions.HTTPError as e:
                print(f"  HTTP Error {e.response.status_code} for {pdf_url}. Retrying ({retries+1}/{max_retries})...")
                if e.response.status_code == 404: # No point retrying a 404
                    print(f"  {pdf_url} returned 404 Not Found. Skipping retries.")
                    failed_downloads.append({'url': pdf_url, 'reason': '404 Not Found'})
                    break
            except Exception as e:
                print(f"  An unexpected error occurred for {pdf_url}: {e}. Retrying ({retries+1}/{max_retries})...")

            retries += 1
            if retries <= max_retries:
                time.sleep(retry_delay) # Wait before retrying
        else: # This block runs if the while loop completes without a 'break' (i.e., all retries failed)
            print(f"  Failed to download {pdf_url} after {max_retries} retries.")
            failed_downloads.append({'url': pdf_url, 'reason': 'Max retries exceeded'})

        time.sleep(politeness_delay) # Politeness delay between URLs

    print(f"\n--- PDF Download Process Finished ---")
    print(f"Successful downloads: {successful_downloads}")
    print(f"Failed downloads: {len(failed_downloads)}")
    if failed_downloads:
        print("\n--- Failed Download Details ---")
        for failure in failed_downloads:
            print(f"URL: {failure['url']} - Reason: {failure['reason']}")
    print(f"-------------------------------------\n")


# --- How to run it ---
if __name__ == "__main__":
    # The file generated by your previous web scraper
    pdf_links_file = "uwe_university_pdf_links.txt"
    # Directory to save the downloaded PDFs
    pdf_output_folder = "../data"

    download_pdfs_from_urls(
        pdf_links_file,
        output_directory=pdf_output_folder,
        politeness_delay=1.0, # Be polite! Adjust based on server
        max_retries=5,       # Increase retries for potentially flaky connections
        retry_delay=10.0      # Longer delay for retries
    )