import requests
from bs4 import BeautifulSoup
import os
import argparse
import logging
from urllib.parse import urljoin
import time
import sys
import re

# ANSI color codes
class Colors:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'

def setup_logging(verbosity):
    """Configure logging based on verbosity level"""
    # File handler (no color)
    file_handler = logging.FileHandler('pdf_downloader.log')
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    
    # Console handler with colors for verbose mode
    class ColoredFormatter(logging.Formatter):
        def format(self, record):
            level_color = {
                'INFO': Colors.GREEN,
                'WARNING': Colors.YELLOW,
                'ERROR': Colors.RED,
                'CRITICAL': Colors.RED
            }.get(record.levelname, Colors.RESET)
            
            # Split timestamp from message
            timestamp = f"{Colors.CYAN}{self.formatTime(record, '%Y-%m-%d %H:%M:%S')}{Colors.RESET}"
            message = f"{level_color}{record.levelname} - {record.getMessage()}{Colors.RESET}"
            return f"{timestamp} - {message}"
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(ColoredFormatter())
    
    logger = logging.getLogger()
    logger.setLevel(logging.INFO if verbosity else logging.WARNING)
    logger.addHandler(file_handler)
    
    if verbosity:
        logger.addHandler(console_handler)

def get_date_from_row(link_element):
    """Extract date from the same row as the PDF link"""
    row = link_element.find_parent('tr') or link_element.find_parent('td') or link_element.find_parent()
    if not row:
        return None
        
    date_patterns = [
        r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
        r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
        r'\d{2}-\d{2}-\d{4}',  # MM-DD-YYYY
    ]
    
    text = row.get_text(strip=True)
    for pattern in date_patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0).replace('/', '-')
    return None

def download_pdfs_from_url(base_url, verbose=False, download_counter=0):
    """Download all PDFs from a given URL"""
    session = requests.Session()
    downloaded_count = 0
    error_count = 0
    
    try:
        response = session.get(base_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        records_section = soup.find(string="Accessing the Records")
        if not records_section:
            logging.warning(f"No 'Accessing the Records' section found in {base_url}")
            container = soup
        else:
            container = records_section.find_parent('div') or records_section.find_parent()
            if not container:
                logging.warning(f"No suitable container found, using full page for {base_url}")
                container = soup
                
        page_num = 1
        while True:
            if verbose:
                logging.info(f"Processing page {page_num} of {base_url}")
                
            pdf_links = container.find_all('a', href=lambda href: href and '.pdf' in href.lower())
            logging.info(f"Found {len(pdf_links)} potential PDF links on page {page_num}")
            
            if not pdf_links and verbose:
                logging.debug(f"HTML content sample: {str(container)[:500]}...")
                
            for link in pdf_links:
                pdf_url = urljoin(base_url, link['href'])
                base_filename = os.path.basename(pdf_url.split('?')[0])
                
                doc_date = get_date_from_row(link)
                date_str = f"_{doc_date}" if doc_date else ""
                
                download_counter += 1
                filename = f"{os.path.splitext(base_filename)[0]}{date_str}_{download_counter}.pdf"
                
                if os.path.exists(filename):
                    logging.info(f"Skipping {filename} - already exists")
                    continue
                
                try:
                    logging.info(f"Attempting to download: {pdf_url}")
                    pdf_response = session.get(pdf_url, stream=True, timeout=30)
                    pdf_response.raise_for_status()
                    
                    content_type = pdf_response.headers.get('content-type', '').lower()
                    if 'pdf' not in content_type:
                        logging.warning(f"Skipping {filename} - not a PDF (Content-Type: {content_type})")
                        continue
                        
                    with open(filename, 'wb') as f:
                        for chunk in pdf_response.iter_content(chunk_size=8192):
                            f.write(chunk)
                            
                    downloaded_count += 1
                    logging.info(f"Successfully downloaded: {filename}")
                    
                except requests.RequestException as e:
                    error_count += 1
                    logging.error(f"Failed to download {pdf_url}: {str(e)}")
                    
            next_button = soup.find('a', string='Next') or \
                         soup.find('a', string=lambda t: t and 'next' in t.lower()) or \
                         soup.find('a', {'class': lambda x: x and 'next' in x.lower()})
            if not next_button or not next_button.get('href'):
                logging.info(f"No more pages found after page {page_num}")
                break
                
            next_url = urljoin(base_url, next_button['href'])
            if next_url == base_url:
                logging.info(f"Next URL same as base URL, stopping pagination")
                break
                
            logging.info(f"Moving to next page: {next_url}")
            response = session.get(next_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            container = soup.find(string="Accessing the Records")
            if container:
                container = container.find_parent('div') or container.find_parent()
            else:
                container = soup
            page_num += 1
            
            time.sleep(1)
            
    except requests.RequestException as e:
        logging.error(f"Error accessing {base_url}: {str(e)}")
        error_count += 1
        
    return downloaded_count, error_count, download_counter

def main():
    parser = argparse.ArgumentParser(description='Download PDFs from URLs listed in url_list.txt')
    parser.add_argument('-v', '--verbose', action='store_true', help='Increase output verbosity')
    args = parser.parse_args()
    
    setup_logging(args.verbose)
    logging.info("Starting PDF download process")
    
    total_downloaded = 0
    total_errors = 0
    download_counter = 0
    
    if not os.path.exists('url_list.txt'):
        logging.error("url_list.txt not found in current directory")
        print("Error: url_list.txt not found")
        return
    
    with open('url_list.txt', 'r') as f:
        urls = [line.strip() for line in f if line.strip()]
    
    if not urls:
        logging.error("No URLs found in url_list.txt")
        print("Error: No URLs found in url_list.txt")
        return
    
    for url in urls:
        logging.info(f"Processing URL: {url}")
        downloaded, errors, download_counter = download -url, args.verbose, download_counter)
        total_downloaded += downloaded
        total_errors += errors
    
    logging.info(f"Download complete. Total files downloaded: {total_downloaded}")
    logging.info(f"Total errors encountered: {total_errors}")
    print(f"Download complete. Check pdf_downloader.log for details")
    print(f"Total files downloaded: {total_downloaded}")
    print(f"Total errors: {total_errors}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.critical(f"Critical error in main process: {str(e)}")
        print(f"Critical error occurred. Check pdf_downloader.log for details")
