import time
import random
import argparse
from bs4 import BeautifulSoup
# 설치한 selenium에서 webdriver를 import
from selenium import webdriver

def login_naver(driver,id,pw):
    time.sleep(random.uniform(1,3)) # 자동화탐지를 우회 하기 위한 delay
    # naver login page로 이동
    driver.get("https://nid.naver.com/nidlogin.login?mode=form&url=https%3A%2F%2Fwww.naver.com")
    # id input, pw input 필드에 값을 입력
    # send_key()를 이용하였을때 captacha탐지가 되기 때문에 우회 방법으로 js으로 
    input_js = ' \
        document.getElementById("id").value = "{id}"; \
        document.getElementById("pw").value = "{pw}"; \
    '.format(id = id, pw = pw)
    time.sleep(random.uniform(1,3)) # 자동화탐지를 우회 하기 위한 delay
    driver.execute_script(input_js)
    time.sleep(random.uniform(1,3)) # 자동화탐지를 우회 하기 위한 delay
    driver.find_element_by_id("log.login").click()

    
def crawling_feed(driver):
    time.sleep(random.uniform(1,3)) # 자동화탐지를 우회 하기 위한 delay
    driver.get("https://myfeed.naver.com/index.nhn")
    # 기존 scrollHeight를 저장
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # Scroll down
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # page loading를 위한 대기 시간
        time.sleep(random.uniform(1.5,2))
        # 기존 height하고 변화가 발생하지 않을시 break
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    # list_feed 부분만 분리
    list_feed = driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[2]/div[1]/div[1]/div[2]").get_attribute('innerHTML')
    # beautifulsoup를 이용하여 분석
    soup = BeautifulSoup(list_feed, 'html.parser')
    list_feed = soup.find_all('li',{'class':'_ccast_item'})
    feed_data = list()
    for i in range(len(list_feed)):
        # feed 정보를 저장할 dictionary 선언
        feed = dict()
        # 정보에 대해 저장
        feed['title'] = list_feed[i].find('h4').find('a').text.strip()
        feed['date'] = list_feed[i].find('span',{'class':'wrt_time'}).text.strip()
        feed['copywriter'] = list_feed[i].find('span',{'class':'h_title'}).text.strip()
        feed['content_type'] = list_feed[i].find('span',{'class':'svc_name'}).text.strip()
        #thumnail이 없을 경우 div의 class의 이름이 달라져서 예외 처리
        try:
            div_cont = list_feed[i].find('div',{'class':'fd_cont'}).find('a')
            feed['preview'] = div_cont.text.strip()
            feed['link'] = div_cont.attrs['href']
        except:
            div_cont = list_feed[i].find('p',{'class':'thumbs_tx'}).find('a')
            feed['preview'] = div_cont.text.strip()
            feed['link'] = div_cont.attrs['href']
        feed_data.append(feed)

    return feed_data


def main(id,pw):
    # 다운받은 webdriver의 경로를 지정
    executable_path='D:/OneDrive - JaeSeo/blog/seleninum/python/webdriver/geckodriver.exe'
    driver = webdriver.Firefox(executable_path = executable_path)
    # 사용자 정의 함수 실행
    login_naver(driver,id,pw)
    data = crawling_feed(driver)
    # 출력을 위한 부분
    for i in range(len(data)):
        print('제목 : {title}\n작성자 : {copy}\n작성날짜 : {date}\n종류 : {type}\n미리보기 : {preview}\n주소 : {link}\n'.format(
            title = data[i]['title'],
            copy = data[i]['copywriter'],
            date = data[i]['date'],
            type = data[i]['content_type'],
            preview = data[i]['preview'],
            link = data[i]['link']))
    
def check_args():
    # 프로그램 실행시 인자를 통해 id, pw를 받음
    parser = argparse.ArgumentParser(description='Crawling naver feed with login.')
    parser.add_argument('-i', 
        required=True,
        metavar="id",
        help="인자로 naver id를 넘겨주세요.", 
        type=str)
    parser.add_argument('-p',
        required=True,
        metavar="password",
        help="인자로 naver password를 넘겨주세요.", 
        type=str)
    args = parser.parse_args()
    main(args.i, args.p)

if __name__ == "__main__":
    check_args()
    
