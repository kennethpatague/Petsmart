from bs4 import BeautifulSoup
from rich import print
from concurrent.futures import ThreadPoolExecutor
import requests
import json
import os
import csv



headers = {
        'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
        'Referer': 'https://ustoy.com/',
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'sec-ch-ua-platform': '"Windows"',
    }


def get_products():
    sitemaps = ["https://www.petsmart.com/sitemap_0.xml",
                "https://www.petsmart.com/sitemap_1.xml",
                "https://www.petsmart.com/sitemap_2.xml",
                "https://www.petsmart.com/sitemap_3.xml",]
    
    product_links = []
    try:
        for sitemap in sitemaps:
            res = requests.get(sitemap)
            res.raise_for_status()
            soup = BeautifulSoup(res.content, features = "xml")
            loc_tags = soup.find_all("loc")
            print(f"Getting product links from {sitemap} - ({len(loc_tags)}) products")

            for loc in loc_tags:
                if loc not in product_links:
                    product_links.append(loc.text)
    except Exception as e:
        print("Error: ", e)
    return product_links


def scraped_data(product_link):
    parsed_products = []
    print(f"Scraping {product_link}")
    res = requests.get(product_link, headers=headers)
    res.raise_for_status()
    soup = BeautifulSoup(res.content, features="html.parser")

    parse_js = soup.select("script[type='application/ld+json']")

    if parse_js:
        for js in parse_js:
            parse_js = json.loads(js.string)
            availability = ''
            if 'offers' in parse_js and 'InStock' in parse_js['offers']['availability']:
                availability = True
            else:
                availability = False
            
            product_info = {
            "Brand": parse_js['brand'],
            "Title": parse_js['name'],
            "UPC": parse_js['gtin13'],
            "SKU": parse_js['sku'],
            "Product URL": parse_js['url'],
            "Image URL": parse_js['image'],
            "Price": "$" + parse_js['offers']['price'],
            "Availability": availability,
            "Review Count": parse_js['aggregateRating']['reviewCount'],
            "Rating": parse_js['aggregateRating']['ratingValue']
            }
            parsed_products.append(product_info)
    return parsed_products


def write_to_csv(parsed_products):
    if not parsed_products:
        print("No product found")
        return
    
    with open('petsmart.csv', 'a', encoding='utf-8', newline='') as csvfile:
        fieldnames = ["Brand", "Title", "UPC", "SKU", "Product URL", "Image URL", "Price", "Availability", "Review Count", "Rating"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if csvfile.tell() == 0:
            writer.writeheader()

        for product in parsed_products:
            writer.writerow(product)

        csvfile.flush()


def scrape_and_write(url):
    product_data = scraped_data(url)
    write_to_csv(product_data)


def main():

    try:
        urls = get_products()
        file_path = os.path.dirname(os.path.realpath(__file__)) + "\\petsmart.csv"
        if os.path.exists(file_path):
            os.remove(file_path)

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(scrape_and_write, url) for url in urls]
            for future in futures:
                try:
                    future.result()
                except KeyboardInterrupt:
                    print("KeyboardInterrupt. Exiting ...")
                    executor.shutdown(wait=False)
                    os._exit(0)
    except Exception as e:
        print("An error occured ", e)
        os._exit(1)


if __name__ == '__main__':
    main()