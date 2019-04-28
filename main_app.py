# ライブラリ
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
import time
import os
import threading
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


class ZaikoApp(ttk.Frame):

    def __init__(self, master=None):
        super().__init__(master)
        self.make_menu()
        self.create_widgets()
        self.is_active = True

    def make_menu(self):
        self.the_menu = Menu(self, tearoff=0)
        self.the_menu.add_command(label="貼り付け")

    def show_menu(self, event):
        widget = event.widget
        self.the_menu.entryconfigure("貼り付け", command=lambda: widget.event_generate("<<Paste>>"))
        self.the_menu.tk.call("tk_popup", self.the_menu, event.x_root, event.y_root)

    def btn_click(self, item_id, type_idx, prefec_idx):
        """
        startボタンを押すと呼び出される。スクレイピングを並列処理で開始する
        :param item_id: 商品id
        :param type_idx: 商品型式（レンタルcd or レンタルdvd）
        :param prefec_idx: 都道府県id（今回は関東だけ）
        :return:
        """
        type_lst = ('rental_cd', 'rental_dvd')
        prefec_lst = ('13', '14', '12', '11')
        # 処理開始
        if self.start_btn['text'] == 'START':
            self.textField.delete(0, 'end')  # テキストボックスを空にする
            self.start_btn['state'] = 'disabled'
            self.is_active = True
            # スクレイピングを並列実行
            thread = threading.Thread(target=self.scraping, args=(item_id, type_lst[type_idx], prefec_lst[prefec_idx]))
            thread.start()
        else:
            # スクレイピングをフラグで中止させ、ボタンをスタートに戻す
            self.is_active = False
            self.start_btn['text'] = 'START'

    def create_widgets(self):
        # 商品IDラベルと入力ボックス
        lbl_item_id = Label(text='商品ID').grid(column=0, row=0, padx=10, pady=20)  # ラベル
        txt_item_id = Entry(width=15)
        txt_item_id.bind("<Button-3><ButtonRelease-3>", self.show_menu)  # 右クリックで貼り付けできるようにする
        txt_item_id.grid(column=1, row=0, pady=20, sticky=W)

        # 販売形式
        lbl_type = Label(text='販売形式').grid(column=0, row=1, padx=10, pady=20)
        combo_type = ttk.Combobox(width=15)
        combo_type['values'] = ('レンタルCD', 'レンタルDVD')
        combo_type['state'] = 'readonly'
        combo_type.grid(column=1, row=1, pady=20)

        # 都道府県
        lbl_prefec = Label(text='都道府県').grid(column=0, row=2, padx=10, pady=20)
        combo_prefec = ttk.Combobox(width=15)
        combo_prefec['values'] = ('東京都', '神奈川県', '千葉県', '埼玉県')
        combo_prefec['state'] = 'readonly'
        combo_prefec.grid(column=1, row=2, pady=20)

        # 処理開始ボタン
        self.start_btn = Button(text='START', width=23, height=5,
                                command=lambda: self.btn_click(txt_item_id.get(), combo_type.current(),
                                                               combo_prefec.current()))
        self.start_btn.grid(column=0, row=3, padx=10, columnspan=2)

        # 進行メッセージ表示ボックス
        self.msg_textbox = Text(width=43, height=1)
        self.msg_textbox.grid(row=0, column=2, padx=20, pady=20, sticky=W)

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
        printFrame.grid(column=2, row=1, padx=20, pady=20, rowspan=3, sticky=W)

        self.grid()  # 表示

    def scraping(self, item_id, item_type, prefecture_id):
        # ---ブラウザの起動---
        self.print_msg('ブラウザを起動しています…')
        driver = webdriver.PhantomJS()
        driver.implicitly_wait(10)  # 要素が見つかるまで10秒待機
        self.print_msg('ブラウザを起動しました')

        # ---商品名の取得（商品IDの正誤検知）---
        self.print_msg('商品名を取得しています…')
        item_url = 'https://store-tsutaya.tsite.jp/item/{0}/{1}.html'.format(item_type, item_id)
        driver.get(item_url)
        # WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'header')))  # タイトルが表示されるまで待つ
        item_html = driver.page_source
        item_soup = BeautifulSoup(item_html, 'html.parser')
        if item_soup.find('div', id='errorBlock') is not None:
            self.print_msg('商品ID、販売形式をもう一度確認してください')
            driver.quit()  # ブラウザを閉じる
            self.start_btn['state'] = NORMAL
            return

        item_title = item_soup.find('div', class_='header').find('h2').find('span').string
        self.print_msg('タイトル：{}　の在庫を検索します'.format(item_title))

        # 店一覧のページをsoupへ
        self.print_msg('店舗一覧を取得しています…')
        shop_search_url = 'https://store-tsutaya.tsite.jp/tsutaya/articleList?account=tsutaya&' \
                          'accmd=1&arg=https%3A%2F%2Fstore-tsutaya.tsite.jp%2Fitem%2F{0}%2F{1}' \
                          '.html&ftop=1&adr={2}' \
            .format(item_type, item_id, prefecture_id)
        driver.get(shop_search_url)
        # WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'txt_k f_left')))
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        self.print_msg('店舗一覧の取得が完了しました')

        # 掲載ページ数を求める
        search_result_num = soup.find(class_='txt_k f_left').string
        total_shop_num = int(search_result_num.split('件')[1].split('全')[-1])
        if total_shop_num % 20 == 0:
            lastpage = total_shop_num / 20
        else:
            lastpage = int(total_shop_num / 20) + 1

        cnt = 0  # 掲載されてる店舗数を数える

        self.print_msg('各店舗の在庫情報を取得します')
        # 中断可能にする
        self.start_btn['text'] = 'STOP'
        self.start_btn['state'] = NORMAL

        # ページごと処理
        for page in range(1, lastpage + 1):
            # stopボタンが押された
            if self.is_active is False:
                self.print_msg('作業を中断しました')
                return

            # 店舗一覧ページに戻る
            driver.get(shop_search_url)
            # driver.implicitly_wait(10)  # 更新待機

            # ページを更新
            driver.execute_script("ExecuteAjaxRequest('./articleList', 'account=tsutaya&accmd=1&" \
                                  "arg=https%3a%2f%2fstore-tsutaya.tsite.jp%2fitem%2f{0}%2f{1}.html" \
                                  "&searchType=True&adr={2}&pg={3}&pageSize=20&pageLimit=10000&" \
                                  "template=Ctrl%2fDispListArticle_g12', 'DispListArticle'); return false;" \
                                  .format(item_type, item_id, prefecture_id, page))
            # driver.implicitly_wait(10)  # 更新待機
            # time.sleep(5)  # 更新待機

            # ページのsoupを取得する
            p_html = driver.page_source
            p_soup = BeautifulSoup(p_html, 'html.parser')

            # ページに掲載されている全店舗のURL取得
            table = p_soup.find('div', id='DispListArticle').find('table')
            links = table.find_all('a')
            for link in links:
                # stopボタンが押された
                if self.is_active is False:
                    self.print_msg('作業を中断しました')
                    return
                shop_url = link.get('href')
                cnt += self.get_zaiko_info(driver, shop_url)  # 在庫情報を取得
                self.print_msg('{}店舗中　{}店舗の在庫確認が終わりました'.format(total_shop_num, cnt))

        self.print_msg('在庫情報の取得が終了しました。')
        driver.quit()  # ブラウザを閉じる
        self.start_btn['state'] = NORMAL

    def get_zaiko_info(self, driver, url):
        # urlを開いてsoupへ
        driver.get(url)
        # 店の名前が表示されるまで待つ
        # WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'green clearfix')))
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        # 店の名前と在庫情報を取得
        shop_name = soup.find('h3', class_='green clearfix').find('a').string
        zaiko = soup.find('div', class_='state').find('span').string

        # 取扱がない場合0をreturn、取扱がある場合はcsvに店名と在庫情報を書き込む
        if '－' in zaiko:
            return 1
        else:
            if '○' in zaiko:
                self.textField.insert('end', '{}では在庫があります'.format(shop_name))
            else:
                self.textField.insert('end', '{}では取扱していますが、現在在庫がありません'.format(shop_name))
            return 1

    def print_msg(self, text):
        """
        メッセージボックスに引数のtextを表示させる。表示後1秒待機する。
        :param text: str
        :return:
        """
        # メッセージボックスにすでに文字が存在していたら、削除
        if self.msg_textbox.get('1.0') != '':
            self.msg_textbox.delete('1.0', 'end')
        self.msg_textbox.insert('1.0', text)
        # すぐ切り替わってしまうので待つ
        time.sleep(1)


def main():
    # ウィンドウ作成
    root = Tk()
    root.title("在庫検索")
    root.geometry("540x420")
    root.resizable(0, 0)

    # アプリケーション実行
    app = ZaikoApp(root)
    app.mainloop()


if __name__ == '__main__':
    main()
