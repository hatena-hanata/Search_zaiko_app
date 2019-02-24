from tkinter import *
from tkinter import ttk
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
import time
import os


def scraping(app,item_id, item_type, prefecture_id):
    # ブラウザ起動
    driver = webdriver.PhantomJS()
    app.textField.insert('end', 'now1')
    # 店一覧のページをsoupへ
    shop_search_url = 'https://store-tsutaya.tsite.jp/tsutaya/articleList?account=tsutaya&' \
                      'accmd=1&arg=https%3A%2F%2Fstore-tsutaya.tsite.jp%2Fitem%2F{0}%2F{1}' \
                      '.html&ftop=1&adr={2}' \
        .format(item_type, item_id, prefecture_id)
    driver.get(shop_search_url)
    driver.implicitly_wait(10)  # 更新待機
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    app.textField.insert('end', 'now2')
    # 掲載ページ数を求める
    search_result_num = soup.find(class_='txt_k f_left').string
    total_shop_num = int(search_result_num.split('件')[1].split('全')[-1])
    if total_shop_num % 20 == 0:
        lastpage = total_shop_num / 20
    else:
        lastpage = int(total_shop_num / 20) + 1

    cnt = 0  # 掲載されてる店舗数を数える

    # ページごと処理
    for page in range(1, lastpage + 1):
        # 店舗一覧ページに戻る
        driver.get(shop_search_url)
        driver.implicitly_wait(10)  # 更新待機

        # ページを更新
        driver.execute_script("ExecuteAjaxRequest('./articleList', 'account=tsutaya&accmd=1&" \
                              "arg=https%3a%2f%2fstore-tsutaya.tsite.jp%2fitem%2f{0}%2f{1}.html" \
                              "&searchType=True&adr={2}&pg={3}&pageSize=20&pageLimit=10000&" \
                              "template=Ctrl%2fDispListArticle_g12', 'DispListArticle'); return false;" \
                              .format(item_type, item_id, prefecture_id, page))
        driver.implicitly_wait(10)  # 更新待機
        time.sleep(5)  # 更新待機

        # ページのsoupを取得する
        p_html = driver.page_source
        p_soup = BeautifulSoup(p_html, 'html.parser')

        # ページに掲載されている全店舗のURL取得
        table = p_soup.find('div', id='DispListArticle').find('table')
        links = table.find_all('a')
        for link in links:
            shop_url = link.get('href')
            cnt += get_zaiko_info(app,driver, shop_url)  # 在庫情報を取得

    # print('{0}件の店舗で取扱しています'.format(cnt))

    driver.quit()  # ブラウザを閉じる


def get_zaiko_info(app,driver, url):
    # urlを開いてsoupへ
    driver.get(url)
    driver.implicitly_wait(10)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    # 店の名前と在庫情報を取得
    shop_name = soup.find('h3', class_='green clearfix').find('a').string
    zaiko = soup.find('div', class_='state').find('span').string

    # 取扱がない場合0をreturn、取扱がある場合はcsvに店名と在庫情報を書き込む
    if '－' in zaiko:
        # print('{0}では取扱していません'.format(shop_name))
        return 0
    else:
        if '○' in zaiko:
            app.textField.insert('end', '{}では在庫があります'.format(shop_name))
        else:
            app.textField.insert('end', '{}では取扱していますが、現在在庫がありません'.format(shop_name))
        return 1


class ZaikoApp(ttk.Frame):

    def __init__(self, master=None):
        super().__init__(master)
        self.create_widgets()


    def btn_click(self,item_id,type_idx,prefec_idx):
        type_lst = ['rental_cd','rental_dvd']
        prefec_lst = ['13','14','12','11']
        scraping(self,item_id,type_lst[type_idx],prefec_lst[prefec_idx])


    def create_widgets(self):
        # 商品ID
        lbl_item_id = Label(text='商品ID').grid(column=0, row=0, padx=10, pady=20)
        txt_item_id = Entry(width=15)
        txt_item_id.grid(column=1, row=0, pady=20)

        # 販売形式
        lbl_type = Label(text='販売形式').grid(column=0, row=1, padx=10, pady=20)
        combo_type = ttk.Combobox(width=15)
        combo_type['values'] = ['レンタルCD', 'レンタルDVD']
        combo_type['state'] = 'readonly'
        combo_type.grid(column=1, row=1, pady=20)

        # 都道府県
        lbl_prefec = Label(text='都道府県').grid(column=0, row=2, padx=10, pady=20)
        combo_prefec = ttk.Combobox(width=15)
        combo_prefec['values'] = ['東京都','神奈川県','千葉県','埼玉県']
        combo_prefec['state'] = 'readonly'
        combo_prefec.grid(column=1, row=2, pady=20)

        # 処理開始ボタン
        start_btn = Button(text='START', width=23, height=5,\
                           command=lambda:self.btn_click(txt_item_id.get(),combo_type.current(),combo_prefec.current())
                           )
        start_btn.grid(column=0, row=3, padx=10, columnspan=2)

        # スクロールバーつきリストボックスを作成、表示
        printFrame = Frame(height=20, width=50)
        # リストボックス
        self.textField = Listbox(printFrame, width=50, height=20)
        self.textField.pack(side=LEFT)
        # スクロールバー
        scrollbar = Scrollbar(printFrame, orient=VERTICAL, command=self.textField.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.textField["yscrollcommand"] = scrollbar.set
        # 表示
        printFrame.grid(column=2, row=0, padx=20, pady=20, rowspan=4)

        self.grid()


def main():
    root = Tk()
    root.title("在庫検索")
    root.geometry("540x370")
    root.resizable(0,0)
    app = ZaikoApp(root)
    app.mainloop()


if __name__ == '__main__':
    main()