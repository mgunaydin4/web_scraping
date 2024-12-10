# Kütüphanelerin import edilmesi
from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import re

# Chrome options tanımlanması
options = webdriver.ChromeOptions()

# Tam ekran özelliği
options.add_argument('--start.maximized')

# Chrome tarayıcısı oluşturma
driver = webdriver.Chrome(options)

# Anasayfanın açılması
SLEEP_TIME = 2

driver.get('https://books.toscrape.com/')
time.sleep(SLEEP_TIME)

# Travel ile Nonfiction kategori sayfalarının linklerini tutan XPath sorgusu
category_elements_xpath = "//a[contains(text(),'Travel') or contains(text(),'Nonfiction')]"

# Kategori detay linklerinin kazınması
category_elements = driver.find_elements(By.XPATH, category_elements_xpath)

category_urls = [element.get_attribute('href') for element in category_elements]
print(category_urls)

# Herhangi bir detay sayfasına gidip o sayfadaki kitapların detay linkini tutan elementleri yakalayan XPath sorgusu
driver.get(category_urls[0])
time.sleep(SLEEP_TIME)
book_elements_xpath = "//div[@class='image_container']//a"

# Driver ile XPath kullanarak elementleri ve detay linklerinin yakalanması
book_elements = driver.find_elements(By.XPATH,book_elements_xpath)
book_urls = [element.get_attribute('href') for element in book_elements]
print(book_urls)
print(len(book_urls))

# Pagination için linki manipüle etme
MAX_PAGINATION = 3
url = category_urls[1]
book_urls = []
for i in range(1,MAX_PAGINATION):
    update_url = url if i == 1 else url.replace("index", f"page-{i}")
    driver.get(update_url)
    book_elements = driver.find_elements(By.XPATH, book_elements_xpath)
    if not book_elements:
        break
    temp_urls = [element.get_attribute('href') for element in book_elements]
    book_urls.extend(temp_urls)

print(book_urls)
print(len(book_urls))

# Herhangi bir ürünün detay sayfasına gidip class attribute'ı content olan div elementini yakalama
driver.get(book_urls[0])
time.sleep(SLEEP_TIME)
content_div = driver.find_elements(By.XPATH, "//div[@class='content']")

# Yakaladığımız div in html'ini inner_html değişkenine atama
inner_html = content_div[0].get_attribute('innerHTML')

# inner_html ile soup objesi oluşturma
soup = BeautifulSoup(inner_html, "html.parser")

# Kitap Adı
name_elem = soup.find("h1")
book_name = name_elem.text

# Kitap Fiyatı
price_elem = soup.find("p", attrs={"class": "price_color"})
book_price = price_elem.text

# Kitap Yıldız Sayısı
regex = re.compile("^star-rating")
star_elem = soup.find("p", attrs={"class": regex})
print(star_elem)
book_star_count = star_elem["class"][-1]

# Kitap Açıklaması
desc_elem = soup.find("div", attrs={"id": "product_description"}).find_next_sibling()
book_desc = desc_elem.text

# Product Information Başlığı altında kalan tablodaki bilgiler
product_info = {}
table_rows = soup.find("table").find_all("tr")
for row in table_rows:
    key = row.find("th").text
    value = row.find("td").text
    product_info[key] = value

####################################
# Tüm Sürecin Fonksiyonlaştırılması
####################################
from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import re

def get_book_detail(driver, url):
    """Gets book data from given book detail page url"""
    driver.get(url)
    time.sleep(SLEEP_TIME)
    content_div = driver.find_elements(By.XPATH, "//div[@class='content']")

    inner_html = content_div[0].get_attribute('innerHTML')

    soup = BeautifulSoup(inner_html, "html.parser")

    name_elem = soup.find("h1")
    book_name = name_elem.text

    price_elem = soup.find("p", attrs={"class": "price_color"})
    book_price = price_elem.text

    regex = re.compile("^star-rating")
    star_elem = soup.find("p", attrs={"class": regex})
    book_star_count = star_elem["class"][-1]

    desc_elem = soup.find("div", attrs={"id": "product_description"}).find_next_sibling()
    book_desc = desc_elem.text

    product_info = {}
    table_rows = soup.find("table").find_all("tr")
    for row in table_rows:
        key = row.find("th").text
        value = row.find("td").text
        product_info[key] = value

    return {
        "book_name": book_name,
        "book_price": book_price,
        "book_star_count": book_star_count,
        "book_desc": book_desc,
        **product_info
    }

def get_book_urls(driver, url):
    """Get book urls from given detail page url"""
    MAX_PAGINATION = 3

    book_urls = []
    book_elements_xpath = "//div[@class='image_container']//a"

    for i in range(1, MAX_PAGINATION):
        update_url = url if i == 1 else url.replace("index", f"page-{i}")
        driver.get(update_url)
        book_elements = driver.find_elements(By.XPATH, book_elements_xpath)

        # Controller of pagination
        if not book_elements:
            break
        temp_urls = [element.get_attribute('href') for element in book_elements]
        book_urls.extend(temp_urls)

    return book_urls

def get_travel_and_nonfiction_category_urls(driver, url):
    """Gets category urls from given homepage url"""
    driver.get(url)
    time.sleep(SLEEP_TIME)

    category_elements_xpath = "//a[contains(text(),'Travel') or contains(text(),'Nonfiction')]"

    category_elements = driver.find_elements(By.XPATH, category_elements_xpath)
    category_urls = [element.get_attribute('href') for element in category_elements]

    return category_urls

def initialize_driver():
    """Initializes driver with maximized option"""
    options = webdriver.ChromeOptions()
    options.add_argument('--start.maximized')
    driver = webdriver.Chrome(options)
    return driver


# Sürecin otomatize edilerek Travel ile Nonfiction kategorilerine ait tüm kitapların detaylarını alacak şekilde
# kodun düzenlenmesi
from selenium import webdriver
import time
from selenium.webdriver.common.by import By

SLEEP_TIME = 0.25

def main():
    BASE_URL = 'https://books.toscrape.com/'
    driver = initialize_driver()
    category_urls = get_travel_and_nonfiction_category_urls(driver, BASE_URL)
    data = []

    for cat_url in category_urls:
        book_urls = get_book_urls(driver, cat_url)
        for book_url in book_urls:
            book_data = get_book_detail(driver, book_url)
            book_data["cat_url"] = cat_url
            data.append(book_data)

    len(data)

    # Optional
    import pandas as pd
    pd.set_option("display.max_columns", None)
    pd.set_option("display.max_colwidth", 40)
    pd.set_option("display.width", 2000)
    df = pd.DataFrame(data)

    # Close Page
    driver.close()

    # To csv
    df.to_csv('books.csv', index=False)

    return df


df = main()
print(df.head())
print(df.shape)
