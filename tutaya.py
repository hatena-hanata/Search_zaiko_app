from bs4 import BeautifulSoup
import requests
from selenium import webdriver
import time
import os
import csv


# グローバル変数
item_id = '005449585'
item_type = 'rental_cd'
prefecture_id = '13'
csv_save_dir = './csv/'
driver = webdriver.PhantomJS()


# 在庫情報を取得する
def get_zaiko_info(url):
    # urlを開いてsoupへ
    driver.get(url)
    driver.implicitly_wait(10)
    html = driver.page_source
    soup = BeautifulSoup(html,'html.parser')

    # 店の名前と在庫情報を取得
    shop_name = soup.find('h3',class_='green clearfix').find('a').string
    zaiko = soup.find('div',class_='state').find('span').string

    # 取扱がない場合0をreturn、取扱がある場合はcsvに店名と在庫情報を書き込む
    if '－' in zaiko:
        print('{0}では取扱していません'.format(shop_name))
        return 0
    else:
        with open(csv_save_dir+'zaiko.csv','a',newline='') as file:
            writer = csv.writer(file)
            writer.writerow([shop_name,zaiko])
        if '○' in zaiko:
            print('{0}では在庫があります'.format(shop_name))
        else:
            print('{0}では取扱していますが、現在在庫がありません'.format(shop_name))
        return 1


def main():
    # csvの保存場所作成
    os.makedirs(csv_save_dir,exist_ok=True)

    # 店一覧のページをsoupへ
    shop_search_url = 'https://store-tsutaya.tsite.jp/tsutaya/articleList?account=tsutaya&'\
                      'accmd=1&arg=https%3A%2F%2Fstore-tsutaya.tsite.jp%2Fitem%2F{0}%2F{1}'\
                      '.html&ftop=1&adr={2}'\
                      .format(item_type,item_id,prefecture_id)
    driver.get(shop_search_url)
    driver.implicitly_wait(10) # 更新待機
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    # 掲載ページ数を求める
    search_result_num = soup.find(class_='txt_k f_left').string
    total_shop_num = int(search_result_num.split('件')[1].split('全')[-1])
    if total_shop_num % 20 == 0:
        lastpage = total_shop_num / 20
    else:
        lastpage = int(total_shop_num/20) + 1

    cnt = 0 # 掲載されてる店舗数を数える

    # ページごと処理
    for page in range(1, lastpage+1):
        # 店舗一覧ページに戻る
        driver.get(shop_search_url)
        driver.implicitly_wait(10) # 更新待機

        # ページを更新
        driver.execute_script("ExecuteAjaxRequest('./articleList', 'account=tsutaya&accmd=1&"\
                              "arg=https%3a%2f%2fstore-tsutaya.tsite.jp%2fitem%2f{0}%2f{1}.html"\
                              "&searchType=True&adr={2}&pg={3}&pageSize=20&pageLimit=10000&"\
                              "template=Ctrl%2fDispListArticle_g12', 'DispListArticle'); return false;"\
                              .format(item_type,item_id,prefecture_id,page))
        driver.implicitly_wait(10)  # 更新待機
        time.sleep(5) # 更新待機

        # ページのsoupを取得する
        p_html = driver.page_source
        p_soup = BeautifulSoup(p_html, 'html.parser')

        # ページに掲載されている全店舗のURL取得
        table = p_soup.find('div', id='DispListArticle').find('table')
        links = table.find_all('a')
        for link in links:
            shop_url = link.get('href')
            cnt += get_zaiko_info(shop_url) # 在庫情報を取得

    print('{0}件の店舗で取扱しています'.format(cnt))

    driver.quit() # ブラウザを閉じる


if __name__ == '__main__':
    main()
