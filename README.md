# [Toy-Project] TCP request message를 수정하여 출석체크하기
&nbsp; <br>
*이 저장소의 코드는 **학습 목적**으로 제공되며, **악의적인 목적으로 사용을 절대 금지합니다.**  
만약 이 코드를 **불법적인 행위**에 악용할 경우, 그에 대한 모든 책임은 사용자 본인에게 있습니다.*  
<br><br><br>
데이터통신 수업을 듣던 중 tcp request message를 내 컴퓨터 내부에서 다른 값으로 바꿔서 보내는 것도 가능하지 않을까?라는 생각이 들었다.  

그래서 이를 실험해보기 위해 출석번호를 설정값으로 바꿔보기위해 코드를 짜보기로 했다.   

selenium은 이전에 관심이 있어 다뤄본 적이 있어서 selenium을 통해 자동화를 시켜보았다.  
<br><br>
### bash
```bash
pip install selenium selenium-wire requests json5
```
tcp 요청을 수정하기 위해서는 selenium이 아닌 selenium-wire를 사용해야한다.  
<br>
### 로그인
```python
login_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'USER_ID')))
login_button.send_keys('*')

pw_button = driver.find_element(By.ID, 'PASSWD')
pw_button.send_keys('*')

login_box = driver.find_element(By.ID, 'btn-login')
login_box.click()
```  
우선 로그인을 해준다.   
해당 요소가 나올 때까지 기다릴 수 있도록 WebDriverWait을 써주는게 편리하다.   
<br>
```python
WebDriverWait(driver, 10).until(EC.alert_is_present())
alert = driver.switch_to.alert
alert.accept()
```
비밀번호 경고처리도 없애주고  
<br>

```python
URL = 'https://at.hongik.ac.kr/stud01.jsp'
driver.get(url=URL)
```
로그인을 했다면 해당 웹페이지에는 본인의 쿠기값이 저장되어 있기에 바로 출석확인 페이지로 넘어간다.   
<br>
```python
cookies = driver.get_cookies()
c1 = cookies
```
해당 페이지에서 쿠키값을 얻어주고 이름과 값을 따로 파싱해준다.  
<br>
로그인 페이지가 아닌 출석확인 페이지에서 쿠키값을 얻은 이유는 두 페이지가 요구하는 쿠키가 다르기 때문이다. 
실제 출석확인 페이지에서 요구하는 쿠키는 현재 페이지에서 요구하는 쿠키와 같다.  
<br>
(stud01.jsp, stud02.jsp, stud03.jsp, stud04.jsp 페이지로 출석확인 페이지, 출석요청 페이지, 출석과목 페이지 등 전부 나뉘어져있다.)
<br><br>

### 필요한 쿠키 목록
| Key               |
|-------------------|
| hongik_abeek_sso |
| SUSER_ID         | 
| SUSER_LOGID      |
| SUSER_NAME       |
| SUSER_GUBUN      |
| SUSER_AUTH       |
| SUSER_AUTHKEY    |
| SUSER_LOGKEY     |
| SUSER_USER       |
| pni_token        |
| SUSER_EXTAUTH    |
| SUSER_LAST       |
| SUSER_LAST_IP    |
| JSESSIONID       |
| SUSER_LIMIT      |

print(c1)을 통해 어떤 쿠키값이 존재한지 알아본 결과, 위와 같이 나왔다.  
<br><br>

### 쿠키정리
```python
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
```
print(c1)을 해서 확인해보면, 딕셔너리 구조로 쿠키값이 나온다. 쿠키의 이름과 값을 필터링해준다.
그리고 실제 전달하는 형태로 만들기위해 ;을 붙여 전송할 쿠키값 c1을 만들었다.   
<br>
어떻게 전송되는지는 f12를 눌러 Network탭에서 요청 파일을 클릭 후 Request Header의 Raw버튼을 클릭해서 알아냈다.
<br><br>

```python
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
```
출석확인 페이지는 출결입력 대상이 없으면 "출결입력 대상이 없습니다."라는 메시지가 뜬다. xc
만약 출결입력 대상이 생기면 해당 메시지가 있던 곳에 "[2024-2] 데이터통신" 이런 식의 클릭가능한 문구가 생긴다.  
<br>
따라서 "출결입력 대상이 없습니다."라는 메시지를 찾지 못하면 [2024-2] 부분을 클릭하도록 만들어봤다.  
<br> 
이 페이지에서는 클릭하는 곳이 왜인지 클릭이 잘 안되어서 예외처리를 확실하게 해줬다.
디버깅하기도 쉽고 금방 다음 단계로 넘어갈 수 있어서 좋은 거 같다.  
<br>
2024-2를 찾게 했더니 클릭에 성공했다.  
<br><br>

```python
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
```
이제 input요소를 찾아서 아무런 숫자나 자동으로 보내본다.  
아무 숫자나 보내는 이유는 어떤 형식으로 출결코드 네자리가 전송되는지 알아둬야하기 때문이다.  
<br><br>

### 바디값
```
key=0000&yy=*&hakgi=*&haksu=*&bunban=*&weekno=*&week=*&time=*&latitude=*&longitude=*
```
실제로는 이런식의 바디가 날라갔다(*로 실제값은 전부 가림)  
내 위치와 수업정보 그리고 출결번호를 받는 구조임을 파악하고 출결번호 값을 바꾸는 식의 코드를 작성하면 목표를 달성할 수 있을 거 같다.  
<br><br>

```python
b1 = None

for request in driver.requests:
    if '*.jsp' in request.url:
        b1 = request.body.decode('utf-8', errors='ignore')
        print("Request Body : ", b1)
        break
```
해당 요청은 *.jsp (*로 모자이크처리함)으로 전달되는 것을 확인했으므로 내가 보낸 request message 중에서 같은 이름을 가진 요청을 찾은 뒤 b1에 저장한다.
<br><br>

***악의적인 목적으로 사용을 절대 금지합니다.***
```python
def update_value(b1, key, value):
    if re.search(rf"(&{key}=)", b1):
        b1 = re.sub(rf"(&{key}=)[^&]*", rf"&{key}={value}", b1)
    else:
        b1 += f"&{key}={value}"
    return b1
  
latitude = "*"
longitude = "*"

b1 = update_value(b1, "latitude", latitude)
b1 = update_value(b1, "longitude", longitude)
```
여담이지만 이런식으로 코드를 수정하면 내 위치도 다르게 전송이 되지 않을까라는 생각도 해보았다.  
<br><br>





















