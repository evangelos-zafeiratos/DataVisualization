import requests
import csv
import re
import json
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

def fuel_Data(URL):
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    jsTag = soup.find_all('script', attrs={"type": "text/javascript"})
    stringData = str(jsTag[-1])
    fuelDataList = re.findall(r'{[.\s\w\"\:\,\[\]]*}',stringData)
    fuelData = json.loads(fuelDataList[0])
    fuelValues = fuelData.get('values')
    fuel_df = pd.DataFrame(fuelValues, columns=['Date', 'Price'])

    # Timestamp is not in the correct format, we remove 3 0s in order to convert it to proper format
    fuel_df['Date'] = fuel_df['Date'].apply(lambda x: datetime.fromtimestamp(x / 1000))
    return fuel_df

def energy_Data(URL):
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    aaa = soup.find('table', id="statTableHTML")
    #print(aaa.prettify())
    rows = aaa.find_all('tr')
    pandas_list = list()
    for row in rows:
        columns = row.find_all('td')
        if len(columns) == 0:
            continue
        else:
            pandas_entry = list()
            date = columns[0].string.split()
            if date[0] == 'Mai':
                date[0] = 'May'
            new_date = date[0] + ' 20' + date[1]
            new_value = columns[1].string
            pandas_entry.append(new_date)
            pandas_entry.append(new_value)
        pandas_list.append(pandas_entry)
    energy_df = pd.DataFrame(pandas_list,columns=['Date', 'Price'])
    return energy_df

def macroEconomy():
    indicatorsURL = 'https://tradingeconomics.com/greece/indicators'
    indicatorsPage = requests.get(indicatorsURL)
    indicatorsSoup = BeautifulSoup(indicatorsPage.content, 'html.parser')

    stockMarket_td = indicatorsSoup.find(href=re.compile("/greece/stock-market")).find_parent('td')
    stockValue = stockMarket_td.next_sibling.next_sibling
    stockValueOld = stockValue.next_sibling.next_sibling

    GDPgrowth_td = indicatorsSoup.find(href=re.compile("/greece/gdp-growth-annual")).find_parent('td')
    GDPannualGrowth = GDPgrowth_td.next_sibling.next_sibling
    GDPChange = GDPannualGrowth.next_sibling.next_sibling

    unemploymentRate_td = indicatorsSoup.find(href=re.compile("/greece/unemployment-rate")).find_parent('td')
    unemploymentRate = unemploymentRate_td.next_sibling.next_sibling
    unemploymentChange = unemploymentRate.next_sibling.next_sibling

    inflation_td = indicatorsSoup.find(href=re.compile("/greece/inflation-cpi")).find_parent('td')
    inflationRate = inflation_td.next_sibling.next_sibling
    inflationRateChange = inflationRate.next_sibling.next_sibling

    macro = pd.DataFrame([['GDP', GDPannualGrowth.string, GDPChange.string], ['unemployment', unemploymentRate.string, unemploymentChange.string], ['inflation', inflationRate.string, inflationRateChange.string]], columns = ['index','Value', 'Change'])#, index = ['GDP', 'unemployment', 'inflation'])

    stockValue = float(stockValue.string)
    stockValueOld = float(stockValueOld.string)

    stockValueChange = (stockValue - stockValueOld)/stockValueOld
    stock = pd.DataFrame([[stockValue, stockValueChange]], columns = ['Value', 'Change'], index = ['stock'])

    return macro, stock

def bonds():
    bondsURL = 'https://tradingeconomics.com/greece/government-bond-yield'
    bondsPage = requests.get(bondsURL)
    bondsSoup = BeautifulSoup(bondsPage.content, 'html.parser')

    bond10Year_td = bondsSoup.find("tr", attrs={"data-symbol": "GGGB10YR:IND"})
    bond10Year = ['10Y']
    for child in bond10Year_td.children:
        text = child.string
        if text == None or text == '\n':
            continue
        else:
            bond10Year.append(text)

    bond20Year_td = bondsSoup.find("tr", attrs={"data-symbol": "GGGB20Y:IND"})
    bond20Year = ['20Y']
    for child in bond20Year_td.children:
        text = child.string
        if text == None or text == '\n':
            continue
        else:
            bond20Year.append(text)
    bonds = pd.DataFrame([bond10Year, bond20Year], columns = ['bond','yield', 'day', 'month', 'year', 'date'])
    return bonds

macro,stocks = macroEconomy()
bonds = bonds()
diesel = fuel_Data('https://gr.fuelo.net/fuel/type/diesel/3years?lang=en')
unleaded = fuel_Data('https://gr.fuelo.net/fuel/type/gasoline/3years?lang=en')
electricity = energy_Data('https://www.statista.com/statistics/1215877/dam-electricity-baseload-price-greece/')


print(macro)
print(stocks)
print(bonds)
print(diesel)
print(unleaded)
print(electricity)
