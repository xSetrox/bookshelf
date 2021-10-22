from tkinter import *
from tkinter import ttk
import tkinter.messagebox
from typing import ClassVar
import main as bsh
colleges = bsh.get_college_ids()
w = Tk()
c_frame = Frame(w, bd=5)
c_frame.grid(column=0, row=0, padx=(0, 5), pady=(0, 5))
college = None
courses = []
course_listings = {}
termid = 0
w.title("bookshelf")
c_list_lbl = ttk.Label(c_frame, text="Enter your college: ")
c_list_lbl.grid(row=0, column=0)
c_search_btn = None
term_btn = None
term_options = None
c_search = Entry(c_frame)
c_search.grid(row=0, column=1)

def remove_course(cname):
    courses.remove(cname)
    for e in course_listings[cname]:
        e.grid_remove()

def add_course(cname):
    global courses 
    if cname.count('-') < 2:
        tkinter.messagebox.showinfo('Invalid course','Invalid course entry. Please enter courses in a format such as CISC-371-DFA.')
        return
    else:
        cnamespl = cname.split('-')
        courses.append(bsh.course(cnamespl[0], cnamespl[1], cnamespl[2]))
        course_label = ttk.Label(c_frame, text=cname)
        course_label.grid(row=4+len(courses), column=0)
        course_del_btn = Button(c_frame, text="Delete", command = lambda: remove_course(cname))
        course_del_btn.grid(row=4+len(courses), column=1)
        course_listings[cname] = [course_label, course_del_btn]
    
def init_course_select(term):
    global termid
    termid = term
    term_btn.config(state=DISABLED)
    term_options.config(state=DISABLED)
    course_entry_lbl = ttk.Label(c_frame, text="Enter your course in a format such as CISC-371-DFA, then hit add.")
    course_entry_lbl.grid(row=2, column=0)
    course_entry = Entry(c_frame)
    course_entry.grid(row=3, column = 0)
    course_add_btn = Button(c_frame, text="Add", command = lambda: add_course(course_entry.get()))
    course_add_btn.grid(row=3, column=1)
    course_entry_lbl = ttk.Label(c_frame, text="Currently added courses:")
    course_entry_lbl.grid(row=4, column=0)

def search_from_box():
    search = bsh.search(c_search.get(), colleges)
    if search:
        c_search_btn.config(state=DISABLED)
        c_search.config(state=DISABLED)
        c_search.delete(0, END)
        c_search.insert(0, search.storename)
        global college
        college = search
        term_label = ttk.Label(c_frame, text="Select what term you're attending: ")
        term_label.grid(row=1, column=0)
        terms = bsh.get_terms(search)
        selected_term = StringVar()
        selected_term.set("")
        global term_options
        term_options = OptionMenu(c_frame, selected_term, *terms.keys())
        term_options.config(width=max([len(t) for t in terms.keys()]))
        term_options.grid(row=1, column=1)
        global term_btn
        term_btn = Button(c_frame, text="Next", command = lambda: init_course_select(terms[selected_term.get()]))
        term_btn.grid(row=1, column=2)
    else:
        tkinter.messagebox.showinfo('College not found','Unfortunately, your college was not found. If you may not be on bkstr.com.')
c_search_btn = Button(c_frame, text="Search", command = search_from_box)
c_search_btn.grid(row=0, column=2)
w.mainloop()