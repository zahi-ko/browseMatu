import re
import urllib.request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import os
import time
import logging

# TODO 考虑page

def collectLinks(pattern=None):
    links = [i.get_attribute("href") for i in driver.find_elements(By.TAG_NAME, 'a')]
    if pattern: matchlinks = [m.group(0) for m in (re.match(pattern, link) for link in links) if m]
    return matchlinks

def parseTable(d: webdriver):
    table = d.find_element(By.CLASS_NAME, 'newfont03')
    rows = table.find_elements(By.TAG_NAME, 'tr')

    for row in rows[2:]:
        cells = [i.find_element(By.TAG_NAME, 'div') for i in row.find_elements(By.TAG_NAME, 'td')]
        if cells[5].text == '100':
            return cells[-1].find_elements(By.TAG_NAME, 'span')[-1].find_element(By.TAG_NAME, 'a').get_attribute("href")

# 配置日志记录
logging.basicConfig(filename=r'C:\projects\python\checkElec\script.log', level=logging.INFO, format='%(asctime)s %(message)s', encoding='utf-8')


BASE_URL = "http://matu.uestc.edu.cn/aptat/user/login.action"
CLASS_URL = "http://matu.uestc.edu.cn/aptat/course/liststudentclass"
CLASSES_URL = f"http://matu.uestc.edu.cn/aptat/task/liststudenttaskgroup?_class.id={0}"
TASK_URL = f"http://matu.uestc.edu.cn/aptat/task/listTaskGroup_Task?taskGroup.id={0}"

CLASS_PATTERN = r'^http://matu\.uestc\.edu\.cn/aptat/task/liststudenttaskgroup\?_class\.id=(\d+)$'
TASKS_GROUP_PATTERN = r'^http://matu\.uestc\.edu\.cn/aptat/task/listTaskGroup_Task\?taskGroup\.id=(\d+)$'
TASK_PATTERN = r'^http://matu\.uestc\.edu\.cn/aptat/assignment/listttudenttaskgrouptaskassignmentforstudent\?taskGroupTask\.id=(\d+)$'


DRIVER_PATH = r"C:\webdrivers\edgedriver_win64\msedgedriver.exe"
SAVE_PATH = r"C:\Users\zahir\Downloads"

edgeOptions = Options()
# edgeOptions.add_argument("--headless")
# edgeOptions.add_argument("--disable-gpu")
edgeOptions.add_argument("--no-sandbox")
edgeOptions.add_argument("--disable-dev-shm-usage")

edgeService = Service(DRIVER_PATH)
driver = webdriver.Edge(service=edgeService, options=edgeOptions)

try:
    driver.get(BASE_URL)
    inputBox = {
        "name": driver.find_element(By.XPATH, '//*[@id="user.Login"]'),
        "passwd": driver.find_element(By.XPATH, '//*[@id="dologin_user_Password"]')
    }

    inputBox['name'].send_keys("Zahi")
    inputBox['passwd'].send_keys("Trapshitv22")

    submitIcon = driver.find_element(By.XPATH, '//*[@id="dologin"]/table/tbody/tr[2]/td/table/tbody/tr[5]/td/table/tbody/tr/td[2]/input')
    submitIcon.click()
    # time.sleep(1)

    driver.get(CLASS_URL)
    # time.sleep(1) #TODO 优化等待时间
    
    classlinks = collectLinks(CLASS_PATTERN)

    for i in classlinks:
        driver.get(i)
        grouplinks = collectLinks(TASKS_GROUP_PATTERN)

        for j in grouplinks:
            driver.get(j)
            taskslinks = collectLinks(TASK_PATTERN)

            for k in taskslinks:
                driver.get(k)
                code = parseTable(driver)
                if code:
                    driver.get(code)
                    time.sleep(0.5)
finally:
    time.sleep(5) # 等待文件下载完毕
    driver.quit()