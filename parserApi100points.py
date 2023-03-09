import requests
from bs4 import BeautifulSoup as BS

s = requests.Session()
print("Введите название сохраняемого файла: ")
name_file = str(input())
f = open(name_file + ".txt", 'w')  # Открыли файл на запись результатов домашки
########################################################################
# Get token
auth_html = s.get("https://api.100points.ru/login")
auth_bs = BS(auth_html.content, "html.parser")
token = auth_bs.select("input[name=_token]")[0]['value']
# Обработали инфу с токеном
########################################################################

login = ""  # Логин от апи
password = ""  # Пароль от апи

# Авторизация на сайте #
payload = {
    "_token": token,
    "returnUrl": '/',
    "email": login,  # Логин от апи
    "password": password  # Пароль от апи
}

answ = s.post("https://api.100points.ru/login", data=payload)  # Авторизовываемся на сайте под нашими данными
answ_bs = BS(answ.content, "html.parser")  # Получаем контент

r = requests.get("https://api.100points.ru/student_homework/index?status=passed",
                 data=payload)  # Создаем запрос на получение страницы домашки
#######################################################################

#######################################################################

# Запрашиваем ссылку на домашку#
print("Введите ссылку домашки, уже с отфильтрованным нужным заданием: \n Отфильтровали домашку - > нажали ")

url_homework = str(input())
#
curators_check_setting = True  # Добавлять результаты "Проверка от куратора часть"
percent_completion_setting = False  # Добавлять результаты "Процент выполнения"
time_homework_setting = False  # Добавлять время сдачи дз
url_homework_setting = True  # Добавлять ссылку на саму дз
test_part_setting = False  # Добавлять результаты "Тестовая часть"
with requests.session() as session:  # Обрабатываем домашку
    session.post("https://api.100points.ru/login", data=payload)
    response = session.get(url_homework + "&page=" + str(1))
    html_after_authorization = BS(response.content, 'html.parser')

    ##################Получаем кол-во страниц для проверки################################
    current_class_page_link = ""
    prev_class_page_link = ""
    try:
        for i in html_after_authorization.select(".pagination"):
            d1 = i.find_all("a", class_="page-link")  # Ищем все строчки html кода с нумерацией страниц
            for j in d1:
                prev_class_page_link = current_class_page_link  # Запоминаем текущую страницу и предыдущую, т.к самый последний html код - это кнопка Next
                current_class_page_link = j
        count_pages = int(((prev_class_page_link.text).replace(' ', '')))  # Убираем пробельчики
    except Exception as ex:
        count_pages = 1
    #######################################################################################
    for i in range(1, count_pages + 1):  # Проходимся по каждой странице
        response = session.get(url_homework + "&page=" + str(i))  # Получаем текущую страницу
        html = BS(response.content, 'html.parser')
        for el in html.select(".odd "):  # Проходимся по строкам учеников
            url = el.select("a", class_="odd")  # Получаем url-ссылку домашки определенного ученика
            find_add_div_user = el.find_all("div")
            level_homework = find_add_div_user[7].get_text().split()
            level_homework_name = " ".join(level_homework)
            f.write(find_add_div_user[2].text + '|' + (level_homework_name) + '|')

            #######################################################
            for url_list in url:  # Проходимся по url чтоб получить чистую ссылку
                homework_user_url = url_list.get("href")
                if (url_homework_setting == True):
                    f.write(homework_user_url + '|')
            ##########################################################

            # Работа со страницей дз # ## Новая версия отличается тем, что не считает кол-во "верный" и использует сразу оценку куратора
            response_homework = session.get(
                homework_user_url + str("?status=checking"))  # Переходим на страницу домашки
            html_homework = BS(response_homework.content, 'html.parser')  # Получаем html домашки
            text_with_value = ""
            for el2 in html_homework.select(".card-body"):
                find_all_done_tasks_user = el2.find_all("div",
                                                        class_="form-group col-md-3")  # Проходимся по домашке и считаем кол-во верных ответов
                k = 0  # ищем по счетчику классов нужный
                for el3 in find_all_done_tasks_user:
                    k += 1
                    if (k == 4) and (time_homework_setting):
                        time_homework = el3.text.strip().split('\n')[1].strip()
                        f.write(time_homework + '|')
                    if (k == 5) and (percent_completion_setting):
                        percent_completion = (el3.text[24:]).partition('%')[0]
                        f.write(percent_completion + '|')
                    if (k == 6) and (curators_check_setting or test_part_setting):
                        text_otvet = (el3.text).split("\n")
                        if (test_part_setting):
                            count_good_test = (text_otvet[1][17:]).partition('/')[0]
                            f.write(count_good_test)
                        if curators_check_setting:
                            count_good_curator = (text_otvet[2][23:]).partition('/')[0]
                            f.write(count_good_curator + '|')
                # f.write('\n')
            #print("Количество верно решенных задач:", text_with_value)
            f.write('\n')
f.close()
