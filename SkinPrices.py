import numpy as np
import pandas as pd
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import matplotlib.pyplot as plt
from matplotlib import rcParams

# read data

skin_data = pd.read_excel('D:\\Fun Projects Programming\\CSGO Skins\\CSGO_Skins.xlsx', nrows = 5)
skintypes = pd.read_excel('D:\\Fun Projects Programming\\CSGO Skins\\Skintype.xlsx')

# merging data on the type of item "database"

data_merged = pd.merge(skin_data, skintypes, on = 'Type', how = 'left')
data_merged = data_merged.replace(' ', '+', regex = True)

# building the hyperlink from data for web scraping

# general hyperlink structure:
#    https://skinport.com/market?cat=Knife&type=Bowie+Knife&item=Ultraviolet&exterior=3&stattrak=0&souvenir=0&stickers=0&nametag=0&vanilla=0
#              cat = Category; type = Typ, item = Skin, exterior = Zustand (2 = FN, 4 = MW, 3 = FT, 5 = WW, 1 = BS), stattrack etc = 0
link = []
for i in range(len(data_merged)):
    if re.search('Case', data_merged['Type'][i]):
        link.append('https://skinport.com/market?cat=Container&item=CS%3AGO+Weapon+Case')
    else:
        link.append('https://skinport.com/market?cat='+data_merged['Category'][i]+'&type='+data_merged['Type'][i]+'&item='+data_merged['Skin'][i]+'&exterior='+str(data_merged['Condition'][i])+'&stattrak=0&souvenir=0&stickers=0&nametag=0&vanilla=0')

scrapequestion = input("Do you want to scrape?")

# Question for scraping in order to prevent getting ip-banned from skinport for too many requests

if scrapequestion == "Yes":

    scraping_output = [[] for l in range(len(link))]

    for i in range(len(link)):

        # Launch the Chrome browser and open the webpage
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
        driver.get(link[i])

        # Wait for the page to load and find all the elements with class "Tooltip-link"
        elements = driver.find_elements(By.CLASS_NAME, "Tooltip-link")

        while len(elements) == 0:
            elements = driver.find_elements(By.CLASS_NAME, "Tooltip-link")

        # Print the text of each element
        for element in elements:
            
            scraping_output[i].append(element.text)

        # Close the browser
        driver.quit()


# Getting the price values
price_pattern = re.compile(".*,.{2} €$")

# Create price object
prices = [[] for l in range(len(link))]

# Looping through the output to search for the prices and append them to
# price object

for i in range(len(scraping_output)):
    
    for j in range(len(scraping_output[i])):
        match = price_pattern.search(scraping_output[i][j])
        if match:
            prices[i].append(float(match.group(0).replace(',', '.').replace('€', '')))

# Object for mean prices

meanprices = [[] for l in range(len(link))]

# Calculating the mean prices 

for i in range(len(meanprices)):
    meanprices[i] = np.round(np.mean(prices[i]))

data_merged['Actual Price'] = meanprices

# Prices are - 12% skinport fees

data_merged['Actual Price'] = data_merged['Actual Price'] * 0.88 

# Change in profit

profitchange = data_merged['Actual Price'] - data_merged['Buying Price']
data_merged['Profit'] = profitchange

# Change in profit in percent

percchange = ((data_merged['Actual Price'] - data_merged['Buying Price']) / data_merged['Buying Price'])
data_merged['% Change '] = percchange

# Time object for the actual date

import time
today = time.strftime("%d-%m-%Y")

# Plot for all items 

rcParams.update({'figure.autolayout': True})
ax = data_merged[['Buying Price', 'Actual Price']].plot(kind = 'bar')
ax.set_xticklabels(data_merged.Type, size = 6.5)
ax.set_xlabel('Type')
ax.set_ylabel('Price')
ax.legend(['Buying Price', 'Actual Price'])
plotname1 = today + "1.pdf"
plt.savefig(plotname1)
plt.show()


# Plot for the sum of the prices

kaufpreis_sum = np.sum(data_merged['Buying Price'])
aktuellerpreis_sum = np.sum(data_merged['Actual Price'])

figure, ax = plt.subplots()
labels = ['Buying Price', 'Actual Price']
positions = np.arange(len(labels))  
ax.set_xticks(positions) 
ax.set_xticklabels(labels)
bar_kauf = ax.bar(positions[0], kaufpreis_sum, width = 0.2, color='r')
bar_akt = ax.bar(positions[1], aktuellerpreis_sum, width = 0.2, color='g')
ax.legend((bar_kauf[0], bar_akt[0]), ('Buying Price', 'Actual Price'))
ax.set_ylabel('Sum')
plotname2 = today + "2.pdf"
plt.savefig(plotname2)
plt.show()


# export data

filename = today + ".xlsx"
data_merged.to_excel(filename)
