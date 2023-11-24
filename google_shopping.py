# For csv file handling
import csv

# For sending HTTP Request
import requests
# For parsing the response
from lxml import html


# Defining proxies
proxies = {
	# "http": "http://<host>:<port>",
	# "https": "http://<host>:<port>"
}

# Defining the HTTP headers for the request
headers = {
    "authority": "www.google.com",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,a\
        pplication/signed-exchange;v=b3;q=0.7",
    "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
    "referer": "https://shopping.google.com/",
    "sec-ch-ua": '"Chromium";v="110", "Not A(Brand";v="24", "Google Chrome";v="110"',
    "sec-ch-ua-arch": '"x86"',
    "sec-ch-ua-bitness": '"64"',
    "sec-ch-ua-full-version": '"110.0.5481.177"',
    "sec-ch-ua-full-version-list": '"Chromium";v="110.0.5481.177", "Not A(Brand";v="24.0.0.0", "Google Chrome";v="\
        110.0.5481.177"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-model": '""',
    "sec-ch-ua-platform": '"Linux"',
    "sec-ch-ua-platform-version": '"5.14.0"',
    "sec-ch-ua-wow64": "?0",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-site",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari\
        /537.36",
}


def save_as_csv(data: list):
    """
    The function that used to save
    the data as as csv file

    Args:
        data (list): data as list of dictionary
    """

    # Column(field) names for the csv file
    fieldnames = ["title", "image_url", "rating", "website", "item_price", "url"]

    # Opening an csv file to save the data
    with open("outputs.csv", mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        # Writing the headers(Column name)
        writer.writeheader()
        # Iterating through each product data
        for row in data:
            # Writing the data in a row
            writer.writerow(row)

def parse_listing_page(input_search_term: str):
    """
    This function will generate the listing page url from
    the input search keyword, Send request to it and extract
    product URLs from the response.

    Args:
        input_search_term (string): The seach keyword that we want
                                    to search

    Returns:
        list: List of extracted product urls
    """

    # Generating the listing page URL
    url = f"https://www.google.com/search?q={input_search_term}&safe=off&tbm=shop"

    # Sending request to the URL
    response = requests.get(url=url, headers=headers, proxies=proxies)

    # Parsing the response
    tree = html.fromstring(response.content)

    # Extracting product URLs
    product_urls = tree.xpath('//a[@class="xCpuod"]/@href')
    return product_urls


def parse_product_page(product_urls: list):
    """
    This function will accept a list of input URLs,
    iterate through each of them, Send request to each
    URL, store the data in a list and return back

    Args:
        product_urls (list): List of product URLs

    Returns:
        list: data as list of dictionary
    """

    # Initializing an empty list to save the extracted data
    data = []

    # Iterating through each product URL
    for product_url in product_urls:
        # Generating the product URL
        url = f"https://www.google.com{product_url}"

        # Sending the request
        response = requests.get(url=url, headers=headers, proxies=proxies)

        # Parsing the response
        tree = html.fromstring(response.content)

        # Extracting title and image url
        title = tree.xpath("//span[contains(@class, 't__title')]/text()")
        image_url = tree.xpath(
            "//div[@id='sg-product__pdp-container']//img[contains(@alt, 'View product image #1')]/@src"
        )
        if not image_url:
            image_url = tree.xpath(
                "//div[@id='sg-product__pdp-container']//div[contains(@class, 'main-image')]/img/@src"
            )

        # Extracting the price comparison table
        price_table = tree.xpath(
            "//table[contains(@id, 'online-sellers-grid')]/tbody/tr"
        )

        # Extracting rating
        rating = tree.xpath(
            '//a[@href="#reviews"]/div[contains(@aria-label, "out of")]/@aria-label'
        )

        # Iterating through each row
        for row in price_table:
            # Extracting the website name
            website = row.xpath("./td[1]//a/text()")
            if not website:
                continue

            # Extracting the price on that website
            item_price = row.xpath("./td[3]/span/text()")
            item_price = item_price[0] if item_price else None

            # Creating a dictionary of data and appending to the list
            data_to_save = {
                "title": title[0] if title else None,
                "image_url": image_url[0] if image_url else None,
                "rating": rating[0] if rating else None,
                "website": website[0] if website else None,
                "item_price": item_price,
                "url": url,
            }
            data.append(data_to_save)
    return data


if __name__ == "__main__":
    input_search_term = "laptop"
    product_urls = parse_listing_page(input_search_term)
    data = parse_product_page(product_urls)
    save_as_csv(data)
