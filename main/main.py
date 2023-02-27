import argparse as parser
import pyodbc as odbc
from email_utils import send_email
from datetime import date
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def scrape_webpages(driver, start_page_number, max_page_number=None):
    """ scrape the ASIC pages from the start page to max"""
    current_page = start_page_number
    parsed = []
    while 1:
        try:
            elements = driver.find_elements(By.CLASS_NAME, 'article-block')
            if len(elements) == 0:
                print('got no elements')
                return parsed

            for element in elements:
                #print(element.text)
                dl_tag = element.find_element(By.TAG_NAME, 'dl')
                if "In Liquidation" not in dl_tag.text:
                    continue

                acn_val_tag = dl_tag.find_element(By.TAG_NAME, 'dd')
                ptags = element.find_elements(By.TAG_NAME, 'p')
                title = ''
                for ptag in ptags:
                    title += ptag.text
                
                parsed.append({
                    'title': title,
                    'acn': acn_val_tag.text
                })

            current_page = current_page + 1
            if max_page_number is not None and current_page > max_page_number:
                return parsed

            # emulate click page
            #inner_page = driver.find_element(By.CLASS_NAME, 'inner')
            pager = driver.find_element(By.CLASS_NAME, 'NoticeTablePager')
            next_page_string = 'Page' + '$' + str(current_page)
            print('next page', next_page_string)
            a_tag = pager.find_element(
                By.XPATH, ("//a[contains(@href, '{myvar}')]".format(myvar=next_page_string)))
            print(a_tag.get_attribute('href'))
            if a_tag.get_attribute('href') is None:
                print('got no where to go')
                return parsed
            a_tag.click()
            window_after = driver.window_handles[0]
            driver.switch_to.window(window_after)
        except Exception:
            return parsed
        except KeyboardInterrupt:
            return parsed


def main():
    argument_parser = parser.ArgumentParser()
    argument_parser.add_argument("-N","--servername", help="Your SQL Server instance name")
    argument_parser.add_argument("-R","--receiver", help="Your email address where you want to send the email report")
    argument_parser.add_argument("-S","--sender", help="Your gmail email address from where you want to send the email")
    argument_parser.add_argument("-P","--password", help="Sender gmail app password")

    passed_argument = argument_parser.parse_args()

    if passed_argument.servername == None:
        print("Servername is missing, use 'python main.py -h' for more help")
        return
    
    if passed_argument.receiver == None:
        print("Receiver email address is missing, use 'python main.py -h' for more help")
        return

    if passed_argument.sender == None:
        print("Sender email address is missing, use 'python main.py -h' for more help")
        return

    if passed_argument.password == None:
        print("Sender email address's password is missing, use 'python main.py -h' for more help")
        return
    
    """
    print('Server name: %s' % passed_argument.servername)
    print('receiver email address: %s' % passed_argument.receiver)
    print('sender email address: %s' % passed_argument.sender)
    print('sender password: %s' % passed_argument.password)
    """

    receiver_emailaddress = passed_argument.receiver
    sender_emailaddress = passed_argument.sender
    sender_password = passed_argument.password
    server_name = passed_argument.servername
    database_name = 'asic_companies'
    body = "COMPANY NUMBER     COMPANY NAME              ISSUE DATE \n"
    today = date.today()
    date_string = today.strftime("%Y-%m-%d")

    """ configure Chrome and scrape the ASIC website and retrieve the data """
    # configure webdriver
    options = Options()
    
    options.add_argument("--window-size=1920,1080")  # set window size to native GUI size
    options.add_argument("start-maximized")  # ensure window is full-screen
    options.add_argument("--headless")

    
    #configure chrome browser to not load images and javascript
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option(
        "prefs", {"profile.managed_default_content_settings.images": 2}
    )

    driver = webdriver.Chrome(options=options)

    driver.get("https://publishednotices.asic.gov.au/browsesearch-notices/")
    
    # wait for page to load
    element = WebDriverWait(driver=driver, timeout=5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'div[id="breadcrumbs-container"]'))
    )

    parsed = scrape_webpages(driver, 1, 3)
    print('number of entries ' + str(len(parsed)))
    #print(parsed)
    connection = odbc.connect("DRIVER={SQL Server};"
                        "SERVER="+server_name+";"
                        "Database="+database_name+";"
                        "Trusted_Connection=yes;")
    cursor = connection.cursor()

    for company_detail in parsed:
        sql_statement = "SELECT COUNT(*) FROM companies_in_liquidation WHERE company_number = ?"
        cursor.execute(sql_statement, company_detail['acn'])
        count = cursor.fetchone()[0]
        if count > 0:
            print("The entry exists")
        else:
            print("The entry does not exist")
            cursor.execute("INSERT INTO companies_in_liquidation (company_number, company_name, notice_date) VALUES (?,?, GETDATE())", (company_detail['acn'], company_detail['title']))
            body += company_detail['acn'] + "                 " + company_detail['title'] + "       " + date_string +"   \n"
   
    connection.commit()
    connection.close()

    send_email(receiver_emailaddress, sender_emailaddress, sender_password, body)
    driver.quit()


if __name__== "__main__":
    main()
