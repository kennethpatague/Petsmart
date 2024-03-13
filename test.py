from bs4 import BeautifulSoup
from selectolax.parser import HTMLParser
from rich import print
import requests
import json


headers = {
        'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
        'Referer': 'https://ustoy.com/',
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'sec-ch-ua-platform': '"Windows"',
    }
res = requests.get("https://www.petsmart.com/dog/beds-and-furniture/cuddler-beds/top-paw-chambray-cuddler-dog-bed-54303.html", headers=headers)
soup = BeautifulSoup(res.content, features="html.parser")

json_data = json.loads(soup.select_one("script[type='application/ld+json']").string)
# print(json_data)


availability = ''
if 'offers' in json_data and 'InStock' in json_data['offers']['availability']:
    availability = True
else:
    availability = False


product_info = {
    "Brand": json_data['brand'],
    "Title": json_data['name'],
    "UPC": json_data['gtin13'],
    "SKU": json_data['sku'],
    "Product URL": json_data['url'],
    "Image URL": json_data['image'],
    "Price": json_data['offers']['price'],
    "Availability": availability,
    "Review Count": json_data['aggregateRating']['reviewCount'],
    "Rating": json_data['aggregateRating']['ratingValue']
}
print(product_info)
