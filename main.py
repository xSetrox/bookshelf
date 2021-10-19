import requests
from fake_headers import Headers
from difflib import get_close_matches
from bs4 import BeautifulSoup

class store():
    def __init__(self, storeurl, storeid) -> None:
        self.storeurl = storeurl
        self.storeid = storeid

class course():
    def __init__(self, dept, course, section) -> None:
        self.department = dept
        self.course = course
        self.section = section

class material():
    #b['publisher'], b['author'], b['title'], b['edition'], b['isbn'], b['priceRangeDisplay']
    def __init__(self, publisher, author, title, edition, isbn, pricerange):
        self.publisher = publisher
        self.author = author
        self.title = title
        self.edition = edition
        self.isbn = isbn
        self.pricerange = pricerange
    
    def __str__(self):
        format = f"""
        Title: {self.title}
        Edition: {self.edition}
        Publisher: {self.publisher}
        ISBN: {self.isbn}
        Price range: {self.pricerange}
        Author: {self.author}
        """
        return format

def headered_get_request(url):
    header = Headers(
        browser="chrome",  # Generate only Chrome UA
        os="win",  # Generate ony Windows platform
        headers=True  # generate misc headers
    )
    r = requests.get(url, headers=header.generate())
    return r

def headered_post_request(url, payload):
    header = Headers(
        browser="chrome",  # Generate only Chrome UA
        os="win",  # Generate ony Windows platform
        headers=True  # generate misc headers
    )
    r = requests.post(url, headers=header.generate(), json=payload)
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
    while True:
        selection = input("Please enter the number of the term you are buying book for: ")
        try:
            selection = int(selection) - 1
        except:
            print("Invalid term entered.")
            continue
        if selection < 1 or selection + 1 > len(terms_ordered):
            print("Invalid term entered.")
            continue
        term = terms_ordered[selection][0]
        break
    return term

#TODO: add blackboard html parser
def get_courses(college, termid):
    courses = []
    while True:
        ans = input("Please input your courses in a format such as CISC-371-DFA. Enter \"stop\" to stop: ")
        if ans.lower() == "stop":
            break
        if ans.count('-') < 2:
            print("Invalid course input.")
            continue
        ans = ans.split('-')
        courses.append(course(ans[0], ans[1], ans[2]))
    return courses

def ellucian_parse(filename):
    courses = []
    try:
        with open(filename, 'r') as f:
            html = f.read()
            soup = BeautifulSoup(html, "lxml")
    except Exception as e:
        print("Problem reading file: ", str(e))
    finds = soup.findAll('caption')
    for f in finds:
        f = f.text
        if '-' in f:
            f = f.split('-')
            course = f[1].strip().replace(' ', '-').strip() + '-' + f[2].strip()
            courses.append(course)
    return courses

def get_books(college, termid, courses):
    if not courses:
        print("Courses list was empty. Cannot continue.")
        return
    books = []
    url = f"https://svc.bkstr.com/courseMaterial/results?storeId={college.storeid}&langId=-1&catalogId=11077&requestType=DDCSBrowse"
    course_jsons = []
    for i in courses:
        secondary = f'{i.department}/{i.course}/{i.section}'
        course_jsons.append({"secondaryvalues":secondary,
            "divisionDisplayName":"",
            "departmentDisplayname":i.department,
            "courseDisplayName":i.course,
            "sectionDisplayName":i.section
        })
    payload = {
        "storeId": college.storeid,
        "termId": termid,
        "programId": "1061",
        "courses": course_jsons
    }
    r = headered_post_request(url, payload).json()
    for b in r[0]['courseSectionDTO'][0]['courseMaterialResultsList']:
        books.append(material(b['publisher'], b['author'], b['title'], b['edition'], b['isbn'], b['priceRangeDisplay']))
    return books

if __name__ == "__main__":
    college = search(input("Please enter your college name: "))
    term = term_selector(college)
    courses = get_courses(college, term)
    books = get_books(college, term, courses)
    for b in books:
        print(str(b))