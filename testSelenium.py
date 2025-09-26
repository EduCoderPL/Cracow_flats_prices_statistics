from selenium import webdriver
from selenium.webdriver.common.keys import Keys

driver = webdriver.Chrome()
driver.get("https://jbzd.com.pl/ulubione")#put here the adress of your page
input()
elem = driver.find_element("xpath", "//*[@type='submit']")#put here the content you have put in Notepad, ie the XPath
button = driver.find_element("id", 'buttonID')
print(elem.get_attribute("class"))
driver.close()