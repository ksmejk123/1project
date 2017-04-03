import csv
import os
from urllib.request import Request, urlopen
import time
import datetime
from bs4 import BeautifulSoup
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
def search_movie(keyword,name):
    a = keyword.encode('utf-8')
    a = str(a).replace('x','').replace('\\','%').split("'")
    search = a[1].upper()

    url = 'http://www.cine21.com/search/movie/?q=%s' %search
    print(url)
    pnext = True
    while pnext == True:
        url = request_until_succeed(url)
        soup = BeautifulSoup(url,'lxml')
        movie_info = soup.find('ul','mov_list')
        if movie_info != None:
            movie_info = movie_info.find_all('li')
            code,list = open_week()
            for i in movie_info:
                title = i.find('p','name').text
                sub_info = i.find_all('p','sub_info')[1]
                dt = sub_info.find_all('a')
                if len(dt) == 0:
                    df = 'pass'
                else:
                    df = dt[0].text.replace(' ','').replace(',','')
                af = ''
                for aa in range(1,len(dt)):
                    af = dt[aa].text +'/'+ af
                print(name,df)
                if df == name:
                    href = i.find('p', 'name')
                    href = href.find('a')['href']
                    story,dscore,ascore = info_get(href)
                    pnext = False
                    return (story,dscore,ascore )
                else:
                    page_next = soup.find('div','page')
                    page_next = page_next.find_all('a')
                    for i in page_next:
                        href2 = i['href']
                        pnext = True
                        q = i['href'][21:].encode('utf-8')
                        q = str(q).replace('x', '').replace('\\', '%').split("'")
                        search = q[1].upper()
                        url = 'http://www.cine21.com'+i['href'][:21]+search
                    print('감독과 안맞음')

def info_get(url):
    url = 'http://www.cine21.com' + url
    res = urlopen(url).read()
    soup = BeautifulSoup(res,'lxml')
    info = soup.find_all('p','sub_info')
    score_d = info[3].find('a')['href']
    d_score = get_score(score_d)
    if len(info) > 4:
        score_a = info[4].find_all('a')
        ascore = ''
        for at in score_a:
            href = at['href']
            a_score = get_score(href)
            a_name = at.text
            if a_name == 'more':
                continue
            else:
                ascore = a_name +':'+a_score +'/'+ascore
    else:
        ascore = '0'
    story = soup.find('div','story').text
    story = story.replace('\t','').replace('\r','').replace('\n','').replace(',', '').replace('(',' ').replace(')',' ')\
        .replace("‘", ' ').replace('’', ' ').replace('?', ' ').replace('&',' ').replace('[', ' ').replace(']', ' ').replace('!', ' ')
    return story,d_score,ascore

def get_score(href):
    url = 'http://www.cine21.com' + href
    res = request_until_succeed(url)
    soup = BeautifulSoup(res,'lxml')
    score = soup.find_all('p','score')
    score_tot =  0.0
    score2 = soup.find('span','score')
    if score2 == None:
        score2 = float(0.0)
    else:
        score2 = score2.text
        score2 = float(score2)

    if 5 >= score2 >=0:
        score2 = 1
    elif 10 >= score2 > 5:
        score2 = 2
    elif 15 >= score2 > 10:
        score2 = 3
    elif 20 >= score2 > 15:
        score2 = 4
    else:
        score2 = 5


    for i in range(len(score)):
        a = score[i].text.replace('\n','')
        a = a.replace('씨네21','').replace('네티즌','')
        if a == '--\t\t\t\t\t':
            a = 5
        score_tot = score_tot + float(a)
    score = (score_tot / 2.0)
    score = round(score + score2,2)
    return str(score)

def csv_open():
    with open('2016_영화.csv','r') as f:
        reader = csv.DictReader(f)
        return [item for item in reader]
if __name__ == '__main__':
    a,b = open_week()
    bb = csv_open()
    print(len(a))
    date = []
    for i in bb:
        name = i['영화명'].replace(' ', '').replace('/', '').replace(':','')
        if a.get(name):
            date.append(i)
    test = []
    print(len(date))
    # story, dscore, ascore = search_movie('최강전사미니특공대영웅의탄생', '이영준')
    for item in date:
        title = item['영화명'].replace(' ', '').replace('/', '').replace(':','').replace('?','').replace('포켓몬더무비XY','')
        name = item['감독'].replace(' ','').split(',')[0]
        story, dscore, ascore = search_movie(title, name)
        with open('movie_info.txt','a',encoding='utf-8') as f:
            f.write(title+'\t'+item['개봉일']+'\t'+name+':'+dscore+'\t'+ascore + '\t' +item['전국스크린수'].replace(',','')+'\t'
                    +item['전국관객수'].replace(',','')+'\t'+item['등급']+'\t'+story+'\n')
