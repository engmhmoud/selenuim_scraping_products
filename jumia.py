import os
from decimal import Decimal
from re import sub
from time import sleep

from selenium import webdriver
from selenium.webdriver.firefox import firefox_profile
from selenium.webdriver.firefox.options import Options

from config import gecko_driver, jumia_base_url, page_load_sleep
from general import init_driver

# every categoy has many products
# every product has one category


class JumiaCategory:
    def __init__(self, name) -> None:
        self.name = name

    def __str__(self) -> str:
        return f"{self.name}"


class JumiaProduct:
    def __init__(self, name, price, oldprice, category: JumiaCategory) -> None:
        self.name = name
        self.price = price
        if oldprice is None:
            oldprice = price
        self.oldprice = oldprice
        self.category = category

    @property
    def discount(self):
        return (self.price - self.oldprice) / self.price

    def add_category(self, category: JumiaCategory):
        self.category = category

    def __str__(self):
        return f"JumiaProduct category:{self.category}Product name :{self.name} price :{self.oldprice} discount:{self.discount} new_price: {self.price}"


def get_jumia_url(driver, page_url):
    driver.get(page_url)
    sleep(page_load_sleep)

    popup_close = driver.find_elements_by_css_selector("[aria-label=newsletter_popup_close-cta]")
    if len(popup_close) > 0:
        popup_close[0].click()

    return True


def get_jumia_products():
    driver = init_driver(gecko_driver)
    # driver.get(jumia_base_url)
    categories: list[JumiaCategory] = [JumiaCategory("phones-tablets"), JumiaCategory("electronics"), JumiaCategory("computing")]
    list_of_all: list[JumiaProduct] = []
    for category in categories:
        category_url = f"{jumia_base_url}/{category.name}"

        for page_n in range(51):
            url = category_url + f"/?page={page_n}"

            # url = f"{jumia_base_url}/{categories[0]}/?page={1}"
            _ = get_jumia_url(driver, url)
            products = driver.find_elements_by_css_selector(".aim .-pvs section.card  div.-paxs  article.prd")
            print(len(products))
            jumia_products: list[JumiaProduct] = []
            for product in products:
                product_title = (
                    ""
                    if len(product.find_elements_by_css_selector("a .info h3.name")) == 0
                    else product.find_elements_by_css_selector("a .info h3.name")[0].text
                ).strip()

                price = (
                    ""
                    if len(product.find_elements_by_css_selector("a .info .prc")) == 0
                    else product.find_elements_by_css_selector("a .info .prc")[0].text
                ).strip()

                old_price = (
                    ""
                    if len(product.find_elements_by_css_selector("a .info .s-prc-w .old")) == 0
                    else product.find_elements_by_css_selector("a .info .s-prc-w .old")[0].text
                ).strip()

                # print(f"product_title{product_title}")
                # print(f"price{price}")
                # print(f"old_price{old_price}")
                if (product_title != "" or product_title is not None) and (price != "" or price is not None):
                    price = price.replace("جنيه", "").strip()
                    price = Decimal(sub(r"[^\d.]", "", price))

                    old_price = "" if old_price == "" else old_price.replace("جنيه", "").strip()
                    old_price = Decimal() if old_price == "" else Decimal(sub(r"[^\d.]", "", old_price))

                    product_obj = JumiaProduct(product_title, price, old_price, category)
                    jumia_products.append(product_obj)
                    print(f"i:{len(list_of_all)} category:{product_obj.category} page_n{page_n}  f_product_obj:{product_obj}")
                    list_of_all.append(product_obj)

    return list_of_all


print(get_jumia_products())
