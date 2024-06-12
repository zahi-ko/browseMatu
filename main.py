import os
import shutil
import requests
from requests.cookies import create_cookie

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options

import re
import time

def login(d: webdriver):
    """
    Logs into the website using the provided webdriver instance.

    Args:
        d (webdriver): The webdriver instance.

    Returns:
        webdriver: The updated webdriver instance after logging in.
    """
    d.get(BASE_URL)
    inputBox = {
        "name": d.find_element(By.XPATH, '//*[@id="user.Login"]'),
        "passwd": d.find_element(By.XPATH, '//*[@id="dologin_user_Password"]')
    }

    inputBox['name'].send_keys("Your username")
    inputBox['passwd'].send_keys("Your password")

    submitIcon = d.find_element(By.XPATH, '//*[@id="dologin"]/table/tbody/tr[2]/td/table/tbody/tr[5]/td/table/tbody/tr/td[2]/input')
    submitIcon.click()

    return d

def collectLinks(d: webdriver, pattern: str=None):
    """
    Collects links from a web page using a WebDriver instance.

    Args:
        d (webdriver): The WebDriver instance.
        pattern (str, optional): A regular expression pattern to match against the links. Defaults to None.

    Returns:
        set: A set of matched links.

    """
    matchlinks = set()
    initialURL = d.current_url

    maxpage = getMaxPage(d)
    if maxpage > 1:
        for i in range(1, maxpage + 1):
            d.get(turnPageURL(initialURL, i))
            links = [i.get_attribute("href") for i in d.find_elements(By.TAG_NAME, 'a')]
            if pattern: matchlinks.update(m.group(0) for m in (re.match(pattern, link) for link in links) if m)
    elif maxpage == 1:
        links = [i.get_attribute("href") for i in d.find_elements(By.TAG_NAME, 'a')]
        if pattern: matchlinks.update(m.group(0) for m in (re.match(pattern, link) for link in links) if m)

    d.get(initialURL)
    return matchlinks

def parseTable(d: webdriver):
    """
    Parses a table on a webpage and extracts specific information.

    Args:
        d (webdriver): The webdriver object representing the browser session.

    Returns:
        dict: A dictionary containing the parsed information. The dictionary has the following keys:
            - 'code': The code link extracted from the table. If not found, it is set to None.
            - 'id': The ID extracted from the table. If not found, it is set to None.
    """
    table = d.find_element(By.CLASS_NAME, 'newfont03')
    rows = table.find_elements(By.TAG_NAME, 'tr')
    res = dict()

    res['code'] = None
    res['id'] = None

    for row in rows[2:]:
        cells = [i.find_element(By.TAG_NAME, 'div') for i in row.find_elements(By.TAG_NAME, 'td')]
        if cells[5].text == '100':
            res['id'] = row.find_element(By.TAG_NAME, 'div').text
            res['code'] = cells[-1].find_elements(By.TAG_NAME, 'span')[-1].find_element(By.TAG_NAME, 'a').get_attribute("href")
            break
    

    return res

def getMaxPage(d: webdriver):
    """
    Get the maximum page number from a web page.

    Args:
        d (webdriver): The webdriver instance.

    Returns:
        int: The maximum page number. If no page number is found, returns 1.
    """
    page = d.find_element(By.XPATH, '//span[contains(@class, "right-text09")]').text
    return int(page) if page else 1

def turnPageURL(url: str, page: int):
    """
    Appends the page number to the given URL.

    Args:
        url (str): The base URL.
        page (int): The page number to be appended.

    Returns:
        str: The updated URL with the page number.

    Example:
        >>> turnPageURL("https://example.com/browse?category=books", 2)
        'https://example.com/browse?category=books&page=2'
    """
    return url + f"&page={page}"

def collectInfo(d: webdriver, url: str):
    """
    Collects information from a webpage using a Selenium WebDriver.

    Args:
        d (webdriver): The Selenium WebDriver instance.
        url (str): The URL of the webpage to collect information from.

    Returns:
        dict: A dictionary containing the collected information.
            - 'id': The ID of the item.
            - 'name': The name of the item.
            - 'description': The description of the item.
    """
    initURL = d.current_url
    info = dict()

    d.get(url)
    table = d.find_element(By.XPATH, '//body/div/table/tbody/tr[2]/td/table/tbody/tr[2]/td/fieldset/table')
    rows = table.find_elements(By.TAG_NAME, 'tr')

    info['id'] = rows[0].find_element(By.TAG_NAME, 'label').text
    info['name'] = d.find_element(By.TAG_NAME, 'legend').text
    info['description'] = rows[1].find_element(By.TAG_NAME, 'pre').text

    return info

def downloadFile(d: webdriver, url: str, path: str, name: str):
    """
    Downloads a file from the specified URL and moves it to the specified path with the given name.

    Args:
        d (webdriver): The webdriver instance.
        url (str): The URL of the file to download.
        path (str): The path where the downloaded file will be moved.
        name (str): The name of the downloaded file.

    Returns:
        None
    """
    d.get(url)
    time.sleep(1)

    filename = max([path + "\\" + f for f in os.listdir(path)], key=os.path.getctime)
    shutil.move(filename, os.path.join(path, name))

def recordTask(d: webdriver, taskid: str | int):
    """
    Records task information to a text file.

    Args:
        d (webdriver): The webdriver object.
        taskid (str | int): The ID of the task.

    Returns:
        None
    """
    if isinstance(taskid, int):
        taskid = str(taskid)
    taskurl = TASK_DETAIL_FORMAT.format(taskid)
    res = collectInfo(d, taskurl)

    with open(f"{res['id']}.txt", 'a', encoding='utf-8') as f:
        f.write(f"题目编号: {res['id']}\n")
        f.write(f"题目名称: {res['name']}\n")
        f.write(f"题目信息: {res['description']}\n")

def initialize():
    """
    Initializes the global variables and sets their initial values.

    This function sets the initial values for the global variables used in the program.
    It also initializes the web driver with the specified options.

    Global Variables:
    - BASE_URL: The base URL of the website.
    - CLASS_URL: The URL for retrieving the list of student classes.
    - CLASSES_URL: The URL for retrieving the list of student task groups for a specific class.
    - TASK_URL: The URL for retrieving the list of tasks for a specific task group.
    - CLASS_PATTERN: The regular expression pattern for matching the class URL.
    - TASKS_GROUP_PATTERN: The regular expression pattern for matching the task group URL.
    - TASK_PATTERN: The regular expression pattern for matching the task URL.
    - TASK_DETAIL_FORMAT: The URL format for retrieving the details of a specific task.
    - TASK_DETAIL_PATTERN: The regular expression pattern for matching the task detail URL.
    - DRIVER_PATH: The path to the web driver executable.
    - SAVE_PATH: The path to the directory where downloaded files will be saved.
    - driver: The web driver instance.

    Returns:
    None
    """
    global BASE_URL
    global CLASS_URL
    global CLASSES_URL
    global TASK_URL
    global CLASS_PATTERN
    global TASKS_GROUP_PATTERN
    global TASK_PATTERN
    global TASK_DETAIL_FORMAT
    global TASK_DETAIL_PATTERN

    global DRIVER_PATH
    global SAVE_PATH
    global driver

    BASE_URL = "http://matu.uestc.edu.cn/aptat/user/login.action"
    CLASS_URL = "http://matu.uestc.edu.cn/aptat/course/liststudentclass"
    CLASSES_URL = "http://matu.uestc.edu.cn/aptat/task/liststudenttaskgroup?_class.id={}"
    TASK_URL = "http://matu.uestc.edu.cn/aptat/task/listTaskGroup_Task?taskGroup.id={}"

    CLASS_PATTERN = r'^http://matu\.uestc\.edu\.cn/aptat/task/liststudenttaskgroup\?_class\.id=(\d+)$'
    TASKS_GROUP_PATTERN = r'^http://matu\.uestc\.edu\.cn/aptat/task/listTaskGroup_Task\?taskGroup\.id=(\d+)$'
    TASK_PATTERN = r'^http://matu\.uestc\.edu\.cn/aptat/assignment/listttudenttaskgrouptaskassignmentforstudent\?taskGroupTask\.id=(\d+)$'
    TASK_DETAIL_PATTERN = r'^http://matu\.uestc\.edu\.cn/aptat/task/taskdetail\?taskid=(\d+)&taskGroupTask\.id=(\d+)&taskGroup\.id=(\d+)$'

    TASK_DETAIL_FORMAT = "http://matu.uestc.edu.cn/aptat/task/taskdetail?taskid={}"

    DRIVER_PATH = r"Your edge driver path"
    SAVE_PATH = r"Your Path to Save Files"

    edgeOptions = Options()
    # edgeOptions.add_argument("--headless")
    # edgeOptions.add_argument("--disable-gpu")
    edgeOptions.add_argument("--no-sandbox")
    edgeOptions.add_argument("--disable-dev-shm-usage")

    edgeService = Service(DRIVER_PATH)
    driver = webdriver.Edge(service=edgeService, options=edgeOptions)


def main():
    """
    This is the main function that executes the browsing and downloading tasks.

    It performs the following steps:
    1. Initializes the program.
    2. Logs in to the website.
    3. Navigates to the class URL.
    4. Collects links to different classes.
    5. Iterates over each class link.
    6. Navigates to the class link.
    7. Collects links to different task groups.
    8. Iterates over each task group link.
    9. Navigates to the task group link.
    10. Collects links to different tasks and task details.
    11. Iterates over each task link.
    12. Navigates to the task link.
    13. Parses the table on the task page.
    14. Downloads the file associated with the task.
    15. Records the task as completed.
    16. Quits the driver.

    Note: The specific implementation details of each step are not provided in this code snippet.
    """
    initialize()
    try:
        driver = login(driver)

        driver.get(CLASS_URL)
        classlinks = collectLinks(driver, CLASS_PATTERN)

        for i in classlinks:
            driver.get(i)
            grouplinks = collectLinks(driver, TASKS_GROUP_PATTERN)

            for j in grouplinks:
                driver.get(j)
                taskslinks = collectLinks(driver, TASK_PATTERN)
                detailslinks = collectLinks(driver, TASK_DETAIL_PATTERN)

                for k in taskslinks:
                    driver.get(k)
                    res = parseTable(driver)

                    if res['code']:
                        downloadFile(driver, res['code'], SAVE_PATH, res['id'] + ".cpp")
                        recordTask(driver, res['id'])
    finally:
        driver.quit()

if __name__ == "__main__":
    main()