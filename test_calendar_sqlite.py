from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import sqlite3

email = f"test{{int(time.time())}}@example.com"
password = "testpass"

conn = sqlite3.connect("events.db")
conn.execute("DELETE FROM users")
conn.execute("DELETE FROM events")
conn.commit()
conn.close()

driver = webdriver.Chrome()
driver.get("http://127.0.0.1:8001/signup")
time.sleep(1)

driver.find_element(By.NAME, "email").send_keys(email)
driver.find_element(By.NAME, "password").send_keys(password)
driver.find_element(By.TAG_NAME, "button").click()

driver.find_element(By.NAME, "email").send_keys(email)
driver.find_element(By.NAME, "password").send_keys(password)
driver.find_element(By.TAG_NAME, "button").click()
time.sleep(1)
assert "行事曆" in driver.page_source
print("登入成功")

driver.find_element(By.LINK_TEXT, "新增行程").click()
driver.find_element(By.NAME, "title").send_keys("測試行程")
driver.find_element(By.NAME, "date").send_keys("02025-06-15")
driver.find_element(By.NAME, "note").send_keys("這是一個自動化測試建立的行程")
driver.find_element(By.TAG_NAME, "button").click()
time.sleep(1)
assert "測試行程" in driver.page_source
print("行程新增成功")

driver.find_element(By.LINK_TEXT, "登出").click()
assert "登入" in driver.page_source
print("登出成功")

driver.quit()