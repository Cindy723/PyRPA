import subprocess
import threading
import pyautogui
import datetime as dt
import re
import sys
import time
import win32api
import xlrd
import os
import keyboard
import pyperclip
import tkinter
from tkinter import *
from tkinter import Tk, Label, ttk, StringVar
# import tkinter.messagebox as messagebox
import tkinter as tk
import win32con
import win32gui

import configparser
import glob2
# from win10toast import ToastNotifier
import shutil
import base64
import ctypes
import win32console
import win32ui
from playsound import playsound

'''https://pypi.org/project/PyAutoGUI/'''

'''
同样的，先安装python环境
https://www.python.org/ftp/python/3.10.1/python-3.10.1-amd64.exe
如果失效 点击这里 https://www.python.org/downloads/release/
我这里安装的3.10版本，cv2是用的pyhon3.9下的(3.10貌似不行)为了提升编程体验，建议使用pycharm并且使用虚拟环境  https://download.jetbrains.com.cn/python/pycharm-community-2021.3.exe
如果失效 点击这里 https://www.jetbrains.com/pycharm/ (选择Community版本已经足够使用)
用到了以下外部依赖包： 
pyautogui  opencv-python  pillow  pyperclip  xlrd   pywin32   glob2  keyboard playsound
如果还提示缺少其它库 安装即可
建议使用虚拟环境 打包也在虚拟环境进行 这样不用在系统里也装一遍库
'''

pyautogui.FAILSAFE = True  # 保护措施，避免失控`
pyautogui.PAUSE = 0  # 默认最小操作周期
'''
pyautogui.click(x,y,clicks ,interval=0.05,duration=0.01,button="left")
等同于下面三行
location = pyautogui.locateOnScreen("1.png")
x, y = pyautogui.center(location)
pyautogui.leftClick(x, y)
pyautogui.locateCenterOnScreen 返回中心点 location.x  location.y
pyautogui.locateOnScreen  返回顶点 location.top  location.left
....

https://summer.blog.csdn.net/article/details/84650938
'''

'''
hwnd = win32gui.FindWindow(lpClassName=None, lpWindowName=None)  # 查找窗口，不找子窗口，返回值为0表示未找到窗口
hwnd = win32gui.FindWindowEx(hwndParent=0, hwndChildAfter=0, lpszClass=None, lpszWindow=None)  # 查找子窗口，返回值为0表示未找到子窗口
win32gui.ShowWindow(hwnd, win32con.SW_SHOWNORMAL)
SW_HIDE：隐藏窗口并激活其他窗口。nCmdShow=0。
SW_SHOWNORMAL：激活并显示一个窗口。如果窗口被最小化或最大化，系统将其恢复到原来的尺寸和大小。应用程序在第一次显示窗口的时候应该指定此标志。nCmdShow=1。
SW_SHOWMINIMIZED：激活窗口并将其最小化。nCmdShow=2。
SW_SHOWMAXIMIZED：激活窗口并将其最大化。nCmdShow=3。
SW_SHOWNOACTIVATE：以窗口最近一次的大小和状态显示窗口。激活窗口仍然维持激活状态。nCmdShow=4。
SW_SHOW：在窗口原来的位置以原来的尺寸激活和显示窗口。nCmdShow=5。
SW_MINIMIZE：最小化指定的窗口并且激活在Z序中的下一个顶层窗口。nCmdShow=6。
SW_SHOWMINNOACTIVE：窗口最小化，激活窗口仍然维持激活状态。nCmdShow=7。
SW_SHOWNA：以窗口原来的状态显示窗口。激活窗口仍然维持激活状态。nCmdShow=8。
SW_RESTORE：激活并显示窗口。如果窗口最小化或最大化，则系统将窗口恢复到原来的尺寸和位置。在恢复最小化窗口时，应用程序应该指定这个标志。nCmdShow=9。
————————————————
原文链接：https://blog.csdn.net/zhuan_long/article/details/120953194
'''
#################################################################
# 全功能版本
#################################################################
DIR = os.path.dirname(__file__)  # 运行路径
CfgFile = "./PyRPA.ini"
config = configparser.ConfigParser()
config.read(CfgFile)

today = time.strftime("%Y%m%d", time.localtime())
log_file = 'PyRPA.log'
IconPath = r'C:\Windows\TEMP\ATO.ico'

mutex = threading.Lock()
ClassWindow = 'TkTopLevel'
WindowName = 'PyRPA'
MSGWindowName = 'AutoWorkMessage'
running = -1  # 1为运行 0 为停止 停止时判断越密集 退出越及时
offseted = False  # 之前是否使用偏移
moved = False  # 之前是否使用移动
JumpLine = -1  # 行跳转标识  可实现某些行间的循环 跳转后继续顺序执行
theme = 0  # 主题


def resource_path(relative_path):
    if getattr(sys, 'frozen', False):  # 是否Bundle Resource
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


#  @ 功能：调用系统命令的线程
#  @ 参数：[I] : InputCmd 输入的参数
#  @ 备注：针对后面在"命令"更换subprocess.Popen后控制台版本正常 但是普通版本报错的问题
def threadSysCMD(InputCmd):
    mylog('调用系统CMD 执行系统命令-->', InputCmd)
    ret = os.system(InputCmd)  # 打包后运行普通版本有窗口
    mylog("CMD 线程退出码：", ret)
    # subprocess.run(InputCmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8", timeout=1)  打包后不带控制台的无法运行


#  @ 功能：分析要做什么
#  @ 参数：[I] : PicName 图片名字  location 找到的图片位置
#  @ 备注：PicName用于防止传进来的位置为空的情况进行重找(小概率)
#         重新找3次 moveTo读不到位置会崩溃
def Analysis(PicName, location):
    global offseted, moved, JumpLine

    def ClickFilter():
        if PicName != 'None':
            pyautogui.moveTo(location.x, location.y, 0)

    mylog('-----> Analysis NowRowKey:', NowRowKey)
    mylog('-----> Analysis NowRowValue:', NowRowValue)
    local = 0
    # if running == 1:
    # if Filter():
    #     if location is not None and running == 1:
    #         mylog('位置非空，立即移动鼠标到图片中心点')
    #         pyautogui.moveTo(location.x, location.y, 0)
    #     else:
    #         mylog('！找到图后立即移动鼠标开启，但位置为空，重新查找')
    #         for Counter in range(0, 3):
    #             location = pyautogui.locateCenterOnScreen(PicName, confidence=0.9)
    #             if location is None and running == 1:
    #                 mylog('重找次数', Counter + 1, '/3')
    #             else:
    #                 mylog('重找成功')
    #                 pyautogui.moveTo(location.x, location.y, 0)

    while local < Key_Value_pair and running == 1:
        mylog('CMD:', NowRowKey[local], 'Value:', NowRowValue[local])
        if NowRowKey[local] == '左键':
            # pyautogui.click(location.x + OffsetX, location.y + OffsetY, clicks=int(NowRowValue[local]), interval=0,
            # duration=0, button='left')
            if offseted is True or moved is True:
                offseted = moved = False
                for i in range(0, int(NowRowValue[local])):  # 配合相对偏移点击
                    mylog("右键点击")
                    pyautogui.leftClick()
            else:
                ClickFilter()  # 偏移和移动都没使用过 在点击前判断图片坐标是否有效 否则盲点无意义
                for i in range(0, int(NowRowValue[local])):
                    mylog("右键点击")
                    pyautogui.leftClick()

        elif NowRowKey[local] == '右键':
            # pyautogui.click(location.x, location.y, clicks=int(NowRowValue[local]), interval=0, duration=0,
            # button='right') 
            if offseted is True or moved is True:
                offseted = moved = False
                for i in range(0, int(NowRowValue[local])):  # 配合相对偏移点击
                    mylog("右键点击")
                    pyautogui.rightClick()
            else:
                ClickFilter()  # 偏移和移动都没使用过 在点击前判断图片坐标是否有效 否则盲点无意义
                for i in range(0, int(NowRowValue[local])):
                    mylog("右键点击")
                    pyautogui.rightClick()

        elif NowRowKey[local] == '等待' or NowRowKey[local] == '延时':
            time.sleep(float(NowRowValue[local]))
        elif NowRowKey[local] == '输入':
            strtemp = pyperclip.paste()
            # mylog("上次剪切板内容：", strtemp)
            pyperclip.copy(str(NowRowValue[local]))
            time.sleep(0.2)
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.2)
            # mylog("恢复上次剪切板内容")
            pyperclip.copy(strtemp)
            # pyautogui.typewrite(str(NowRowValue[local]), interval=0.1)
        elif NowRowKey[local] == '按键':
            pyautogui.press(str(NowRowValue[local]))
        elif NowRowKey[local] == '滚动':
            pyautogui.scroll(int(NowRowValue[local]))
        elif NowRowKey[local] == '滑动':
            ClickFilter()
            Split = re.split('/', NowRowValue[local])
            mylog('滑动', Split)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            time.sleep(1)
            pyautogui.moveRel(xOffset=int(Split[0]), yOffset=int(Split[1]), tween=pyautogui.linear)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        elif NowRowKey[local] == '截屏':
            if os.path.exists('Screenshot') is not True:
                os.mkdir('Screenshot')
            ShotImgpath = 'Screenshot/Shot_' + f'{time.strftime("%m%d%H%M%S ")}.png'
            pyautogui.screenshot().save(ShotImgpath)
        elif NowRowKey[local] == '热键':
            ReplaceStr = NowRowValue[local].replace('=', '+')
            ReplaceStr = ReplaceStr.replace('+', '-')
            Split = re.split('-', ReplaceStr)
            if len(Split) == 2:
                pyautogui.hotkey(Split[0], Split[1])
            elif len(Split) == 3:
                pyautogui.hotkey(Split[0], Split[1], Split[2])
        elif NowRowKey[local] == '命令':
            threading.Thread(target=threadSysCMD, args=(NowRowValue[local],)).start()
            # subprocess.Popen(NowRowValue[local], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # return proc.stdout.read().decode()
            # res = os.popen(NowRowValue[local])
            # output_str = res.read()
            # mylog(output_str)
        elif NowRowKey[local] == '中键':
            pyautogui.middleClick()
        elif NowRowKey[local] == '移动':
            moved = True
            Split = re.split('/', NowRowValue[local])
            mylog('移动鼠标到', Split)
            pyautogui.moveTo(int(Split[0]), int(Split[1]), 0)
        elif NowRowKey[local] == '偏移':  # 相对位移 +X向右 +Y向下  负值相反
            ClickFilter()
            offseted = True
            Split = re.split('/', NowRowValue[local])
            mylog('鼠标相对移动', Split)
            pyautogui.moveRel(xOffset=int(Split[0]), yOffset=int(Split[1]), tween=pyautogui.linear)
        elif NowRowKey[local] == '鼠标拖拽':  # 状态栏大多数情况不需要偏移拖拽
            ClickFilter()
            Split = re.split('/', NowRowValue[local])
            mylog('鼠标拖拽', Split)
            pyautogui.dragTo(x=int(Split[0]), y=int(Split[1]), duration=3, button='left')
        elif NowRowKey[local] == '相对拖拽':
            Split = re.split('/', NowRowValue[local])
            mylog('相对拖拽', Split)
            pyautogui.dragRel(xOffset=int(Split[0]), yOffset=int(Split[1]), duration=0.11, button='left',
                              mouseDownUp=True)
        elif NowRowKey[local] == '弹窗' or NowRowKey[local] == '提示':
            pyautogui.alert(text=NowRowValue[local], title=MSGWindowName)
            # tkinter.messagebox.showinfo(title='PyRPA: ', message=str(NowRowValue[local]))
        elif NowRowKey[local] == '左键按下':
            if offseted is True:
                offseted = False
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        elif NowRowKey[local] == '左键释放':
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        elif NowRowKey[local] == '右键按下':
            if offseted is True:
                offseted = False
            win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
        elif NowRowKey[local] == '右键释放':
            win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
        elif NowRowKey[local] == '跳转':
            JumpLine = int(NowRowValue[local])
            break
        elif NowRowKey[local] == '音频' or NowRowKey[local] == '音乐' or NowRowKey[local] == '播放':
            playsound(".\\Source\\" + NowRowValue[local])
        else:
            mylog('CMD:', NowRowKey[local], '!! 未知指令', NowRowKey[local])
            pyautogui.alert(text='CMD: ' + NowRowKey[local] + '!! 未知指令', title=MSGWindowName)
        local += 1
        time.sleep(0.01)


#  @ 功能：找图并执行动作
#  @ 参数：[I] :PicName 图片名字 timeout没找到循环找图的超时时间  interval下次找图的时间间隔
#  @ 备注：timeout 为0表示只找一次
def FindPicAndClick(PicName, timeout, outmethod, interval):
    ImgPath = (WorkPath + '\\' + PicName)
    if PicName != '' and os.path.exists(ImgPath) is True and running == 1:
        mylog(ImgPath, '图片有效')
        location = pyautogui.locateCenterOnScreen(ImgPath, confidence=0.9)
        ViewLog = True
        if location is not None:
            mylog(ImgPath, 'location is not None, Quick run')
            Analysis(ImgPath, location)
        else:
            BeginTime = time.time()
            while timeout >= 0 and location is None and running == 1:
                if ViewLog:
                    mylog(ImgPath, 'is not appear,waiting..(timeout > 0)')
                    ViewLog = False

                location = pyautogui.locateCenterOnScreen(ImgPath, confidence=0.9)
                time.sleep(interval)
                if time.time() - BeginTime > timeout:
                    mylog(ImgPath, 'waiting timeout !!!!')
                    mylog('超时方法： ' + outmethod)
                    if outmethod == '弹窗':  # pyautogui.alert和通知有冲突 通知后无法弹窗
                        pyautogui.alert(text=ImgPath + '查找超时', title=MSGWindowName)
                        # tkinter.messagebox.showinfo(title='PyRPA: ', message=str(ImgPath + '查找超时'), icon='error')
                        return outmethod
                    else:
                        return outmethod
            while timeout == -1 and location is None and running == 1:  # 一直找图 热键停止
                if ViewLog:
                    mylog(ImgPath, 'timeout = -1, is not appear,waiting..(timeout = -1)')
                    ViewLog = False

                location = pyautogui.locateCenterOnScreen(ImgPath, confidence=0.9)
                time.sleep(interval)

            mylog(ImgPath, 'appear,waiting succecs,run')
            Analysis(ImgPath, location)
    elif PicName == '':
        mylog(WorkPath, ' Excel中的图片名为空\n【以非找图模式运行】')
        Analysis('None', None)
    else:
        mylog(ImgPath, '！！图片无效，无法继续运行')
        pyautogui.alert(text=ImgPath + ' ！！图片无效，无法继续运行', title=MSGWindowName)


#  @ 功能：日志记录 调试时可以选择输出控制台
#  @ 参数：[I] :*BUF 输入的内容
LogOutMethod = 0


def mylog(*BUF):
    #  输出到文件
    if LogOutMethod == 1:
        with open(log_file, 'a') as log:
            print(dt.datetime.now().strftime('%F %T:%f'), file=log, end=' ')
            for i in BUF:
                print(i, file=log, end=' ')
            print('', file=log)

    # 输出到控制台
    elif LogOutMethod == 2:
        print(dt.datetime.now().strftime('%F %T:%f'), end=' ')
        for i in BUF:
            print(i, end=' ')
        print(end='\n')


Key_Value_pair = 0  # 键值对数
NowRowKey = []
NowRowValue = []
LineValue = ['', 'B', 'C', 'D', 'E', 'F', 'G']
CurrentROW = 1


# @功能：检查数据格式是否符合要求 不符合提示错误的单元格
# @备注：stype = 0  empty,  1 string,  2 number
def DataCheck(sheet):
    mylog('EXCEL数据校验')

    def ShowErroInfo():
        mylog('！第 ' + str(nowrow + 1) + ' 行 ' + LineValue[line] + ' 列 数据有问题，程序无法继续运行')
        pyautogui.alert(text='！第 ' + str(nowrow + 1) + ' 行 ' + LineValue[line] + ' 列 数据有问题，程序无法继续运行',
                        title=MSGWindowName)
        exit(-1)

    def ActionCheck(nowrow):
        Action = str(sheet.row(nowrow)[6].value)
        Action = Action.replace(',', '，')
        Action = Action.replace('“', '"')
        Action = Action.replace('”', '"')

        # mylog(nowrow+1, ' 等号次数', Action.count('='), '逗号次数', Action.count('，'))
        if Action.count('=') == Action.count('，') + 1:
            return True
        else:
            mylog('！第 ' + str(nowrow + 1), '行 动作队列异常')
            pyautogui.alert(text='！第 ' + str(nowrow + 1) + ' 行 ' + LineValue[line] + ' 列动作队列有问题，程序无法继续运行', title=MSGWindowName)
            return False

    for nowrow in range(1, sheet.nrows):
        # mylog('第 ', nowrow+1, ' 行')
        for line in range(1, 7):  # 判断各行的各列 程序是以0行开始 为用户显示的是实际表格
            stype = sheet.cell(nowrow, line).ctype
            # mylog(LineValue[line] +'列  数据类型 '+str(stype))
            if line == 1 and stype != 2:
                ShowErroInfo()
                return False
            elif sheet.row(nowrow)[1].value == 1 and sheet.row(nowrow)[2].value != '':  # 检查启用并且为找图模式的
                if line == 2 and stype != 1:
                    if stype != 0:
                        ShowErroInfo()
                        return False
                if line == 3 and stype != 2:
                    ShowErroInfo()
                    return False
                elif line == 4:
                    if int(sheet.row(nowrow)[3].value) != -1:
                        TempStr = str(sheet.row(nowrow)[line].value)
                        if not (TempStr == '弹窗'
                                or TempStr == '跳过'
                                or TempStr == '退出'
                                or (TempStr.find("跳转") != -1)):
                            ShowErroInfo()
                            return False
                if line == 5 and stype != 2:
                    ShowErroInfo()
                    return False
                if line == 6 and stype != 1:
                    ShowErroInfo()
                    return False
            else:
                # mylog('不检查非找图模式的行')
                break
        if ActionCheck(nowrow) is False:  # 数据类型如果检查通过 再检查执行动作队列
            return False
    return True


#  @ 功能：主要用于找图前的参数输入
#  @ 参数：[I] :sheet 表格的sheet
def workspace(sheet):
    global NowRowKey, NowRowValue, StatusText, Key_Value_pair, JumpLine, CurrentROW
    StatusText = '工作'
    if DataCheck(sheet) is True:
        mylog('数据校验通过')
    else:
        return
    CurrentROW = 1
    while CurrentROW < sheet.nrows and running == 1:
        if sheet.row(CurrentROW)[1].value == 1:  # 该行是否启用
            mylog('--------------work start--------------')
            mylog('EXCEL ROW ', CurrentROW + 1)
            SourceStr = sheet.row(CurrentROW)[6].value
            mylog('EXCEL Str: ', SourceStr)
            ReplaceStr = SourceStr.replace(',', '，')
            ReplaceStr = ReplaceStr.replace('，', '=')
            Split = re.split('=', ReplaceStr)

            i = 0
            Count = 0
            while Count < len(Split):
                NowRowKey.append(Split[Count])
                NowRowValue.append(Split[Count + 1])
                Count += 2
                i += 1
            Key_Value_pair = i
            ret = str(FindPicAndClick(PicName=sheet.row(CurrentROW)[2].value,
                                      timeout=sheet.row(CurrentROW)[3].value,
                                      outmethod=sheet.row(CurrentROW)[4].value,
                                      interval=sheet.row(CurrentROW)[5].value))
            mylog("FindPicAndClick ret=", ret)
            NowRowKey.clear()
            NowRowValue.clear()
            if ret == '退出':
                mylog('查找超时,退出整个查找')
                return ret

            if ret.find("跳转") != -1:
                Templist = re.split('=', ret)
                if len(Templist) > 0:
                    CurrentROW = int(Templist[1]) - 2  # 针对程序
                    mylog("由超时行为触发的跳转到第 ", int(Templist[1]), "行")  # 针对用户
                    if CurrentROW > sheet.nrows or CurrentROW < 0:
                        mylog("！请检查跳转参数")
                        pyautogui.alert(text='！请检查跳转参数', title=MSGWindowName)
                        return -1
        else:
            mylog("EXCEL ROW", CurrentROW + 1, '未启用操作')

        if JumpLine != -1:
            mylog("由动作触发的跳转到第 ", JumpLine, "行")
            CurrentROW = int(JumpLine) - 2
            JumpLine = -1
            if CurrentROW > sheet.nrows or CurrentROW < 0:
                mylog("！请检查跳转参数")
                pyautogui.alert(text='！请检查跳转参数', title=MSGWindowName)
                return -1
        CurrentROW += 1
    mylog('works end')


#  @ 功能：窗口控制
#  @ 参数：[I] :wClassName 窗口类名字 wCaption窗口名
#              action = -1 关闭窗口并结束所有任务 action=1显示  action=0最小化
#              已知bug：如果最小化窗口开始，将导致运行结束不能正常还原窗口
def WindowCtrl(wClassName, wCaption, action):
    hwnd = win32gui.FindWindow(wClassName, wCaption)
    if hwnd != 0:
        if action == -1:  # 暂不使用
            # mylog('执行窗口摧毁')
            win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
        elif action == 0:
            if win32gui.IsIconic(hwnd) is not True:
                # mylog('执行窗口最小化')
                win32gui.ShowWindow(hwnd, win32con.SW_SHOWMINIMIZED)
        # elif action == 1:
        #     if win32gui.IsIconic(hwnd):
        #         mylog('执行窗口还原')
        #         win32gui.ShowWindow(hwnd, win32con.SW_SHOWNORMAL)


#  @ 功能：开始热键绑定的事件
def begin_working():
    global running
    # mylog('热键按下 ：begin_working')
    WindowCtrl(ClassWindow, WindowName, 0)
    mutex.acquire()
    running = 1
    mutex.release()


#  @ 功能：结束热键绑定的事件
def finished_working():
    global running
    # mylog('热键按下 ：finished_working')
    WindowCtrl(ClassWindow, WindowName, 1)
    mutex.acquire()
    running = 0
    mutex.release()
    WindowCtrl(None, MSGWindowName, -1)


StatusText = ''


#  @ 功能：定期刷新显示左上角状态标签
class ViewSta(Frame):
    msec = 100  # 标签更新频率

    def __init__(self, parent=None, **kw):
        Frame.__init__(self, parent, kw)
        mutex.acquire()
        self._running = False
        mutex.release()
        self.str1 = StringVar()
        Lab = Label(self, textvariable=self.str1,  # 设置文本内容
                    width=0,  # 设置label的宽度
                    height=0,  # 设置label的高度
                    justify='left',  # 设置文本对齐方式：左对齐
                    anchor='nw',  # 设置文本在label的方位：西北方位
                    font=('宋体', 8),  # 设置字体，字号
                    fg='red',  # 设置前景色
                    bg='white',  # 设置背景色
                    padx=0,  # 设置x方向内边距
                    pady=0)  # 设置y方向内边距
        Lab.pack()
        self.flag = True

    def _update(self):
        self._setstr()
        self.timer = self.after(self.msec, self._update)

    def _setstr(self):
        self.str1.set(StatusText)

    def start(self):
        self._update()
        self.pack(side=TOP)


#  @ 功能：维持左上角标签的线程(基于窗口)
def ThreadShowLabelWindow():
    mylog("ThreadShowLabelWindow")
    root = Tk()
    root.overrideredirect(True)
    t = ViewSta(root)
    t.start()
    root.mainloop()


TotalTaskList = ['']  # 任务列表

ETLoop = None
ETStart = None
ETStop = None
LpCounter = 0
StartKey = ''
StopKey = ''
ListCfg = ['loopcounter', 'starthotkey', 'stophotkey']  # 下拉栏是独立的
XlsSource = None
WorkPath = ''


def KillSelf():
    # subprocess.Popen("taskkill /f /t /im PyRPA.exe", stdin=subprocess.PIPE, stdout=subprocess.PIPE,
    #                  stderr=subprocess.PIPE)
    # subprocess.Popen("taskkill /f /t /im PyRPA-c.exe", stdin=subprocess.PIPE, stdout=subprocess.PIPE,
    #                  stderr=subprocess.PIPE)
    TempPath = os.path.dirname(DIR)
    mylog("TempPath: ", TempPath)
    for root, dirs, files in os.walk(TempPath):
        if "_MEI" in root and DIR not in root:
            try:
                mylog("删除", root)
                shutil.rmtree(root)
            except:
                pass
        else:
            pass

    subprocess.call("taskkill /f /t /im PyRPA.exe")
    subprocess.call("taskkill /f /t /im PyRPA-c.exe")


#  @ 功能：显示主界面和处理事件
def ThreadShowUIAndManageEvent():
    global TotalTaskList, g_fg, ETLoop, ETStart, ETStop, LpCounter, StartKey, StopKey, XlsSource, theme
    mylog("ThreadShowUIAndManageEvent")
    Top = tk.Tk()
    Top.title(WindowName)  # 窗口标题
    Top.tk.call("source", "sun-valley.tcl")  # 加载主题
    # Top.tk.call("set_theme", "light")
    # Top.tk.call("set_theme", "dark")
    Top.geometry("350x295+10+16")
    # Top.resizable(False, False)  # 固定大小
    Top.minsize(350, 295)  # 最小尺寸
    Top.maxsize(450, 395)  # 最大尺寸
    Top.iconbitmap(IconPath)
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
    # 调用api获得当前的缩放因子
    ScaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0)
    # 设置缩放因子
    mylog('当前系统缩放：', ScaleFactor, ' %')
    if ScaleFactor > 100:
        ComboxWidth = 24 - int(24 * (ScaleFactor-100)/100)
    else:
        ComboxWidth = 24
    Top.tk.call('tk', 'scaling', ScaleFactor / 85)
    #   ----------数据源下拉菜单----------
    Combobox_1 = ttk.Combobox(Top, values=TotalTaskList, width=ComboxWidth, height=30)  # 创建下拉菜单
    # Combobox_1.grid(padx=140, pady=12)
    Combobox_1.place(x=140, y=12)
    # noinspection PyBroadException
    try:
        Option = config.get('SAVE', 'optionselect')
        mylog('恢复上次下拉菜单上次选择的第', int(Option), '项')  # 如果用户改变文件夹名字和数量可能导致不准确 需重新建立索引
    except Exception as e:
        mylog('配置文件[SAVE].optionselect 读取出错')
        Option = 0
    if int(Option) != 0:
        if len(TotalTaskList) - 1 < int(Option):
            mylog('！Option小于配置文件的[SAVE].optionselect，原因是先前的文件夹可能被删除，默认选择第0个')
            Option = 0
    Combobox_1.current(Option)

    def UpdataCurrentXls():  # 当前表格重定向
        global XlsSource
        global WorkPath
        WorkPath = '.\\Source\\' + Combobox_1.get()

        FilesList = os.listdir(WorkPath)
        for k in range(len(FilesList)):
            FilesList[k] = os.path.splitext(FilesList[k])[1]

        if '.xls' not in FilesList:
            mylog('！路径' + WorkPath + ' 下可能没有任务表，程序无法继续运行，\n请添加表格或者删除任务文件夹')
            pyautogui.alert(text='！路径' + WorkPath + ' 下可能没有任务表，程序无法继续运行，\n请添加表格或者删除任务文件夹', title=MSGWindowName)
            # tkinter.messagebox.showinfo(title='PyRPA: ', message='！路径' + WorkPath + '下可能没有任务表，程序无法继续运行，\n请添加表格或者删除任务文件夹', icon='error')
            KillSelf()
        NowDirXlsPath = glob2.glob(WorkPath + '\\*.xls')[0]  # 弱水三千只取一瓢饮
        if os.path.exists(NowDirXlsPath) is not True:
            mylog('！' + NowDirXlsPath + ' 不存在，程序无法继续运行')
            pyautogui.alert(text='！' + NowDirXlsPath + ' 不存在，程序无法继续运行', title=MSGWindowName)
            # tkinter.messagebox.showinfo(title='PyRPA: ', message='！' + NowDirXlsPath + '不存在，程序无法继续运行', icon='error')
            KillSelf()
        else:
            mylog('任务路径更新:', NowDirXlsPath)
            XlsSource = xlrd.open_workbook(filename=NowDirXlsPath).sheet_by_index(0)

    def SourceSelectFunc(event):  # 触发下拉菜单栏事件 写入选择的列表到配置文件
        CurrentLine = TotalTaskList.index(Combobox_1.get())  # 获取选择的项在整个列表位置
        config.set("SAVE", "optionselect", str(CurrentLine))
        for choose in config.keys():
            # print("[{s}]".format(s=choose))
            with open(CfgFile, "w+") as file:
                config.write(file)
        UpdataCurrentXls()

    UpdataCurrentXls()  # 先打开上次的表
    SelectedWork = Combobox_1.get()
    mylog('当前工作目录', SelectedWork)
    Combobox_1.bind("<<ComboboxSelected>>", SourceSelectFunc)
    # ###

    #   ----------日志设置下拉菜单----------
    LogMethodList = ['不记录日志', '记录在文件', 'Debug']
    Combobox_2 = ttk.Combobox(Top, values=LogMethodList, width=ComboxWidth, height=30)  # 创建下拉菜单
    # Combobox_2.grid(padx=140, pady=0)
    Combobox_2.place(x=140, y=60)
    Option = config.get('SAVE', 'logmethod')
    if int(Option) < 3:
        mylog('恢复上次日志记录下拉菜单:', LogMethodList[int(Option)])
        Combobox_2.current(int(Option))
        LogOutMethod = Option
        mylog('LogOutMethod ', LogOutMethod)

    def LogMethodSelectFunc(event):  # 触发下拉菜单栏事件 写入选择的列表到配置文件
        global LogOutMethod
        CurrentLine = LogMethodList.index(Combobox_2.get())  # 获取选择的项在整个列表位置
        config.set("SAVE", "logmethod", str(CurrentLine))
        for choose in config.keys():
            # print("[{s}]".format(s=choose))
            with open(CfgFile, "w+") as file:
                config.write(file)
        LogOutMethod = CurrentLine
        mylog('日志记录更新：', LogMethodList[CurrentLine])

    Combobox_2.bind("<<ComboboxSelected>>", LogMethodSelectFunc)
    # ###

    theme = int(config.get("SAVE", 'theme'))
    if theme == 0:  # 默认白色主题
        Top.tk.call("set_theme", "light")
        g_fg = "#000000"
    elif theme == 1:  # 暗黑
        Top.tk.call("set_theme", "dark")
        g_fg = "#E8E8E8"
    Label_y_base = 16
    Lab = tk.Label(Top, text="工作数据:", font=("宋体", 14), fg=g_fg)
    Lab.place(x=20, y=Label_y_base)

    Lab = tk.Label(Top, text="日志记录:", font=("宋体", 14), fg=g_fg)
    Lab.place(x=20, y=Label_y_base + 46 * 1)

    Lab = tk.Label(Top, text="循环次数:", font=("宋体", 14), fg=g_fg)
    Lab.place(x=20, y=Label_y_base + 46 * 2)

    # Lab = tk.Label(Top, text="次", font=("宋体", 13), fg=g_fg)
    # Lab.place(x=210, y=Label_y_base + 46 * 2)
    Lab = tk.Label(Top, text="(-1为一直循环)", font=("宋体", 9), fg="#A0A0A0")
    Lab.place(x=223, y=Label_y_base + 46 * 2 + 8)

    Lab = tk.Label(Top, text="启动热键:", font=("宋体", 14), fg=g_fg)
    Lab.place(x=20, y=Label_y_base + 46 * 3)

    Lab = tk.Label(Top, text="停止热键:", font=("宋体", 14), fg=g_fg)
    Lab.place(x=20, y=Label_y_base + 46 * 4)

    Entry_y_base = 105
    # ETLoop = Entry(Top, bd=1)
    # ETLoop.place(x=145, y=Entry_y_base, width=50)
    ETLoop = ttk.Entry(Top)
    ETLoop.place(x=140, y=Entry_y_base, width=80, height=30)

    # ETStart = Entry(Top, bd=1)
    # ETStart.place(x=145, y=Entry_y_base + 46 * 1, width=162)
    ETStart = ttk.Entry(Top)
    ETStart.place(x=140, y=Entry_y_base + 45 * 1, width=175, height=30)

    # ETStop = Entry(Top, bd=1)
    # ETStop.place(x=145, y=Entry_y_base + 46 * 2, width=162)
    ETStop = ttk.Entry(Top)
    ETStop.place(x=140, y=Entry_y_base + 45 * 2, width=175, height=30)

    # switch = ttk.Checkbutton(Top, text="Switch", style="Switch.TCheckbutton")
    # switch.place(x=140, y=Entry_y_base + 45 * 2)

    # 先拿出之前的配置，启动先前的热键事件检测
    LpCounter = config.get("SAVE", ListCfg[0])
    StartKey = config.get("SAVE", ListCfg[1])
    StopKey = config.get("SAVE", ListCfg[2])
    mylog('恢复上次设置的循环次数，', LpCounter)
    ETLoop.insert("insert", LpCounter)
    mylog('恢复上次设置的开始热键，', StartKey)
    ETStart.insert("insert", StartKey)
    mylog('恢复上次设置的停止热键，', StopKey)
    mylog('-等待用户操作-')
    ETStop.insert("insert", StopKey)
    keyboard.add_hotkey(StartKey, begin_working)
    keyboard.add_hotkey(StopKey, finished_working)

    # 触发配置更新事件 读出输入框数据写入配置文件 同时更新热键绑定 下拉菜单是单独处理的
    def UpdataCfg():
        global LpCounter
        global StartKey
        global StopKey
        ListCfgValue = [ETLoop.get(), ETStart.get(), ETStop.get()]
        mylog('配置更新, ListCfg:', ListCfgValue)

        # 实时更新使用端
        LpCounter = ListCfgValue[0]
        StartKey = ListCfgValue[1]
        StopKey = ListCfgValue[2]

        keyboard.add_hotkey(StartKey, begin_working)
        keyboard.add_hotkey(StopKey, finished_working)
        for j in range(0, 3):
            config.set("SAVE", ListCfg[j], ListCfgValue[j])
        for List in ListCfg:
            for choose in config.keys():
                # print("[{s}]".format(s=choose))
                with open(CfgFile, "w+") as file:
                    config.write(file)
        UpdataCurrentXls()  # 运行时可以修改xls

    # mylog('窗口绘制完成，当前选中的任务  {}'.format(com.get()))
    def Bbegin():
        global running
        running = 1
        mylog('点击开始')
        WindowCtrl(ClassWindow, WindowName, 0)

    # 使用ttk时设置风格
    # s = ttk.Style()
    # s.configure('W.TButton', font=('Helvetica', 14))
    # time.sleep(0.6)
    # my_style.configure('W.TButton', background='#E0E0E0', font=('方正姚体', 14))

    #  使用tk样式
    # butt = tk.Button(Top, text="保存并刷新", width=15, height=1, font=("方正姚体", 11), fg="#E8E8E8", relief=RIDGE, command=UpdataCfg)
    # butt.place(x=25, y=250, width=120)
    butt = ttk.Button(Top, text="保存并刷新", style='W.TButton', command=UpdataCfg)
    butt.place(x=20, y=245, width=145)

    butt2 = ttk.Button(Top, text="点击开始", style='W.TButton', command=Bbegin)
    butt2.place(x=170, y=245, width=145)

    Top.protocol("WM_DELETE_WINDOW", KillSelf)
    Top.mainloop()


#  @ 功能：拿到文件夹列表
#  @ 参数：[I] :p 当前要查看的目录
def getDirList(p):
    p = str(p)
    if p == "":
        return []
    p = p.replace("/", "\\")
    if p[-1] != "\\":
        p = p + "\\"
    a = os.listdir(p)
    b = [x for x in a if os.path.isdir(p + x)]
    return b


#  @ 功能：解码base64图标
def WriteIcon():
    b64encodeIcon = "AAABAAEAgIAAAAEAIAAoCAEAFgAAACgAAACAAAAAAAEAAAEAIAAAAAAAAAABAMMOAADDDgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAC3g24At4NuALeDbgC3g24At4NuALeDbgC3g24At4NuALeDbgC3g24At4NuALeDbgC3g24At4NuAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAtoZtALeDbgC3g24Wt4NudbeDboC3g26At4NugLeDboC3g26At4NugLeDboC3g26At4NucLeDbg+3g24AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAC4hG0At4NuALeDblC3g278t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27kt4NuHreDbgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAALiEbgC2gm4At4NujLeDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbuG3g24et4NuAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAt4NuALeDbg63g27Et4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu4beDbh63g24AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAALmEbwC3g24At4NuMbeDbuu3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27ht4NuHreDbgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAwIpwALeDbgC3g25nt4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbuG3g24et4NuAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAC3g24At4NuA7eDbqO3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu4beDbh63g24AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAALeDbgC3g24at4Nu1reDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27ht4NuHreDbgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAt4NwALaDbgC2g24At4NuALeDbgC3g24At4NuALeDbgC3g24At4JuALiCbgC1hG8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAC3g24At4NuALeDbkW3g271t4Nu/7eD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bv+3g27/t4Nu/7eDbv+3g27/t4Nu4beDbh63g24AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAALeDbgC3g255t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g255t4NuAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAt4NuALeDbgC2gm0Ft4NuereDbve3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbuW3g26Ft4NuILeDbgC3g24AuIFvALaEbQAAAAAAAAAAAAAAAAAAAAAAAAAAALiFbAC3g24At4Nuc7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27ht4NuHreDbgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAt4NuALeDbnm3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbnm3g24AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAALeDbgC3g24AtoJtBbeDbnq3g273t4Nu/7eDbv+3g27/t4Nu/7eD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bv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbtG3g24nt4NuALaDbgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAC3g24At4NuALaCbQW3g256t4Nu97eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu4beDbh63g24AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAALiDbQC6hGcAt4NvALeDbjy3g27Rt4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27Rt4NuPbeDbgC1iG8At4NwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAt4NuALeDbgC2gm0Ft4NuereDbve3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eD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5P/i0sv/0LKm/8GVg/+4hXH/toFs/7eCbf+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7aBbP/IopL/8O3r//Hv7f/x7+3/8e/vfvbitgD71oAA+9aAAPvWgAD71oAA+9aAAPvWgAD71oAA+9aAAPvWgAD71oAA+9aAAPvWgAD71oAA+9aAAPvWgAD71oAA+9aAAPvWgAD71oAA+9aAAPvWgADgtnkAs39tKLeDbuW3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27lt4NuKreDbgAAAAAAAAAAALeDbgC3g26At4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7iEb/+hc1v/iWBG/4lgRv+JYEb/iWBG/4lgRv+JYEb/iWBG/4lgRv+IX0X/h15F/4deRf+HXkX/h15F/4ZcQ/+8p5n/8/Hw//Hv7f/w7ev/yKKS/7aBbP+3g27/t4Nu/7eCbf+8jHn/w5mI/7qIdP+2gmz/toJt/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/toFs/8iikv/w7ev/8e/t//Hv7v/058m/+9V9fvvWgID71oCA+9aAgPvWgID71oCA+9aAgPvWgID71oCA+9aAgPvWgID71oCA+9aAgPvWgID71oCA+9aAgPvWgID71oCA+9aAgPvWgID71oCA+9aAgP3ZgX3WqHamt4Nu/beDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv23g25bt4NuAAAAAAAAAAAAt4NuALeDboC3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/uIRv/6ByWv+IYEX/iWBG/4lgRv+JYEb/iWBG/4lgRv+JYEb/iWBG/4lgRv+JYEb/iWBG/4lgRv+JYEb/h15D/72omv/z8fD/8e/t//Dt6//IopL/toFs/7eDbv+3g27/t4Nu/7eDbf+2gm3/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+2gWz/yKKS//Dt6//x7+3/8e/v//bitv/71n7/+9aA//vWgP/71oD/+9aA//vWgP/71oD/+9aA//vWgP/71oD/+9aA//vWgP/71oD/+9aA//vWgP/71oD/+9aA//vWgP/71oD/+9aA//vWgP/71oD//NeA/9uveP+2gm7/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbnm3g24AAAAAAAAAAAC3g24At4NugLeDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+4hG//oHJa/4hgRf+JYEb/iWBG/4lgRv+JYEb/iWBG/4lgRv+JYEb/iWBG/4lgRv+JYEb/iWBG/4lgRv+HXkP/vaia//Px8P/x7+3/8O3r/8iikv+2gWz/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+2gm3/t4Nt/7eDbv+3g27/t4Nu/7aBbP/IopL/8O3r//Hv7f/x7+//9uK2//vWfv/71oD/+9aA//vWgP/71oD/+9aA//vWgP/71oD/+9aA//vWgP/71oD/+9aA//vWgP/71oD/+9aA//vWgP/71oD/+9aA//vWgP/71oD/+9aA//vWgP/814D/2694/7aCbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4NuebeDbgAAAAAAAAAAALeDbgC3g26At4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7iEb/+hc1v/iWBG/4lgRv+JYEb/iWBG/4lgRv+JYEb/iWBG/4lgRv+IX0b/iF9F/4hfRf+IX0X/iF9F/4ZdQ/+8p5n/8/Hw//Hv7f/w7ev/yKKS/7aBbP+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7aCbf+2gmz/uYdz/8KYh/+8jHn/t4Jt/7eDbv+3g27/toFs/8iikv/w7ev/8e/t//Hv7v/058m/+9V9fvvWgID71oCA+9aAgPvWgID71oCA+9aAgPvWgID71oCA+9aAgPvWgID71oCA+9aAgPvWgID71oCA+9aAgPvWgID71oCA+9aAgPvWgID71oCA+9aAgP3ZgX3WqHamt4Nu/beDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv23g25bt4NuAAAAAAAAAAAAt4NuALeDboC3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/uIRv/6R0Xf+JYEb/iWBG/4lgRv+JYEb/iWBG/4lgRv+JYEb/imFG/5hvTv+ddVH/nXVQ/511UP+ddVD/nHNO/8eynv/y8e//8e/t//Dt6//IopL/toFs/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Jt/7aBbP+4hXD/wJSC/9CxpP/h0cr/7efk/8+vov+2gmz/t4Nu/7eDbv+2gWz/yKKS//Dt6//x7+3/8e/t//Hv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AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAC3g24At4NuALeDbwW3g256t4Nu97eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu5beDboW3g24gt4NuALeDbgC4gW8AtoRtAAAAAAAAAAAAAAAAAAAAAAAAAAAAuIVsALeDbgC3g25zt4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbuG3g24et4NuAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAC3g24At4NuebeDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4NuebeDbgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAC3g24At4NuALeDbwW3g256t4Nu97eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu8beDbp63g24ywX5zALeDbgC4hG0AuINtAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAC3g24At4NuALeDbju3g27xt4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu4beDbh63g24AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAALeDbgC3g255t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g255t4NuAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAC3g24At4NuALeDbwW3g256t4Nu97eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu+reDbri3g25ItoNtBbeDbgC4g24AuINuAICAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAC3g24At4NuE7eDbs23g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27ht4NuHreDbgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAt4NuALeDbly3g279t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/beDblu3g24AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAC3g24At4NuALeDbwW3g256t4Nu97eDbv+3g27/t4Nu/7eDbs63g25ht4NuDreDbgC3g24At4NtALeEbwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAALeDbgC5hnAAt4NumLeDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbuG3g24et4NuAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAC3g24At4NuKreDbuW3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27lt4NuKreDbgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAC3g24At4NuALeDbwW3g256t4Nu9reDbuC3g257t4NuG7eDbgC3g24At4JvALeEbQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAt35oALeDbgC3g25bt4Nu/LeDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu4beDbh63g24AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAALeDbgC4gm4Dt4NumLeDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbpe2g24DtoNuAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA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AAAAAAAAAAAAAAAAAAC4g20AuoNqALeDbgC3gm4Dt4NuKreDbly3g255t4NuebeDbly3g24qt4JvA7eDbgC3jWgAt4VtAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAt4NuALeDbhq3g27Wt4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbuG3g24et4NuAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAC4g20At4NuALeDbgC3g24At4NuALeDbgC3g24At4NuALeDbgC3g28At4JvALaDbAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAC3g24At4NuA7eDbqO3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu4beDbh63g24AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMCKcAC3g24At4NuZ7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27ht4NuHreDbgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAuYRvALeDbgC3g24xt4Nu67eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbuG3g24et4NuAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAt4NuALeDbg63g27Et4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu4beDbh63g24AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAC4hG4AtoJuALeDboy3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27ht4NuHreDbgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAALiEbQC3g24At4NuULeDbvy3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbv+3g27/t4Nu/7eDbuS3g24et4NuAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAtoZtALeDbgC3g24Wt4NudbeDboC3g26At4NugLeDboC3g26At4NugLeDboC3g26At4NucLeDbg+3g24AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAt4NuALeDbgC3g24At4NuALeDbgC3g24At4NuALeDbgC3g24At4NuALeDbgC3g24At4NuALeDbgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA//////////////////////////////AAP//////////////////gAD//////////////////4AA//////////////////+AAP//////////////////gAD//////////////////wAA//////////////////8AAP//////////////////AAD//////////////////wAA///8AD////////////4AAP//+AAf////////D//+AAD///AAD////////gf//gAA///gAAf///////wB//wAAP//4AAH///////4AH/8AAD//+AAB///////8AAf/AAA///gAAf//////+AAB/wAAP//4AAH///////AAAP4AAD//+AAB///////gAAA+AAA///gAAf//////wAAAAAAAP//4AAH//////4AAAAAAAD//+AAB//////8AAAAAAAA///gAAf/////+AAAAAAAAP//4AAH//////AAAAAAAAD//+AAB//////gAAAAAAAA///wAA//////wAAAAAAAAP//+AAf/////4AAAAAAAAD///wAP/////+AAAAAAAAA////gf//////gAAAAAAAAP///4H//////4AAAAAAAAD///+B///////AAAAAAAAA////gf//////4AAAAAAAAP///4H//////+AAAAAAAAD///+B/gB////wAAAAAAAAAwH/gfwAP///8AAAAAAAAAMB/4HwAA////gAAAAAAAADAf+B8AAP///4AAAAAAAAAwH/geAAB////AAAAAAAAAMB/4HgAAf///wAAAAAAAADAf+B4AAH///+AAAAAAAAAwH/geAAB////wAAAAAAAAAAA4HgAAf///8AAAAAAAAAAAOB4AAH////gAAAAAAAAAADgeAAB////4AAAAAAAAAAAAHgAAf///+AAAAAAAAAAAABwAAH////gAAAAAAAAAAAAYAAB////4AAAAAAAAAAAAEAAAf///4AAAAAAAAAAAAAAAAP///gAAAAAAAAAAAAAAAAD///AAAAAAAAAAAAAAAAAD//8AAAAAAAAAAAAAPgAAB//wAAAAAAAAAAAAADwAH///4AAAAAAAAAAAAAAAAD///+AAAAAAAAAAAAAAAAB////gAAAAAAAAAAAAAAAA////4AAAAAAAAAAAAAAAA//AA+AAAAAAAAAAAAAAAAf/gAHgAAAAAAAAAAAAAAAP/wAA4AAAAAAAAAAAAAAAH/4AAGAAAAAAAAAAAAAAP//+AABgAAAAAAAAAAAAAD///gAAYAAAAAAAAAAAAAAAAAAAAGAAAAAAAAAAAAAAAAAAAABgAAAAAAAAAAAAAAAAAAAAYAAAAAAAAAAAAAAAAAAAAGAAAAAAAAAAAAAAAAAAAABgAAAAAAAAAAAAAAAAAAAAYAAAAAAAAAAAAAA///4AAGAAAAAAAAAAAAAAP//+AABgAAAAAAAAAAAAAAAf/gAAYAAAAAAAAAAAAAAAD/8AAOAAAAAAAAAAAAAAAAf/gAHgAAAAAAAAAAAAAAAD/8AD4AAAAAAAAAAAAAAAAP///+AAAAAAAAAAAAAAAAB////gAAAAAAAAAAAAAAAAP///8AAAAAAAAAAAAAA8AB////8AAAAAAAAAAAAAPgAAB///8AAAAAAAAAAAAAAAAAP///4AAAAAAAAAAAAAAAAA////4AAAAAAAAAAAAAAAAP////gAAAAAAAAAAAAQAAB////4AAAAAAAAAAAAGAAAf///+AAAAAAAAAAAABwAAH////gAAAAAAAAAAAAeAAB////4AAAAAAAAAAA4HgAAf///8AAAAAAAAAAAOB4AAH////AAAAAAAAAAADgeAAB////gAAAAAAAAMB/4HgAAf///wAAAAAAAADAf+B4AAH///8AAAAAAAAAwH/geAAB///+AAAAAAAAAMB/4HgAAf///gAAAAAAAADAf+B8AAP///wAAAAAAAAAwH/gfAAD///8AAAAAAAAAMB/4H8AD///+AAAAAAAAD///+B/gB////gAAAAAAAA////gf//////wAAAAAAAAP///4H//////4AAAAAAAAD///+B//////+AAAAAAAAA////gf//////gAAAAAAAAP///4H//////4AAAAAAAAD///wAP//////AAAAAAAAA///4AB//////4AAAAAAAAP//8AAP//////AAAAAAAAD//+AAB//////4AAAAAAAA///gAAf//////AAAAAAAAP//4AAH//////4AAAAAAAD//+AAB///////AAAAAAAA///gAAf//////4AAAPgAAP//4AAH///////AAAP4AAD//+AAB///////4AAH/AAA///gAAf///////AAH/wAAP//4AAH///////4AH/8AAD//+AAB////////AH//AAA///gAAf///////4H//4AAP//4AAH////////D//+AAD///AAD////////////gAA///4AB////////////8AAP///AA/////////////AAD//////////////////wAA//////////////////8AAP//////////////////gAD//////////////////4AA//////////////////+AAP//////////////////gAD//////////////////8AA///////////////////////////////8= "
    img = base64.b64decode(b64encodeIcon)
    file = open(IconPath, 'wb')
    file.write(img)
    file.close()
 

#  @ 功能：禁用控制台应用的关闭窗口
#  @ 备注：因为控制台的关闭事件不好捕获，直接禁用掉
#  @      只允许使用主窗体的关闭来退出程序 在关闭事件中清除临时文件
#  @ 没有控制台不要使用
def DisableCloseButton():
    # pass
    h = win32console.GetConsoleWindow()
    if h is not None:
        wnd = win32ui.CreateWindowFromHandle(h)
        if wnd is not None:
            menu = wnd.GetSystemMenu()
            menu.DeleteMenu(win32con.SC_CLOSE, win32con.MF_BYCOMMAND)
autoruntaskdir = ''


#  @ 功能：全局初始化
def Initial():
    global LogOutMethod
    global StatusText
    global TotalTaskList
    global autoruntaskdir

    LogOutMethod = int(config.get('SAVE', 'logmethod'))
    autoruntaskdir = str(config.get('TASKCFG', 'autoruntaskdir'))
    mylog('Run path:', DIR)
    mylog('Execute File:', sys.argv[0])
    mylog('autoruntaskdir: ', autoruntaskdir)
    # 删除上次的运行文件放到程序关闭时  但-c版本需要关闭窗口才能删除文件 关闭控制台时文件将不会被清除 但下次正常关闭时可以删除之前运行的所有垃圾
    StatusText = '启动'
    if os.path.exists(IconPath) is not True:
        WriteIcon()
    # if os.path.exists(log_file) is True:
    #     os.remove(log_file)
    if os.path.exists('Source') is not True:
        mylog('! Source文件夹不存在，程序无法继续运行')
        # pyautogui.alert(text='Source文件夹不存在，程序无法继续运行', title=MSGWindowName)
        tkinter.messagebox.showinfo(title='PyRPA: ', message='Source文件夹不存在，程序无法继续运行', icon='error')
    else:
        TotalTaskList = getDirList('Source')
        mylog('当前Source文件夹内容(可选任务列表):', TotalTaskList)
    DisableCloseButton()


#  很多警告都是拼写相关 建议关掉这些不必要的警告
if __name__ == '__main__':
    Initial()
    RunCounter = 0
    threading.Thread(target=ThreadShowLabelWindow).start()
    threading.Thread(target=ThreadShowUIAndManageEvent).start()
    mylog(' ————————————————————————————————————————————')
    mylog('|欢迎使用自动化软件！  <程序版本V0.9.3>')
    mylog('|作者: Up主 "极光创客喵" chundong_cindy@163.com')
    mylog('|鸣谢: Up主"不高兴就喝水"')
    mylog(' ————————————————————————————————————————————\n')


    def MainWork():
        global StatusText
        global RunCounter
        if StartKey != '' and StopKey != '':
            keyboard.add_hotkey(StartKey, begin_working)
            keyboard.add_hotkey(StopKey, finished_working)
        mylog('等待热键按下,或点击开始')

        if autoruntaskdir != '':
            mylog('自动运行模式，运行任务文件夹：', autoruntaskdir)
            time.sleep(0.5)   # 这个等待非常重要 等待上面操作结束
            StatusText = '准备'
            begin_working()
            time.sleep(0.5)   # 这个等待非常重要 等待上面操作结束

        while running == -1:
            time.sleep(0.1)
            StatusText = '准备'

        time.sleep(0.5)  # 等待窗口退出
        RunCounter = int(LpCounter)
        if RunCounter == -1:
            mylog('进入一直循环')
            while running == 1:
                if workspace(XlsSource) == '退出':
                    break
        else:
            numCounter = 0
            totalCounter = RunCounter
            while RunCounter > 0 and running == 1:
                numCounter += 1
                mylog('\n【运行', numCounter, '/', totalCounter, '次 ↓】')
                if workspace(XlsSource) == '退出':
                    break
                RunCounter -= 1
        mylog('EXCEL遍历结束')
        if autoruntaskdir != '':
            mylog('自动模式运行结束 杀死自己')  # 调试模式下将不起作用
            KillSelf()

        # WindowCtrl(ClassWindow, WindowName, 1)  中间有弹窗还原将会有问题
        # 不使用还原，结束弹出通知(通知期间无法操作)
        # if int(config.get('SAVE', 'enablemessage')) == 1:
        #     toaster = ToastNotifier()
        #     toaster.show_toast(u'PyRPA', u'EXCEL遍历结束', icon_path=IconPath)


    while 1:
        mylog('*********************主循环*********************')
        mylog('*********************主循环*********************')
        mutex.acquire()
        running = -1
        mutex.release()
        MainWork()

