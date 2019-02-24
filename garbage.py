# ライブラリ
from tkinter import *
from tkinter import ttk
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
import time
import os
import random
import threading


class ZaikoApp(ttk.Frame):

    def __init__(self, master=None):
        super().__init__(master)
        # ブラウザーを起動
        self.driver = webdriver.PhantomJS()
        self.create_widgets()

    def btn_click(self,item_id):
        thread = threading.Thread(target=self.scraping, args=(item_id,))
        thread.start()
        #self.scraping(item_id)

    def create_widgets(self):
        # 商品ID
        lbl_item_id = Label(text='商品ID').pack(padx=10, pady=20)  # ラベル
        txt_item_id = Entry(width=15)
        txt_item_id.pack(pady=20)

        # 処理開始ボタン
        self.start_btn = Button(text='START', width=23, height=5,
                           command=lambda:self.btn_click(txt_item_id.get()))
        self.start_btn.pack(padx=10)

        # 進行メッセージ表示
        self.msg_textbox = Text(width=43,height=1)
        self.msg_textbox.pack(padx=20,pady=20)

        self.pack()

    def print_msg(self,str):
        if self.msg_textbox.get('1.0') != '':
            self.msg_textbox.delete('1.0','end')
        self.msg_textbox.insert('1.0',str)

    def scraping(self,item_id):
        self.print_msg('スクレイピングを開始します')
        # 作品名の取得（商品IDの正誤検知）
        item_url = 'https://store-tsutaya.tsite.jp/item/{0}/{1}.html'.format('rental_cd', item_id)
        self.driver.get(item_url)
        self.print_msg('入力まち')
        '''
        # driver.implicitly_wait(10)
        time.sleep(10)
        item_html = self.driver.page_source
        item_soup = BeautifulSoup(item_html, 'html.parser')
        title = item_soup.find('div', class_='header')
        print(title)
        '''





def main():
    # ウィンドウ作成
    root = Tk()
    root.title("在庫検索")
    root.geometry("540x420")
    root.resizable(0,0)

    # アプリケーション部分作成
    app = ZaikoApp(root)
    app.mainloop()


if __name__ == '__main__':
    main()
