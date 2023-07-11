import time
from datetime import datetime
import threading
import sys
from tkinter import Tk, Label, Entry, Button, StringVar, Text, END, messagebox
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


class PageBot:
    PASS_XPATH = "/html/body/div[2]/div[2]/div/div[1]/div/div[2]/div[2]/div/input"
    INPUT_XPATH = "/html/body/div[2]/div[2]/div/div[1]/div/div[2]/div[3]/div/input"
    BUTTON_XPATHS = [
        "/html/body/div[2]/div[2]/div/div[1]/div/div[2]/button",
        # "/html/body/div[2]/div[2]/div/div[2]/div/div[1]/div[1]/div[8]/div[3]/div/div[2]/div/button"
    ]
    JOIN_XPATHS = [
        "/html/body/div[2]/div[2]/div/div[2]/div/div[1]/div[1]/div[4]/div[2]/div/div[2]/button",
        "/html/body/div[2]/div[2]/div/div[2]/div/div[1]/div[1]/div[4]/div[2]/div/div[2]/button[1]",
        "/html/body/div[2]/div[2]/div/div[2]/div/div[1]/div[1]/div[4]/div[2]/div/div[2]/button[2]",
        "/html/body/div[2]/div[2]/div/div[2]/div/div[1]/div[2]/div/div[2]/button[2]"
    ]
    JOIN_MES = [
        "参加許可準備",
        "参加許可準備",
        "1人の参加許可を実行",
        "複数人の参加許可を実行"
    ]

    def __init__(self, url, password, log_callback, name):
        self.url = url
        self.password = password
        self.log_callback = log_callback
        self.name = name
        self.exit_flag = False

    def stop_bot(self):
        self.log("終了実行中。時間がかかる場合があります。")
        self.exit_flag = True

    def stop_check(self):
        if self.exit_flag:
            self.driver.quit()
            sys.exit()

    def run_bot(self):
        self.log("Webドライバ生成中")
        options = Options()
        options.add_argument('--headless=new')
        options.add_argument('--enable-javascript')
        options.add_argument('incognito')
        service = Service(ChromeDriverManager().install())
        service.log_path = 'NULL'  # Disable logging
        service.command_line_args()  # Get args
        service.command_line_args().append('--silent')
        self.driver = webdriver.Chrome(options=options, service=service)
        self.wait = WebDriverWait(self.driver, 10)
        self.driver.get(self.url)
        self.driver.maximize_window()
        self.stop_check()
        self.log(f"指定されたURLを起動 {self.url}")
        self.log("入室操作をしています。")
        if self.password != "":
            self.pass_input()
        self.type_input()
        self.log("参加許可をしていない場合してください。")
        for btn_xpath in self.BUTTON_XPATHS:
            while not self.click_element(btn_xpath):
                self.stop_check()
                time.sleep(1)
        while True:
            try:
                button = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'コンピューターでオーディオに接続')]"))
                )
                time.sleep(1)
                button.click()
                break
            except:
                time.sleep(1)
        self.log("入室完了です。")
        self.log("こちらのアカウントに共同ホストを付与してください。")
        while not self.exit_flag:
            self.click_elements(self.JOIN_XPATHS)
        self.driver.quit()

    def pass_input(self):
        self.stop_check()
        input_element = self.wait.until(EC.presence_of_element_located((By.XPATH, self.PASS_XPATH)))
        self.log(f"パスワード入力完了")
        input_element.send_keys(self.password)

    def type_input(self):
        self.stop_check()
        input_element = self.wait.until(EC.presence_of_element_located((By.XPATH, self.INPUT_XPATH)))
        self.log(f"Zoom名:{self.name}で開始します。")
        input_element.send_keys(self.name)

    def click_element(self, xpath):
        try:
            element = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            element.click()
            return True
        except:
            return False

    def click_element2(self, xpath):
        try:
            element = self.driver.find_element(By.XPATH, xpath)
            element.click()
            return True
        except:
            time.sleep(1)
            return False

    def click_elements(self, xpath_list):
        i = 0
        for xpath in xpath_list:
            if self.click_element2(xpath):
                self.log(self.JOIN_MES[i])
            i += 1

    def log(self, message):
        self.log_callback(message)


class App:
    def __init__(self, window):
        window.geometry("576x436")  # ウィンドウサイズを固定
        window.resizable(False, False)  # ウィンドウのサイズ変更を無効化
        self.url_text = StringVar()
        self.url_text.set("Zoomの参加URLを入力して下さい")
        Label(window, text="URL:").grid(row=0, column=0, sticky='w')
        Entry(window, textvariable=self.url_text, width=82).grid(row=0, column=1)
        self.pass_text = StringVar()
        self.pass_text.set("ysd8010")
        Label(window, text="パスワード:").grid(row=1, column=0, sticky='w')
        Entry(window, textvariable=self.pass_text, width=82).grid(row=1, column=1)
        self.name_text = StringVar()
        self.name_text.set("ホスト用＠イヤホンなし")
        Label(window, text="Zoom名:").grid(row=2, column=0, sticky='w')
        Entry(window, textvariable=self.name_text, width=82).grid(row=2, column=1)
        self.run_button = Button(window, text="開始", command=self.run_bot)
        self.run_button.grid(row=3, column=0, padx=10, pady=10, sticky='ew')
        self.stop_button = Button(window, text="強制終了", command=self.stop_bot, state="disabled")
        self.stop_button.grid(row=3, column=1, padx=10, pady=10, sticky='ew')

        self.log_area = Text(window, bg='black', fg='white')
        self.log_area.grid(row=4, column=0, columnspan=2, sticky='ew')

        window.protocol("WM_DELETE_WINDOW", self.delete_window)

        self.bot = None

    def run_bot(self):
        self.log_area.delete("1.0", "end")
        url = self.url_text.get().replace("/j/", "/wc/join/")
        if not "/wc/join/" in url:
            self.log("正しいZoomのURLを入力してください。")
            return
        self.bot = PageBot(url, self.pass_text.get(), self.log, self.name_text.get())
        self.run_button.configure(state="disabled")  # 起動ボタンを無効化
        self.stop_button.configure(state="normal")  # 終了ボタンを有効化
        threading.Thread(target=self.bot.run_bot).start()

    def stop_bot(self):
        if self.bot:
            self.bot.stop_bot()
            self.log("終了しました。")
        self.run_button.configure(state="normal")  # 起動ボタンを有効化
        self.stop_button.configure(state="disabled")  # 終了ボタンを無効化

    def log(self, message):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_area.insert(END, f"{current_time}: {message}" + '\n')
        self.log_area.update_idletasks()

    def delete_window(self):

        # 終了確認のメッセージ表示
        ret = messagebox.askyesno(
            title="終了確認",
            message="プログラムを終了しますか？")

        if ret:
            self.stop_bot()
            window.destroy()
            sys.exit()


if __name__ == "__main__":
    window = Tk()
    window.title("ZoomEntryBot")
    window.iconbitmap(default='zoom.ico')
    App(window)
    window.mainloop()
