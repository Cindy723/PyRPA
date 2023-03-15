import cv2

# 读取图片并转为灰度图
gray = cv2.imread('./Source/temple_numbers/number_completed.png', cv2.IMREAD_GRAYSCALE)
# 二值化，cv2.THRESH_OTSU指定由函数判断阈值
ret, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY|cv2.THRESH_OTSU)
# 寻找轮廓
contours = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[0]
# print('contours', contours)
# 将符合要求的轮廓收集并从左到右排序
result = []
for cnt in contours:
    [x,y,w,h] = cv2.boundingRect(cnt)
    print(x, y, w, h)
    if 12 > h > 10:
        result.append([x,y,w,h])
result.sort(key=lambda x:x[0])
print(result)
# 按轮廓截取数字并缩放到14×20大小，导出
count = 0
for x, y, w, h in result:
    # 在灰度图中画出轮廓
    cv2.rectangle(gray, (x,y),(x+w,y+h),(0,0,255),1)
    res = cv2.resize(thresh[y:y+h, x:x+w], (14, 22))
    print(res)
    cv2.imwrite(f'Source/{count}.png', res)
    count += 1
    print(count)
# 保存轮廓图
cv2.imwrite("./Source/temple_numbers/draw_contours.png", gray)