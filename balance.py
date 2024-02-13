import os
import json
from dotenv import load_dotenv
from bs4 import BeautifulSoup as bs
import requests
from urllib3 import poolmanager
from ssl import create_default_context, Purpose, CERT_NONE

class CustomHttpAdapter (requests.adapters.HTTPAdapter):
    def __init__(self, ssl_context=None, **kwargs):
        self.ssl_context = ssl_context
        super().__init__(**kwargs)

    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = poolmanager.PoolManager(
            num_pools=connections, maxsize=maxsize,
            block=block, ssl_context=self.ssl_context)

def ssl_supressed_session():
    ctx = create_default_context(Purpose.SERVER_AUTH)
    # to bypass verification after accepting Legacy connections
    ctx.check_hostname = False
    ctx.verify_mode = CERT_NONE
    # accepting legacy connections
    ctx.options |= 0x4    
    session = requests.Session()
    session.mount('https://', CustomHttpAdapter(ctx))
    return session


load_dotenv()
SECURITY_QUESTION=os.getenv('SECURITY_QUESTION')
SECURITY_ANSWER=os.getenv('SECURITY_ANSWER')

USERNAME=os.getenv('USERNAME')
PASSWORD=os.getenv('PASSWORD')

URL = 'https://www.mohela.com/DL/secure/account/loginStep1.aspx'
SUMMARY_URL = 'https://www.mohela.com/DL/secure/borrower/AccountSummary.aspx'

PAYLOAD = {
    '__EVENTTARGET': 'ctl00$ctl00$cphContent$cphMainForm$btnLogin',
    'ctl00$ctl00$cphContent$cphMainForm$txtLoginID': USERNAME,
    'ctl00$ctl00$cphContent$cphMainForm$txtPassword': PASSWORD,
    'ctl00$ctl00$cphContent$cphMainForm$hdndevicePrint': 'version=1&pm_fpua=mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/121.0.0.0 safari/537.36|5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36|Win32&pm_fpsc=24|2560|1440|1400&pm_fpsw=&pm_fptz=-5&pm_fpln=lang=en-US|syslang=|userlang=&pm_fpjv=0&pm_fpco=1'
}


s = ssl_supressed_session()

# Get the __VIEWSTATE
login_page = s.get(URL)
soup = bs(login_page.content, 'html.parser')
viewstate = soup.find('input', {'id': '__VIEWSTATE'}).get('value')
PAYLOAD['__VIEWSTATE']=viewstate

# Post to the login page
login = s.post(URL, data=PAYLOAD)
soup = bs(login.content, 'html.parser')
viewstate = soup.find('input', {'id': '__VIEWSTATE'}).get('value') # new viewstate
PAYLOAD['__VIEWSTATE']=viewstate

# Answer security question
PAYLOAD['ctl00$ctl00$cphContent$cphMainForm$hdnSecQuestionID'] = SECURITY_QUESTION
PAYLOAD['ctl00$ctl00$cphContent$cphMainForm$txtAnswer'] = SECURITY_ANSWER
PAYLOAD['ctl00$ctl00$cphContent$cphMainForm$btnSubmitAnswer'] = 'Submit'
sec = s.post(URL, data=PAYLOAD)

# Attempt to get the summary
summary = s.get(SUMMARY_URL)
soup = bs(summary.content, 'html.parser')
for t in soup.findAll(string='Current Principal:'):
    p = t.parent
    if p.name != 'th': continue
    ns = p.nextSibling
    if ns and not ns.name: ns = ns.nextSibling
    if not ns or ns.name not in ('td', 'th'): continue
    output = { 'principal' : ns.string, 'interest': ns.findNext('td').string }
    print(json.dumps(output))
