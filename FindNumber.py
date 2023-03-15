from ctypes import windll, byref, c_ubyte
from ctypes.wintypes import RECT, HWND
import numpy as np
import time


class FindNumber(object):
    def __init__(self):
        self.numbers = []

    def get_number_list(self, img_path):
        import cv2
        # 加载数字模板
        temps = []
        for i in range(10):
            temps.append(cv2.imread(f'Source/temple_numbers/{i}.png', cv2.IMREAD_GRAYSCALE))

        # 按下任意键退出识别
        # while cv2.waitKey(delay=100) == -1:
        im = cv2.imread(img_path)
        im_grayed = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        # im = im[157:655, 355:1148]
        # 提取指定画面中的数字轮廓
        gray = cv2.cvtColor(im, cv2.COLOR_BGRA2GRAY)
        # print('gray', gray)
        ret, thresh = cv2.threshold(im_grayed, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        contours = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[0]
        result = []
        for cnt in contours:
            [x, y, w, h] = cv2.boundingRect(cnt)
            print(x,y,w,h)
            # 按照高度筛选
            if 12 >= h >= 10:
                result.append([x, y, w, h])

        result.sort(key=lambda x: x[0])
        # print('result', result)
        numbers = []
        for x, y, w, h in result:
            # 在画面中标记识别的结果
            cv2.rectangle(im, (x, y), (x + w, y + h), (0, 0, 255), 1)
            digit = cv2.resize(thresh[y:y + h, x:x + w], (14, 22))
            res = []
            for i, t in enumerate(temps):
                score = cv2.matchTemplate(digit, t, cv2.TM_CCORR_NORMED)
                res.append((i, score[0]))
            res.sort(key=lambda x: x[1])
            cv2.putText(im, str(f"{res[-1][0]}"), (x, y+35), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0))
            cv2.imshow('Digits OCR Test', im)
            numbers.append(res[-1][0])
        print('numbers', numbers)
        self.numbers = numbers

    def get_number(self):
        number_count = len(self.numbers)
        number = 0
        if number_count <= 0:
            print('没有找到数字！')
            return number

        first_number = self.numbers[0]
        if first_number == 0:
            for i in range(number_count):
                current_number = self.numbers[i]
                if current_number != 0:
                    number += self.numbers[i] / 10 ** i

            number = round(number, number_count - 1)
        else:
            for i in range(number_count):
                current_number = self.numbers[i]
                if current_number != 0:
                    number += self.numbers[i] * 10 ** (number_count - (i + 1))
        print('number', number)
        return number
