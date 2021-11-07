from tkinter import *
from tkinter import ttk
import tkinter.messagebox
from typing import ClassVar
import tkinter as tk
from PIL import ImageTk, Image
import main as bsh
colors = {'good':'#51ff99', 'skeptical':'#ff9900', 'bad':'#FA1E3B'}
colleges = bsh.get_college_ids()
root = Tk()
logo = ImageTk.PhotoImage(Image.open('./bookshelf.png'))
logo_lbl = ttk.Label(root, image=logo, width=10)
logo_lbl.pack()
root.update()
root.minsize(500, 500)
search_frame = Frame()
search_frame.pack()
college = None
courses = []
course_listings = {}
termid = 0
root.title("bookshelf")
c_list_lbl = ttk.Label(search_frame, text="Enter your college: ")
c_list_lbl.pack(side=LEFT)
c_search_btn = None
done_btn = None
term_btn = None
course_entry_lbl = None
term_options = None
c_search = Entry(search_frame)
c_search.pack(side=LEFT)

def search_from_box(a):
    pass

c_search_btn = Button(search_frame, text="Search", bg=colors['good'], command = lambda: search_from_box(None))
c_search_btn.pack(side=LEFT)

def remove_course(cname, cobj):
    global courses
    global done_btn
    courses.remove(cobj)
    for e in course_listings[cname]:
        e.pack_forget()
    if not courses:
        done_btn.config(state=DISABLED)

def add_course(a, cname, entrybox):
    global courses 
    global done_btn
    if cname.count('-') < 2:
        tkinter.messagebox.showinfo('Invalid course','Invalid course entry. Please enter courses in a format such as CISC-371-DFA.')
        return
    else:
        course_frame = Frame()
        course_frame.pack()
        entrybox.delete(0, 'end')
        cnamespl = cname.split('-')
        course_obj = bsh.course(cnamespl[0], cnamespl[1], cnamespl[2])
        courses.append(course_obj)
        course_label = ttk.Label(course_frame, text=cname)
        course_label.pack(side=LEFT)
        course_del_btn = Button(course_frame, text="Delete", bg=colors['bad'], command = lambda: remove_course(cname, course_obj))
        course_del_btn.pack(side=LEFT)
        course_listings[cname] = [course_label, course_del_btn, course_frame]
        done_btn.config(state=NORMAL)

def book_search(courses):
    book_div = Frame()
    book_div.pack()
    books_lbl = ttk.Label(book_div, text="Your required materials:")
    books_lbl.place(relx=0.5, rely=0.5, anchor=CENTER)
    # books.append(material(b['publisher'], b['author'], b['title'], b['edition'], b['isbn'], b['priceRangeDisplay']))
    books = bsh.get_books(college, termid, courses)
    book_tree = Frame()
    book_tree.pack()
    books_tbl = ttk.Treeview(book_tree)
    books_tbl['columns'] = ('For course', 'Publisher', 'Author', 'Title', 'Edition', 'ISBN', 'Price')
    books_tbl.heading('#0', text='', anchor=CENTER)
    books_tbl.column('#0', width=0, stretch=NO)
    for c in books_tbl['columns']:
        books_tbl.heading(c, text=c, anchor=CENTER)
        books_tbl.column(c, anchor=CENTER, stretch=YES)
    for x,b in enumerate(books):
        books_tbl.insert(parent='',index='end',iid=x,text='', values=(b.forclass, b.publisher, b.author, b.title, b.edition, b.isbn, b.pricerange))
    for e in course_listings.keys():
        for el in course_listings[e]:
            el.pack_forget()
    course_entry_lbl.config(text="Your required materials:")
    books_tbl.pack()


def init_course_select(term):
    global termid
    global done_btn
    global course_entry_lbl
    instructional_div = Frame()
    instructional_div.pack()
    course_select_frame = Frame()
    course_select_frame.pack()
    termid = term
    term_btn.config(state=DISABLED)
    term_options.config(state=DISABLED)
    course_entry_lbl = ttk.Label(instructional_div, text="Enter your course in a format such as CISC-371-DFA, then hit add.")
    course_entry_lbl.pack()
    course_entry = Entry(course_select_frame)
    course_entry.pack(side=LEFT)
    course_add_btn = Button(course_select_frame, text="Add", bg=colors['skeptical'], command = lambda: add_course(None, course_entry.get(), course_entry))
    course_add_btn.pack(side=LEFT)
    done_btn = Button(course_select_frame, text="Done", bg=colors['good'], command = lambda: book_search(courses))
    done_btn.pack(side=LEFT)
    done_btn.config(state=DISABLED)
    course_div = Frame()
    course_div.pack()
    course_entry_lbl = ttk.Label(course_div, text="Currently added courses:")
    course_entry_lbl.pack()
    root.unbind('<Return>')
    root.bind('<Return>', lambda a: add_course(None, course_entry.get(), course_entry))

def search_from_box(a):
    search = bsh.search(c_search.get(), colleges)
    if search:
        search_res_frame = Frame(root)
        search_res_frame.pack()
        c_search_btn.config(state=DISABLED)
        c_search.config(state=DISABLED)
        c_search.delete(0, END)
        c_search.insert(0, search.storename)
        global college
        college = search
        term_label = ttk.Label(search_res_frame, text="Select what term you're attending: ")
        term_label.pack(side=LEFT)
        terms = bsh.get_terms(search)
        selected_term = StringVar()
        selected_term.set("")
        global term_options
        term_options = OptionMenu(search_res_frame, selected_term, *terms.keys())
        term_options.config(width=max([len(t) for t in terms.keys()]))
        term_options.pack(side=LEFT)
        global term_btn
        term_btn = Button(search_res_frame, text="Next", bg=colors['good'], command = lambda: init_course_select(terms[selected_term.get()]))
        term_btn.pack(side=LEFT)
    else:
        tkinter.messagebox.showinfo('College not found','Unfortunately, your college was not found. If the spelling is correct, it may not be on bkstr.com.')

root.bind('<Return>', search_from_box)
root.mainloop()