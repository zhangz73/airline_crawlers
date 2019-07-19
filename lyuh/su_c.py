from selenium import webdriver
import time
import datetime
import csv


origs = ['SEA', 'LIH', 'HNL', 'OGG', 'ITO']
dests = ['SEA', 'LIH', 'HNL', 'OGG', 'ITO']
# dests = ['SEA', 'LIH', 'HNL', 'OGG', 'ITO']
start_date = datetime.date(2019,12,14)
check_days = 2


def main():
	print()
	print('/////////////////////////////////////////////////////////////////////////////')
	print('////////////////////// Student Universe Crawler v1.0.0 //////////////////////')
	print('/////////////////////////////////////////////////////////////////////////////')
	print('loading.')
	time.sleep(1)
	print('loading..')
	time.sleep(1)
	print('loading...')
	time.sleep(1)
	print('/////////////////////////////////////////////////////////////////////////////')
	with open('flights.csv', mode='w') as flights_file:
		flight_writer = csv.writer(flights_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		flight_writer.writerow(['Origin', 'Destination', 'Date', 'Price ($)', 'Num Stops', 'Connection', 'Duration (h)', 'Departure', 'Arrival', 'Carrier'])

		for orig in origs:
			for dest in dests:
				if orig == dest:
					continue
				for i in range(0, check_days):
					# Calculate date
					date = start_date + datetime.timedelta(days=i)
					print('---- Searching ' + orig + ' -> ' + dest + ' on ' + str(date) + ":")
					# Get url
					url = get_url(orig, dest, date)
					# Get driver
					driver = webdriver.Chrome('/Users/hongxiao_lyu/Desktop/su_crawler/chromedriver') 
					driver.get(url)
					# Crawl
					crawl(driver, flight_writer, orig, dest, date)
					# Close driver
					driver.close()
					driver.quit()
					print('-------------------------------------------------------------------')
	print()
	print('/////////////////////////////////////////////////////////////////////////////')
	print('////////////////////// Student Universe Crawler v1.0.0 //////////////////////')
	print('/////////////////////////////////////////////////////////////////////////////')
	print()
	print()


def get_url(orig, dest, date):
	return 'https://www.studentuniverse.com/flights/1/' + orig + '/' + dest + '/' + str(date) + '?flexible=true&premiumCabins=false'


def crawl(driver, flight_writer, orig, dest, date):
	# Wait for the page to load with content
	time.sleep(10)
	# Close the ads
	try:
		driver.find_element_by_class_name('IM_overlay_close_container').click();
	except:
		notuseful = 1
	time.sleep(5)

	# Find all iters and loop through
	lis = driver.find_elements_by_class_name('itin')
	for li in lis:
		price = li.find_element_by_class_name('itin-price-price').text
		airports = li.find_element_by_class_name('itin-leg-summary-airports').text
		num_stops = li.find_element_by_class_name('itin-leg-summary-stops').text
		try:
			connections = li.find_element_by_class_name('itin-leg-summary-connections').text
		except:
			connections = '()'
		duration = li.find_element_by_class_name('itin-leg-summary-duration').text
		times = li.find_element_by_class_name('itin-leg-summary-times').text
		carrier = li.find_element_by_class_name('itin-leg-summary-carrier').text
		print(price)
		print(airports + '   (' + carrier + ')')
		print(num_stops + '   ' + connections)
		print(duration + '   (' + times + ')')
		print()
		a = orig
		b = dest
		c = date
		d = price[1:]
		if num_stops == 'Nonstop':
			e = 0
		else:
			e = num_stops.split(' ')[0]
		f = connections
		duration = duration.split(' ')
		# duration format: (??h ??min) || (??h) || (??min)
		if len(duration) == 2:
			g = int(duration[0][:-1]) + int(duration[1][:-1]) / 60
		else:
			if duration[0][-1] == 'h':
				g = int(duration[0][:-1])
			else:
				g = int(duration[0][:-1]) / 60
		g = str('%.2f'%g)  # Duration (in decimal)
		times = times.split(' - ')
		h = times[0]  # Departure
		i = times[1]  # Arrival
		j = carrier  # Carrier
		flight_writer.writerow([a,b,c,d,e,f,g,h,i,j])


main()








