from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import pandas as pd
from bs4 import BeautifulSoup

# from lxml import etree

data_f = None
# State the Webdriver options
options = webdriver.ChromeOptions()

# Add argument to make it headless
# options.add_argument('--headless')

# Define the chrome driver path
ser = Service(
    r"C:\Users\AhmadAizudeen\OneDrive - The SOUTH-EAST ASIAN CENTRAL BANKS (SEACEN) RESEARCH AND TRAINING\Desktop\NLP Project\cfm-nlp\chromedriver_win32\chromedriver.exe"
)

# Initiate the Chromedriver by passing options as argument
driver = webdriver.Chrome(service=ser, options=options)

# Obtain the web page
# driver.get('https://www.federalreserve.gov/newsevents/pressreleases.htm')

driver.get(
    r"https://www.imf.org/en/Publications/SPROLLs/world-economic-outlook-databases#sort=%40imfdate%20descending"
)

element = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, "coveo-results-column"))
)


source = BeautifulSoup(driver.page_source, "html.parser")
source

#     dom = etree.HTML(str(source))

#     # int(time[0][4:])

#     date = [dom.xpath(f'//*[@id="article"]/div[1]/div[{x}]/div[1]/time')[0].text for x in range(1,21)]
#     date2 = [date[x][4:] for x in range(len(date))]
#     date_lim = '2023' if 2023 in date2 else '2024'
#     date_len = len(date)
#     title = [dom.xpath(f'//*[@id="article"]/div[1]/div[{x}]/div[2]/p[1]/span/a/text()')[0] for x in range(1, date_len + 1)]
#     link = ['https://www.federalreserve.gov'+dom.xpath(f'//*[@id="article"]/div[1]/div[{x}]/div[2]/p[1]/span/a/@href')[0] for x in range(1, date_len + 1)]
#     type_ = [dom.xpath(f'//*[@id="article"]/div[1]/div[{x}]/div[2]/p[2]/b/em')[0].text for x in range(1, date_len + 1)]

#     if data_f is None:
#         data_f = {'date': date, 'title' : title, 'link': link, 'type' : type_}
#         data_f = pd.DataFrame(data_f)
#     else:
#         data_f2 = {'date': date, 'title' : title, 'link': link, 'type' : type_}
#         data_f2 = pd.DataFrame(data_f2)
#         data_f = pd.concat([data_f, data_f2], ignore_index=True)

#     click_pag = driver.find_element(By.XPATH, f'//*[@id="article"]/ul[1]/li[11]/a')
#     click_pag.click()

# Print the title of the web page
print(driver.title)
