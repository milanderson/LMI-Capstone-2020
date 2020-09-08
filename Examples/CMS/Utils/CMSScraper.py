from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import shutil, os
from time import sleep

CMS_RULE_XPATH = "//div[@class='SUPLINF']"
CMS_COMMENT_BROWSE_XPATH = "//div[@class='GIY1LSJIUC']/div/a"
CMS_COMMENT_COUNT_XPATH = "//div[@class='GIY1LSJI4C']/h3[@class='h2']"
CMS_COMMENT_ID_XPATH = "//div[@class='GIY1LSJKXC']/ul/li[3]/span"
CMS_COMMENT_XPATH = "//div[@class='breakWord']/div[@class='GIY1LSJLXD']/div[@class='GIY1LSJIXD']/div[2]"
CMS_REG_RULES_ROOT_PATH = "https://beta.regulations.gov/document/"
CMS_REG_DOCS_ROOT_PATH = "https://www.regulations.gov/document?D="
CMS_LINK_XPATH = "//a[@class='gwt-Anchor']"

CHROMEDRIVER_PATH = "C:\\Scripts\\chromedriver.exe"
DOWNLOAD_PATH = "C:\\Scripts\\downloads\\"
OUTPUT_PATH = "C:\\Out\\"

USAGE = '''
    Usage
        CMSScraper.py rulename [savepath]
    Description
        Selenium automation to download a rule, the html comments and all attachments
    Argments
        rulename
            The CMS rule docket number
        savepath (Optional)
            The output directory to save rules and comments to
'''

def GetText(el, pref=""):
    text = pref + el.text
    tagName = el.tag_name.lower()
    if "h" == tagName[0] and len(tagName) == 2:
        pref += " "*(int(tagName[1]) - 2)
    elif len(pref) == 0:
        pref = "     "

    if tagName == "li" or tagName == "table":
        text += "\n".join([GetText(c, pref + "    ") for c in el.get_property('children')])
    elif tagName == "tr":
        text += ". ".join([GetText(c, pref) for c in el.get_property('children')])
    else:
        text += "\n".join([GetText(c, pref) for c in el.get_property('children')])
    return text

def GetRule(driver, ruleName, dlPath):
    if not os.path.isfile(OUTPUT_PATH + ruleName + ".txt"):
        driver.get(CMS_REG_RULES_ROOT_PATH + ruleName)
        rule_el = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, CMS_RULE_XPATH)))
        print("\tRule found, extracting text")
        f = open(OUTPUT_PATH + ruleName + ".txt", 'w')
        ruleText = GetText(rule_el).encode('ascii', errors='ignore').decode('ascii', errors='ignore')
        f.write(ruleText)
        print("\tWriting rule text")
        f.close()

def GetComments(driver, ruleName, dlPath, stDocNum=2):
    driver.get(CMS_REG_DOCS_ROOT_PATH + ruleName)
    comment_browse_link = WebDriverWait(driver, 25).until(EC.presence_of_element_located((By.XPATH, CMS_COMMENT_BROWSE_XPATH)))
    comment_browse_link.click()
    count_elem = WebDriverWait(driver, 25).until(EC.presence_of_element_located((By.XPATH, CMS_COMMENT_COUNT_XPATH)))
    count = int("".join([c for c in count_elem.text if c in '1234567890']))
    doc_elem =  WebDriverWait(driver, 25).until(EC.presence_of_element_located((By.XPATH, CMS_COMMENT_ID_XPATH)))
    root_doc_pts = doc_elem.text.split()[-1].split('-')
    root_doc_name = "-".join(root_doc_pts[:-1])
    root_doc_pad_size = len(root_doc_pts[-1])
    for i in range(stDocNum, count + 1):
        docName = root_doc_name + "-" + str(i).zfill(root_doc_pad_size)
        print("\tDownloading " + docName)
        try:
            GetComment(driver, docName, dlPath) 
        except Exception as e:
            print("Error encountered on document " + docName + ". ", e)

def GetComment(driver, docName, dlPath):
    if not os.path.isfile(OUTPUT_PATH + docName + ".txt"):
        driver.get(CMS_REG_DOCS_ROOT_PATH + docName)
        comment = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, CMS_COMMENT_XPATH)))
        f = open(OUTPUT_PATH + docName + ".txt", 'w')
        commentText = GetText(comment).encode('ascii', errors='ignore').decode('ascii', errors='ignore')
        f.write(commentText)
        f.close()

        att_Num = 1
        att_Nums = {}
        for link in driver.find_elements_by_xpath(CMS_LINK_XPATH):
            if link and link.get_attribute("href") and 'attachment' in link.get_attribute("href"):
                next_num = link.get_attribute("href").split('attachment')[1].split('&')[0]
                if next_num not in att_Nums or att_Nums[next_num] == 'pdf':
                    observer = Observer()
                    observer.schedule(DownloadHandler(OUTPUT_PATH + docName + "_" + str(att_Num), att_Nums, next_num), DOWNLOAD_PATH, recursive=False)
                    observer.start()
                    link.click()
                    sleep(10)
                    observer.stop()
                    att_Num += 1

def InitDriver(dlPath=DOWNLOAD_PATH):
    chromeOptions = webdriver.ChromeOptions()
    prefs = {"download.default_directory" : dlPath}
    chromeOptions.add_experimental_option("prefs", prefs)
    return webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, chrome_options=chromeOptions)


class DownloadHandler(FileSystemEventHandler):
    def __init__(self, target, attDict, attNum):
        self.target = target
        self.attachmentDict = attDict
        self.attNum = attNum

    def on_modified(self, event):
        if not any(ending in event.src_path for ending in ["crdownload", ".tmp"]):
            attFType = event.src_path.split('.')[-1]
            shutil.copy(event.src_path, self.target + "." + attFType)
            self.attachmentDict[self.attNum] = attFType

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print(USAGE)
    else:    
        try:
            stDocNum = int(sys.argv[1].split('-')[-1])
            dlPath = DOWNLOAD_PATH if len(sys.argv) != 3 else sys.argv[2]
            driver = InitDriver(dlPath)
            print('Downloading Rule')
            GetRule(driver, sys.argv[1], dlPath, stDocNum)
            print("Downloading Comments")
            GetComments(driver, sys.argv[1], dlPath)
            
        except Exception as e:
            print(e)
        finally:
            driver.quit()