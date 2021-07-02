from bs4 import BeautifulSoup
from django.http import HttpResponse
from django.shortcuts import render



def news_view(request):
    url = 'https://www.glamour.ru/beauty-news/'
    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36"}
    response = request.get(url, headers=headers)

    list_news = []

    context = {'list_news': list_news}

    if response.status_code == 200:
        html = response.text
        soup = BeautifulSoup(html, 'lxml')
        all_news = soup.find('div', class_="grid--with-sidebar").find_all('div', class_="col-content")
        for news in all_news:
            title = news.find('div', class_="item__body").find('h3', class_="item__title").text
            title = title.strip()
            data = {'title': title}
            list_news.append(data)
    else:
        return HttpResponse('<h1>Page not found</h1>')
    return render(request, 'news.html', context)