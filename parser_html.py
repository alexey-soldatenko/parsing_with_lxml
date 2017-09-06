from lxml import html
from urllib.request import Request, urlopen
import csv

#функция записи страницы в файл
def write_page_in_file(url, file):
	request = Request(url, headers={'User-Agent':'Mozilla/5.0'})
	webpage = urlopen(request).read()
	with open(file, 'wb') as out_file:
		out_file.write(webpage)

#функция парсинга файла
def parse_file(file_name):
	document = html.parse(file_name)
	return document.find('body')

#основная страница с заказами
url = 'https://freelancehunt.com/projects/skill/python/22.html'

write_page_in_file(url, 'test.html')
body = parse_file('test.html')

#находим все строки таблицы table table-normal, в которой хранятся записи о заказах
row = body.xpath('//table[@class="table table-normal"]/tbody/tr')
#список, включающий словари с данными о каждом заказе
out_list = []

for tr in row:
	#словарь с данными о заказу
	parametrs = {}

	#Заголовок заказа - он же ссылка на страницу заказа
	a = tr.xpath('td[@class="left"]/a[@class="bigger visitable"]')
	parametrs["title"] = a[0].text
	parametrs["link"] = a[0].attrib["href"]

	#переходим на страницу заказа и берем описание
	write_page_in_file('https://freelancehunt.com/'+parametrs["link"], 'test.html')
	new_page = parse_file('test.html')
	describe = new_page.xpath('//div[@class="linkify-marker img-responsive-container"]//p')
	s = ''
	for p in describe:
		try:
			s += p.text +' '
		except:
			s += p.text_content()
	parametrs["describe"] = s

	#цена заказа
	price = tr.xpath('td[@class="text-center"]/span/div[@class="text-green price with-tooltip"]')
	if price != []:
		parametrs["price"]=price[0].text
	else:
		parametrs["price"]= "договорная"

	#дата публикации заказа 
	date_open = tr.xpath('td[@class="text-center hidden-xs"]/div[@class="with-tooltip"]/div[@class="with-tooltip calendar"]')
	if date_open == []:
		date_open = tr.xpath('td[@class="text-center hidden-xs"]/div[@class="with-tooltip"]')
		parametrs["date_open"] = 'today'
	else:
		day = str(date_open[0].xpath('h2')[0].text)
		month = str(date_open[0].xpath('h5')[0].text)
		parametrs["date_open"] = day + ' ' + month

	#дата завершения
	date_close = tr.xpath('td[@class="text-center hidden-xs"]/div[@class="with-tooltip calendar"]')
	if date_close == []:
		date_close = tr.xpath('td[@class="text-center hidden-xs"]/div[@class="with-tooltip calendar date-expiring"]')
	day = str(date_close[0].xpath('h2')[0].text)
	month = str(date_close[0].xpath('h5')[0].text)
	parametrs["date_close"] = day + ' ' + month
	
	#записываем в список значения текущего заказа
	out_list.append(parametrs)
	del parametrs

#записываем полученный список в файл csv, с которым в дальнейшем работаем как с файлом libre office
with open('test1.csv', 'w') as csvfile:
	fieldnames = ['title', 'describe', 'date_open', 'link', 'date_close', 'price']
	writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
	writer.writeheader()
	for ls in out_list:
		writer.writerow(ls)
	
