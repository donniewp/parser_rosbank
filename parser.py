import requests
from bs4 import BeautifulSoup
import time
from progress.bar import IncrementalBar

f = open('textAll.txt', 'w')
b = open('textAll_Fail.txt', 'w')  # открываем (создаем) два файла для дальнейшего использования


def laziesformfind(stuff): # лютейший кастыль, с помощью которого из огромного html кода я нахожу нужный топик
    form = ''
    for i in range(stuff.find('"form_id":"1","product_code":"') + 30, len(script)): # нахожу соответствующую строку ("form_id":"1","product_code":")
        if script[i] != '"':        # нам известен индекс первой двойной кавычки. прибавляем +30(те длину всей строки)
            form += script[i]       # и уже получаем индекс последней кавычки строки. после нее как раз таки стоит топик. (как это выглядит в html коде - "form_id":"1","product_code":"тут находится наш топик")
            # прибавляем к строке символы, если это не кавычка
        else:
            break
            # нашли кавычку после топика, заканчиваем цикл
    return form


headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 "
                         "(KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36"} # браузеры с помощью которых мы заходим на сайт
opensite = open('URL_RB.txt', 'r', encoding="utf8") # открываем файл с сайтами (файл должен находить в одной папке с кодом)
sites = [] # создаем массив сайтов
while True:
    site = opensite.readline()[:-2] # эта штука считывает 1 сторочку в txt
    if not site:
        break
    sites.append(site) #добавляем в массив сайтов

bar = IncrementalBar('Countdown', max=len(sites)) # имитация загрузочной строки

num = 1
numFail = 1
err_timeout = 0
err_ConnectionError = 0
err_AttributeError = 0

for site in sites: # из большого массива сайта берем первый сайт и так далее
    time.sleep(3) # задержка кода
    bar.next()
    try: # пытаемся получить код сайта
        r = requests.get(site, timeout=30, headers=headers).text
    except requests.Timeout as err: # если случилось одна из ошибок, то ничего страшного, мы просто идем дальше =)
        err_timeout += 1
        b.write(str(numFail) + ') ' + site + '\n')
        numFail += 1
        continue
    except requests.exceptions.TooManyRedirects:
        b.write(str(numFail) + ') ' + site + '\n')
        numFail += 1
        continue
    except requests.ConnectionError as err:
        b.write(str(numFail) + ') ' + site + '\n')
        numFail += 1
        err_ConnectionError += 1
        continue

    doc = BeautifulSoup(r, "lxml") # приводим код сайта в формат бьютифулсуп для дальнейшего парсинга
    try:
        script = doc.find("script", type='application/json').text #находим такой скрипт, у которого есть соответвующий тайп  (единственная строчка хоть как-то связанная с парсингом =) )
    except AttributeError: # если скрипта нет, то ничего страшного идем дальше
        err_AttributeError += 1
        b.write(str(numFail) + ') ' + site + '\n')
        numFail += 1
        continue
    if laziesformfind(script) == '': # обращаемся к моему костылю, с помощью которого, по соответвую мы находим топик
        continue # кстати костыль, из-за того что, заместо использования иснтрументов парсинга, я просто использую втроенные функции работы со строками ( чем и является html код )
    else:
        f.write(str(num) + ') ' + laziesformfind(script) + ' : ' + site + '\n') # если такой есть, то мы записываем его в txt файл
        num += 1
f.close()
b.close() # закрываем txt файлы
bar.finish() # заканчиваем имитацию
print('TimeoutErrors: ', err_timeout)
print('ConnectionError: ', err_ConnectionError)
print('AttributeError: ', err_AttributeError) # выводим ошибки
