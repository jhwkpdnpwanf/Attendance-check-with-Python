import requests
import re

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
from seleniumwire import webdriver  
import time

options = webdriver.ChromeOptions()
driver = webdriver.Chrome(options=options, seleniumwire_options={
'connection_timeout': 30,
'request_timeout': 60,
})

URL = 'https://www.hongik.ac.kr/my/login.do?auty=LOGIN&referer=%2Fmy%2Findex.do%3Fauty%3D2'
driver.get(url=URL)

# 로그인
login_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'USER_ID')))
login_button.send_keys('*')

pw_button = driver.find_element(By.ID, 'PASSWD')
pw_button.send_keys('*')

login_box = driver.find_element(By.ID, 'btn-login')
login_box.click()

# 비밀번호 변경 경고 처리
WebDriverWait(driver, 10).until(EC.alert_is_present())
alert = driver.switch_to.alert
alert.accept()

URL = 'https://at.hongik.ac.kr/*.jsp'
driver.get(url=URL)


cookies = driver.get_cookies()
c1 = cookies

print(c1)

name_value_list = [{'name': cookie['name'], 'value': cookie['value']} for cookie in c1]

target_names = [
    "hongik_abeek_sso", "SUSER_ID", "SUSER_LOGID", "SUSER_NAME", "SUSER_GUBUN", "SUSER_AUTH",
    "SUSER_AUTHKEY", "SUSER_LOGKEY", "SUSER_USER", "pni_token", "SUSER_EXTAUTH",
    "SUSER_LAST", "SUSER_LAST_IP", "JSESSIONID", "SUSER_LIMIT"
]

filtered_cookies = {}
for cookie in name_value_list:
    if cookie['name'] in target_names:
        filtered_cookies[cookie['name']] = cookie['value']

cookies = "; ".join([f"{key}={value}" for key, value in filtered_cookies.items()])

print(cookies)

def update_value(b1, key, value):
    if re.search(rf"(&{key}=)", b1):
        b1 = re.sub(rf"(&{key}=)[^&]*", rf"&{key}={value}", b1)
    else:
        b1 += f"&{key}={value}"
    return b1

try:
    while True:
        try:
            td_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//td[@colspan='4']"))
            )
           
            if td_element.text == "출결입력 대상이 없습니다.":
                print("아직 출결입력 대상이 없다. 페이지를 새로고침함.")
                driver.refresh()
                time.sleep(8)  # 몇초간 대기할지 설절

        except Exception as e:
            try:
                print("출결입력 대상을 찾음. 페이지로 넘어갑니다.")      
                element = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//tr[@class='success']//td[text()='2024-2']"))
                )
                element.click()
                break
            except Exception as inner_exception:
                print("셀레니움으로 클릭에서 실패함 :", inner_exception)


except KeyboardInterrupt:
    print("프로그램이 중지되었습니다.")

try:
    input_element = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.ID, "key"))
    )

    #숫자
    input_element.clear()
    input_element.send_keys("0000")
    time.sleep(1)
    #제출버튼
    submit_button = WebDriverWait(driver, 3).until(
        EC.element_to_be_clickable((By.ID, 'btn_insert'))
    )
    submit_button.click()


except Exception as e:
    print("숫자입력중오류:", str(e))

time.sleep(3)


b1 = None

for request in driver.requests:
    if '*.jsp' in request.url:
        b1 = request.body.decode('utf-8', errors='ignore')
        print("Request Body : ", b1)
        break

def parse_headers_cookies(input_text):
    headers = {}
    cookies = {}

    lines = input_text.strip().split("\n")
    current_section = "headers"

    for line in lines:
        line = line.strip()
       
        if line.lower().startswith("cookie:"):
            current_section = "cookies"
            cookie_str = line.split(":", 1)[1].strip()
            cookie_pairs = cookie_str.split("; ")
            for pair in cookie_pairs:
                if "=" in pair:
                    key, value = pair.split("=", 1)
                    cookies[key] = value
        elif current_section == "headers" and ": " in line:
            key, value = line.split(": ", 1)
            headers[key] = value

    return headers, cookies

b1_len = len(b1)
input_text = f"""
POST /*.jsp HTTP/1.1
Accept: *
Accept-Encoding: *
Accept-Language: *
Cache-Control: *
Connection: *
Content-Length: {b1_len}
Content-Type: *
Host: *
Origin: *
Pragma: *
Referer: *
Sec-Fetch-Dest: *
Sec-Fetch-Mode: *
Sec-Fetch-Site: *
Sec-Fetch-User: *
Upgrade-Insecure-Requests: *
User-Agent: *
sec-ch-ua: "*"
sec-ch-ua-mobile: *
sec-ch-ua-platform: "*"
"""

input_text = input_text + f"\nCookie: {cookies}\n"
headers, cookies = parse_headers_cookies(input_text)


print("cookies: ", cookies)
print("headers: ", headers)
print("b1: ",b1)



url = "https://at.hongik.ac.kr/*.jsp"

def send_request(num, headers, cookies, b1):
    num_str = str(num).zfill(4)
    b1 = b1.replace("key=0000", f"key={num_str}")

    response = requests.post(url, headers=headers, cookies=cookies, data=b1)
    print(f"요청: 상태 코드 {response.status_code}, 전송된 key 값: {num_str}")

    if response.status_code != 200:
        print(f"Unexpected status code {response.status_code}.")
        return False

    return True

num = "1234" # 실제 출석번호
send_message = send_request(num, headers, cookies, b1)
print("출석입력 완료")

driver.quit()
