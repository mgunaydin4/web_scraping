import streamlit as st
from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import re
import pandas as pd



SLEEP_TIME = 0.25


# Selenium Driver Initialization
def initialize_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Tarayıcıyı arka planda çalıştırmak için
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)
    return driver

# Function to scrape book details
def get_book_detail(driver, url):
    driver.get(url)
    time.sleep(SLEEP_TIME)
    content_div = driver.find_elements(By.XPATH, "//div[@class='content']")
    if not content_div:
        return {}

    inner_html = content_div[0].get_attribute('innerHTML')
    soup = BeautifulSoup(inner_html, "html.parser")

    book_name = soup.find("h1").text
    book_price = soup.find("p", attrs={"class": "price_color"}).text
    regex = re.compile("^star-rating")
    star_elem = soup.find("p", attrs={"class": regex})
    book_star_count = star_elem["class"][-1] if star_elem else "No Rating"
    desc_elem = soup.find("div", attrs={"id": "product_description"}).find_next_sibling()
    book_desc = desc_elem.text if desc_elem else "No Description"
    product_info = {row.find("th").text: row.find("td").text for row in soup.find("table").find_all("tr")}

    return {
        "book_name": book_name,
        "book_price": book_price,
        "book_star_count": book_star_count,
        "book_desc": book_desc,
        **product_info
    }


# Function to scrape book URLs
def get_book_urls(driver, url):
    MAX_PAGINATION = 3
    book_urls = []
    book_elements_xpath = "//div[@class='image_container']//a"
    for i in range(1, MAX_PAGINATION):
        update_url = url if i == 1 else url.replace("index", f"page-{i}")
        driver.get(update_url)
        book_elements = driver.find_elements(By.XPATH, book_elements_xpath)
        if not book_elements:
            break
        temp_urls = [element.get_attribute('href') for element in book_elements]
        book_urls.extend(temp_urls)
    return book_urls


# Function to scrape category URLs
def get_travel_and_nonfiction_category_urls(driver, url):
    driver.get(url)
    time.sleep(SLEEP_TIME)
    category_elements_xpath = "//a[contains(text(),'Travel') or contains(text(),'Nonfiction')]"
    category_elements = driver.find_elements(By.XPATH, category_elements_xpath)
    return [element.get_attribute('href') for element in category_elements]


# Main Application Logic
def main():
    st.title("Book Scraping Application")
    st.write("Bu uygulama, 'Books to Scrape' sitesinden kitap verilerini toplar.")

    if st.button("Verileri Çek"):
        BASE_URL = 'https://books.toscrape.com/'
        driver = initialize_driver()
        st.write("Sürücü başlatıldı ve anasayfa açılıyor...")
        category_urls = get_travel_and_nonfiction_category_urls(driver, BASE_URL)

        data = []
        for cat_url in category_urls:
            st.write(f"Kategori: {cat_url} için veriler çekiliyor...")
            book_urls = get_book_urls(driver, cat_url)
            for book_url in book_urls:
                book_data = get_book_detail(driver, book_url)
                book_data["category_url"] = cat_url
                data.append(book_data)

        driver.quit()
        df = pd.DataFrame(data)
        st.write("Veri toplama işlemi tamamlandı!")
        st.dataframe(df)

        # CSV Kaydetme
        csv = df.to_csv(index=False)
        st.download_button(
            label="Veriyi CSV olarak indir",
            data=csv,
            file_name="books.csv",
            mime="text/csv",
        )


# Streamlit Run
if __name__ == "__main__":
    main()
