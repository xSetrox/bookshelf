import requests
from fake_headers import Headers
from difflib import get_close_matches
from bs4 import BeautifulSoup

class store():
    def __init__(self, storeurl, storeid) -> None:
        self.storeurl = storeurl
        self.storeid = storeid

def headered_get_request(url):
    header = Headers(
        browser="chrome",  # Generate only Chrome UA
        os="win",  # Generate ony Windows platform
        headers=True  # generate misc headers
    )
    r = requests.get(url, headers=header.generate())
    return r

def get_all_courses(college, term):
    print("Gathering courses for this term...")
    #r = headered_get_request(f"https://svc.bkstr.com/courseMaterial/courses?storeId={college.storeid}&termId={term}").json()
    url = f"https://svc.bkstr.com/courseMaterial/courses?storeId={college.storeid}&termId={term}"
    print(url)
    r = headered_get_request(url).json()
    course_sections = {}
    courses = r['finalDDCSData']['division'][0]['department']
    for dept in courses:
        depname = dept['depName']
        for c in dept['course']:
            coursename = c['courseName']
            for s in c['section']:
                section = s['sectionName']
                course_id = s['courseId']
                course_sections[f'{depname}-{coursename}-{section}'] = course_id
    return course_sections

# ideally make this asynchronous. the time it takes user to type the school name should give this enough time to process, usually
def get_college_ids():
    stores = {}
    print("Please wait, gathering stores list...")
    all_colleges_dir = "https://svc.bkstr.com/store/byName?storeType=FMS&catalogId=10001&langId=-1&schoolName=*"
    r = headered_get_request(all_colleges_dir).json()
    request_json = r['storeResultList']
    for key in request_json:
        stores[key['storeName']] = store(key['storeUrl'], key['storeNumber'])
    return stores

stores = get_college_ids()
def search(query):
    query = query.lower()
    for s in stores:
        if s.lower() == query:
            return stores[s]
    else:
        # todo: fix close matches
        close_matches = get_close_matches(query, stores.keys())
        if close_matches:
            print(close_matches)
        else:
            print("Sorry, college not found.")
            return

def term_selector(school):
    r = headered_get_request("https://svc.bkstr.com/courseMaterial/info?storeId=" + school.storeid).json()
    request_json = r['finalData']['campus']
    if len(request_json) < 2:
        campus = request_json[0]
    program = campus['program']
    if len(program) < 2:
        program = program[0]
    terms = {}
    terms_ordered = []
    for x,t in enumerate(program['term']):
        terms_ordered.append([])
        terms_ordered[x] = [t['termId'], t['termName']]
    print("Terms: ")
    for x,t in enumerate(terms_ordered, 1):
        print(f'{x}. {t[1]}')
    selection = input("Please enter the number of the term you are buying book for: ")
    try:
        selection = int(selection) - 1
    except:
        print("Error.")
        exit()
    print(terms_ordered)
    term = terms_ordered[selection][0]
    return term

def get_books_for(college, termid, courses):
    url = f"https://svc.bkstr.com/courseMaterial/results?storeId={college.storeid}&langId=-1&catalogId=11077&requestType=DDCSBrowse"
    print(url)
    r = headered_get_request(url).json()

if __name__ == "__main__":
    college = search(input("Please enter your college name: "))
    term = term_selector(college)
    courses = get_all_courses(college, term)
    get_books_for(college, term, courses)

# https://www.bkstr.com/mercydobbsferrystore/course-materials-results?shopBy=course&divisionDisplayName=&departmentDisplayName=CISC&courseDisplayName=371&sectionDisplayName=DFA&programId=1061&termId=100070972
#POST to this ^^ with payload ie {"storeId":"11553","termId":"100070972","programId":"1061","courses":[{"secondaryvalues":"CISC/311/DFA","divisionDisplayName":"","departmentDisplayName":"CISC","courseDisplayName":"311","sectionDisplayName":"DFA"},{"secondaryvalues":"CISC/231/DFA","divisionDisplayName":"","departmentDisplayName":"CISC","courseDisplayName":"231","sectionDisplayName":"DFA"}]}
