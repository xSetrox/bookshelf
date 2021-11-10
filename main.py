from typing import TYPE_CHECKING
import requests
from fake_headers import Headers
from difflib import get_close_matches
from bs4 import BeautifulSoup

stores = []
class store():
    def __init__(self, storeurl, storeid, storename) -> None:
        self.storeurl = storeurl
        self.storeid = storeid
        self.storename = storename

class course():
    def __init__(self, dept, course, section) -> None:
        self.department = dept
        self.course = course
        self.section = section

class material():
    #b['publisher'], b['author'], b['title'], b['edition'], b['isbn'], b['priceRangeDisplay']
    def __init__(self, forclass, publisher, author, title, edition, isbn, pricerange):
        self.forclass = forclass
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
        stores[key['storeName']] = store(key['storeUrl'], key['storeNumber'], key['storeName'])
    return stores

def search(query, stores):
    query = query.lower()
    for s in stores:
        if s.lower() == query:
            return stores[s]
    else:
        # todo: fix close matches
        close_matches = get_close_matches(query, stores.keys())
        if close_matches:
            return stores[close_matches[0]]
        else:
            return

def get_terms(school):
    r = headered_get_request("https://svc.bkstr.com/courseMaterial/info?storeId=" + school.storeid).json()
    request_json = r['finalData']['campus']
    if len(request_json) < 2:
        campus = request_json[0]
    program = campus['program']
    if len(program) < 2:
        program = program[0]
    terms = {}
    for t in program['term']:
        terms[t['termName']] = t['termId']
    return terms

#TODO: add blackboard html parser
def get_courses(college, termid):
    courses = []
    while True:
        ans = input("Please input your courses in a format such as CISC-371-DFA. Enter \"stop\" to stop: ")
        if ans.lower() == "stop":
            break
        if ans.count('-') < 2:
            continue
        ans = ans.split('-')
        courses.append(course(ans[0], ans[1], ans[2]))
    return courses

def portal_parse(filename):
    courses = []
    try:
        with open(filename, 'r') as f:
            html = f.read()
            soup = BeautifulSoup(html, "lxml")
    except Exception as e:
        print("Problem reading file: ", str(e))
        return None
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
        return
    books = []
    url = f"https://svc.bkstr.com/courseMaterial/results?storeId={college.storeid}&langId=-1&catalogId=11077&requestType=DDCSBrowse"
    course_jsons = []
    # we need to build the json POST request by giving the 'courses' key a list of courses
    for i in courses:
        secondary = f'{i.department}/{i.course}/{i.section}'
        course_jsons.append({
            "divisionDisplayName":"",
            "departmentDisplayName":i.department,
            "courseDisplayName":i.course,
            "sectionDisplayName":i.section,
            "secondaryvalues":secondary
        })
    payload = {
        "courses": course_jsons,
        "programId": "1061", 
        "storeId": college.storeid,
        "termId": termid 

    }
    r = headered_post_request(url, payload).json()
    fcp = r[0]['courseSectionDTO']
    for x in fcp:
        forcourse = f"{x['department']}-{x['course']}-{x['section']}"
        if x['courseSectionStatus']['code'] == "500":
            books.append(material(forcourse, '', '', 'Course not found', '', '', ''))
            continue
        if 'courseMaterialResultsList' in x:
            for b in x['courseMaterialResultsList']:
                books.append(material(forcourse, b['publisher'], b['author'], b['title'], b['edition'], b['isbn'], b['priceRangeDisplay']))
        else:
            books.append(material(forcourse, '', '', 'No materials found for this course', '', '', ''))
    return books 