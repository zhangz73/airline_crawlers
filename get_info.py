import re, sys, math, time
import requests
import xlrd
import xlsxwriter
from bs4 import BeautifulSoup
import urllib.request as urllib2
from requests_html import HTMLSession
from selenium import webdriver
import multiprocessing
from joblib import Parallel, delayed

cpu_count = multiprocessing.cpu_count()

session = HTMLSession()
#driver = webdriver.Chrome('/Users/zhangji/Desktop/installers/chromedriver')

all_data = []


workbook = xlsxwriter.Workbook('Airlines2.xlsx', {'strings_to_urls': False})
worksheet = workbook.add_worksheet()
worksheet.write('A1', 'Origin')
worksheet.write('B1', 'Destination')
worksheet.write('C1', 'travel_date')
worksheet.write('D1', 'number of stops')
worksheet.write('E1', 'flight duration')
worksheet.write('F1', 'flight time')
worksheet.write('G1', 'price per person')


def get_single_page(url, origin, destination, travel_date, idx):
    global driver
    driver.get(url)
    time.sleep(10)
    try:
        driver.find_element_by_class_name('IM_overlay_close_container').click()
        time.sleep(10)
    except:
        hh = 1

    all_trips = driver.find_elements_by_class_name('itin')
    for single_trip in all_trips:
        try:
            price = single_trip.find_element_by_class_name('itin-price-price').text
            num_stops = single_trip.find_element_by_class_name('itin-leg-summary-stops').text
            duration = single_trip.find_element_by_class_name('itin-leg-summary-duration').text
            times = single_trip.find_element_by_class_name('itin-leg-summary-times').text
            worksheet.write('A' + str(idx), origin)
            worksheet.write('B' + str(idx), destination)
            worksheet.write('C' + str(idx), travel_date)
            worksheet.write('D' + str(idx), num_stops)
            worksheet.write('E' + str(idx), duration)
            worksheet.write('F' + str(idx), times)
            worksheet.write('G' + str(idx), price)
            idx += 1
            if idx % 10 == 0:
                    print("we have printed " + str(idx) + " in total!")
            if idx % 250 == 0:
                driver.close()
                driver.quit()
                driver = webdriver.Chrome('/Users/zhangji/Desktop/installers/chromedriver')

        except:
            print(idx)
    return idx

def get_single_page_parallel(url, origin, destination, travel_date, driver):
    driver.get(url)
    time.sleep(10)
    try:
        driver.find_element_by_class_name('IM_overlay_close_container').click()
        time.sleep(10)
    except:
        hh = 1

    all_info = []
    all_trips = driver.find_elements_by_class_name('itin')
    for single_trip in all_trips:
        try:
            price = single_trip.find_element_by_class_name('itin-price-price').text.strip('$')
            num_stops = single_trip.find_element_by_class_name('itin-leg-summary-stops').text
            duration = single_trip.find_element_by_class_name('itin-leg-summary-duration').text
            times = single_trip.find_element_by_class_name('itin-leg-summary-times').text

            if (num_stops == 'Nonstop' or num_stops == '1 Stop') \
                    and 'h' in duration and int(duration.split('h')[0]) < 20:
                all_info.append([origin, destination, travel_date, num_stops, duration, times, price])

        except:
            time.sleep(10)
            price = single_trip.find_element_by_class_name('itin-price-price').text.strip('$')
            num_stops = single_trip.find_element_by_class_name('itin-leg-summary-stops').text
            duration = single_trip.find_element_by_class_name('itin-leg-summary-duration').text
            times = single_trip.find_element_by_class_name('itin-leg-summary-times').text

            if (num_stops == 'Nonstop' or num_stops == '1 Stop') \
                    and 'h' in duration and int(duration.split('h')[0]) < 20:
                all_info.append([origin, destination, travel_date, num_stops, duration, times, price])

    return all_info

def all_jobs_per_cpu(date, places):
    global all_data
    infos = []
    cnt = 0
    driver = webdriver.Chrome('/Users/zhangji/Desktop/installers/chromedriver')
    for d in date:
        print("We are crawling date " + str(d))
        for orig in places:
            for dest in places:
                if orig != dest:
                    url = get_url(orig, dest, d)
                    curr_info = get_single_page_parallel(url, orig, dest, d, driver)
                    cnt += 1
                    for infs in curr_info:
                        infos.append(infs)

                    if cnt % 10 == 0:
                        driver.close()
                        driver.quit()
                        driver = webdriver.Chrome('/Users/zhangji/Desktop/installers/chromedriver')
    for infs in infos:
        all_data.append(infs)
    driver.close()
    driver.quit()

def get_url(origin, destination, travel_date):
    str = "https://www.studentuniverse.com/flights/1/" + origin + "/" + \
          destination + "/" + travel_date + "?flexible=false&premiumCabins=false"
    return str


date = ["2019-12-" + str(i) for i in range(14, 32)]
for i in range(1, 6):
    date.append("2020-01-0" + str(i))
places = ['SEA', "LIH", "OGG", "ITO", "HNL"]

print(date)

date_distribute = []
for i in range(cpu_count):
    size = int(math.ceil(1.0 * len(date) / cpu_count))
    lo = i * size
    hi = min((i + 1) * size, len(date))
    date_distribute.append(date[lo:hi])

"""
idx = 2

for d in date:
    for orig in places:
        for dest in places:
            if orig != dest:
                url = get_url(orig, dest, d)
                idx = get_single_page(url, orig, dest, d, idx)
"""

Parallel(n_jobs=cpu_count, require='sharedmem')(delayed(all_jobs_per_cpu)(d, places) for d in date_distribute)
all_data = sorted(all_data, key=lambda x: (x[2], x[0], x[1], x[6]))

print("Crawling finished! Start to print...")
idx = 2
alphabets = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
for data in all_data:
    for i in range(len(alphabets)):
        worksheet.write(alphabets[i] + str(idx), data[i])
    idx += 1


print("jobs done!")

workbook.close()

