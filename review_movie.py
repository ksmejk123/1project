from bs4 import BeautifulSoup
import os
from urllib.request import Request,urlopen
import time
import datetime
import json
import csv

def request_until_succeed(url):
    req = Request(url)
    success = False
    while success is False:
        try:
            response = urlopen(req)
            if response.getcode() == 200:
                success = True
        except Exception as e:
            print(e)
            time.sleep(5)

            print("Error for URL %s: %s" % (url, datetime.datetime.now()))
            print("Retrying.")

            if '400' in str(e):
                return None;
    return response.read()

def search_movie(keyword):
    a = keyword.encode('utf-8')
    a = str(a).replace('x','').replace('\\','%').split("'")
    search = a[1].upper()

    url = 'http://www.cine21.com/search/movie/?q=%s' %search
    url = request_until_succeed(url)
    soup = BeautifulSoup(url,'lxml')

    movie_info = soup.find('ul','mov_list')
    if movie_info != None:
        movie_info = movie_info.find_all('li')
        code,list = open_week()
        code = code[keyword]

        for i in movie_info:
            title = i.find('p','name').text
            sub_info = i.find_all('p','sub_info')[1]
            dt = sub_info.find_all('a')
            if len(dt) == 0:
                df = 'pass'
            else:
                df = dt[0].text
            af = ''
            for aa in range(1,len(dt)):
                af = dt[aa].text +'/'+ af
            chek = chek_movie(code,df)

            if chek == 200:
                href = i.find('p','name')
                href = href.find('a')['href']
                rank, day, tot, story = info_get(href)
                with open('movie_info.csv', 'a', newline='', encoding='utf-8') as f:
                    reader = csv.DictWriter(f, fieldnames=['title','day', 'df', 'af', 'tot','rank','story'])
                    reader.writeheader()
                    reader.writerow({'title': title,'day':day, 'df': df, 'af': af, 'tot': tot,'rank':rank,'story': story})
                # with open('movie_info.txt', 'a', encoding='utf-8') as f:
                #     story = story.replace(',', '').replace("'", ' ').replace('"', ' ').replace('?', ' ').replace('&',' ').replace('[', ' ').replace(']', ' ').replace('!', ' ')
                #     f.write(title + ',' + day + ',' + df + ',' + af + ',' + tot + ',' + rank+ ',' +story + ',' + '\n')
            else:
                print('감독과 안맞음')

def info_get(url):
    url = 'http://www.cine21.com' + url
    print(url)
    res = urlopen(url).read()
    soup = BeautifulSoup(res,'lxml')
    info = soup.find_all('p','sub_info')
    rank2 = info[0].find_all('span')
    if len(rank2) < 3:
        rank = '__'
        day = '__'
        tot =  '__'
    else:
        rank = info[0].find_all('span')[2]
        rank = rank.text
        tot = info[2].find_all('span')
        if len(tot) < 1:
            day = '개봉일없음'
            tot = '관객수없음'
        elif len(tot) < 2:
            day = info[2].find_all('span')[0].text
            day = day.replace('개봉일 : ', '')
            tot = '관객수없음'
        else:
            day = info[2].find_all('span')[0].text
            day = day.replace('개봉일 : ', '')
            tot = info[2].find_all('span')[1].text
            tot = tot.replace('누적관객 : ','')

    story = soup.find('div','story').text
    story = story.replace('\t','').replace('\r','').replace('\n','').replace(',', '').replace('(',' ').replace(')',' ')\
        .replace("‘", ' ').replace('’', ' ').replace('?', ' ').replace('&',' ').replace('[', ' ').replace(']', ' ').replace('!', ' ')
    print(story)
    return rank,day,tot,story


def reviw_search(keyword):
    a = keyword.encode('utf-8')
    a = str(a).replace('x', '').replace('\\', '%').split("'")
    search = a[1].upper()
    url = 'http://movie.naver.com/movie/search/result.nhn?section=movie&query=%s&section=all&ie=utf8' %search
    # print(url)
    url = request_until_succeed(url)
    soup = BeautifulSoup(url, 'lxml')

    movie_info = soup.find('ul','search_list_1')
    movie_info = movie_info.find_all('li')
    code,list = open_week()
    code = code[keyword]
    for i in movie_info:
        dt = i.find_all('dd','etc')
        if dt[1].find('a') == None:
            print(dt[1])
            df = 'pass'
        else:
            df = dt[1].find('a').text
        chek = chek_movie(code,df)
        if chek == 200:
            href = i.find('p','result_thumb')
            href = href.find('a')['href']
            href = href.replace('basic','pointWriteFormList')
            href = href+'&type=after&page=1'
            print('http://movie.naver.com'+href)
            review_get(keyword,href)
        else:
            print('감독과 안맞음')
def review_get(keyword,href):
    url = 'http://movie.naver.com%s' %href
    res = request_until_succeed(url)
    soup = BeautifulSoup(res,'lxml')
    page_next = soup.find('div','paging')
    p_next = True
    if page_next == None:
        p_next = False
        print('리뷰없음')
    else:
        if os.path.exists('review2/%s.txt' % keyword) == False:
            while p_next == True:
                soup = BeautifulSoup(res, 'lxml')
                page_next = soup.find('div', 'paging')
                page_next = page_next.find('a','pg_next')
                review_list = soup.find('div','score_result')
                review_items = review_list.find_all('li')
                for i in review_items:
                    score = i.find('div','star_score').text.replace('\n','')
                    user = i.find('div','score_reple')
                    user_id = user.find('dt').find('span').text.replace('\n','')
                    user_review = user.find('p')
                    user_review = user_review.getText().replace('BEST','')

                    with open('review2/%s.txt' %keyword,'a',encoding='utf-8') as f:
                        f.write(user_id+' '+user_review+' '+score+'\n')
                if page_next != None:
                    href2 = page_next['href']
                    res = request_until_succeed('http://movie.naver.com' + href2)
                else:
                    p_next = False
                    print('마지막페이지')
        else:
            p_next = False
            print('pass')


def chek_movie(code,dname):
    key = '60bb37c104a9db27671bbc03aef50b42'
    url = 'http://www.kobis.or.kr/kobisopenapi/webservice/rest/movie/searchMovieInfo.json?' \
          'key=%s&movieCd=%s' % (key, code)
    res = urlopen(url).read()
    data = json.loads(res.decode('utf-8'))
    data = data['movieInfoResult']['movieInfo']['directors'][0]['peopleNm']

    if data == dname:
        s = 200
        return s
    else:
        s = 400
        return 400

def open_week():
    file_list = os.listdir('week2')
    # df = pd.DataFrame(columns=["tit",'day','scr'])
    df = {}
    df_list = []
    for i in file_list:
        with open('week2/'+i,'r',encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader, None)
            for file in reader:
                code = file[0]
                tit = file[1].replace(' ', '').replace('/', '').replace(':','')
                open_day = file[2]
                scr = file[3]
                if df.get(tit) == None:
                    df_list.append(tit)
                    df[tit] = code
    return df,df_list
def info_open():
    date = []
    with open('movie_info.csv','r',encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i in reader:
            date.append(i)
    return date

if __name__ == '__main__':
    a,b = open_week()
    print(len(b))
    for i in b:
        print(i)
        i = i.replace(' ', '').replace('\n', '').replace('/', '').replace(':','')
        reviw_search(i)
        # search_movie(i)





