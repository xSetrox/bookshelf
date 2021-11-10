from tkinter import *
from tkinter import ttk
import tkinter.messagebox
from PIL import ImageTk, Image
import csv
import main as bsh
import webbrowser
from tkinter import filedialog as fd
from tkinter.messagebox import showinfo

class BookshelfGui():
    def __init__(self) -> None:
        self.all_optional_frames = []
        self.colors = {'good':'#51ff99', 'skeptical':'#ff9900', 'bad':'#FA1E3B', 'magenta':'#fb3dff'}
        self.colleges = bsh.get_college_ids()
        self.root = Tk()
        self.logo = ImageTk.PhotoImage(Image.open('./bookshelf.png'))
        self.logo_lbl = ttk.Label(self.root, image=self.logo, width=10)
        self.logo_lbl.pack()
        self.root.update()
        self.root.minsize(1000, 500)
        self.search_frame = Frame()
        self.search_frame.pack()
        self.all_optional_frames.append(self.search_frame)
        self.college = None
        self.courses = []
        self.course_listings = {}
        self.termid = 0
        self.root.title("bookshelf")
        self.c_list_lbl = ttk.Label(self.search_frame, text="Enter your college: ")
        self.c_list_lbl.pack(side=LEFT)
        self.all_optional_frames.append(self.c_list_lbl)
        self.done_btn = None
        self.term_btn = None
        self.course_entry_lbl = None
        self.term_options = None
        self.c_search = Entry(self.search_frame)
        self.c_search.pack(side=LEFT)
        self.all_optional_frames.append(self.c_search)
        self.c_search_btn = Button(self.search_frame, text="Search", bg=self.colors['good'], command = lambda: search_from_box(None))
        self.c_search_btn.pack(side=LEFT)
        self.root.bind('<Return>', self.search_from_box)
        self.root.mainloop()

    def remove_course(self, cname, cobj):
        self.courses.remove(cobj)
        for e in self.course_listings[cname]:
            e.pack_forget()
        if not self.courses:
            self.done_btn.config(state=DISABLED)

    def add_course(self, a, cname, entrybox):
        if cname.count('-') < 2:
            tkinter.messagebox.showinfo('Invalid course','Invalid course entry. Please enter courses in a format such as CISC-371-DFA.')
            return
        else:
            course_frame = Frame()
            course_frame.pack()
            self.all_optional_frames.append(course_frame)
            if entrybox:
                entrybox.delete(0, 'end')
            cnamespl = cname.split('-')
            course_obj = bsh.course(cnamespl[0], cnamespl[1], cnamespl[2])
            self.courses.append(course_obj)
            course_label = ttk.Label(course_frame, text=cname)
            course_label.pack(side=LEFT)
            course_del_btn = Button(course_frame, text="Delete", bg=self.colors['bad'], command = lambda: self.remove_course(cname, course_obj))
            course_del_btn.pack(side=LEFT)
            self.course_listings[cname] = [course_label, course_del_btn, course_frame]
            self.done_btn.config(state=NORMAL)

    def to_spreadsheet(self, data):
        file = open('./My course materials.csv', 'w')
        writer = csv.writer(file)
        headers = ['For course', 'Publisher', 'Author', 'Title', 'Edition', 'ISBN', 'Price']
        writer.writerow(headers)
        for e in data:
            writer.writerow(e)
        file.close()
        tkinter.messagebox.showinfo('Spreadsheet saved','Your spreadsheet has been exported to \"My course Materials.csv\"')

    def amazon_isbn_search(self, data):
        for e in data:
            webbrowser.open("https://www.amazon.com/s?k=" + e[5])

    def start_over(self, book_div, book_tree, post_frame):
        book_div.pack_forget()
        book_tree.pack_forget()
        post_frame.pack_forget()
        search_frame = Frame()
        search_frame.pack()
        self.all_optional_frames.append(search_frame)
        self.college = None
        self.courses = []
        self.course_listings = {}
        self.termid = 0
        self.root.title("bookshelf")
        c_list_lbl = ttk.Label(search_frame, text="Enter your college: ")
        c_list_lbl.pack(side=LEFT)
        self.all_optional_frames.append(c_list_lbl)
        self.done_btn = None
        self.term_btn = None
        self.course_entry_lbl = None
        self.term_options = None
        c_search = Entry(search_frame)
        c_search.pack(side=LEFT)
        self.all_optional_frames.append(c_search)
        self.c_search_btn = Button(search_frame, text="Search", bg=self.colors['good'], command = lambda: self.search_from_box(None))
        self.c_search_btn.pack(side=LEFT)
        self.root.unbind('<Return>')
        self.root.bind('<Return>', self.search_from_box)

    def book_search(self, courses):
        books = bsh.get_books(self.college, self.termid, courses)
        if not books:
            tkinter.messagebox.showinfo('No materials found','No materials were found for any of your courses.')
        else:
            books_export = []
            book_div = Frame()
            book_div.pack()
            books_lbl = ttk.Label(book_div, text="Your required materials:")
            books_lbl.pack()
            # books.append(material(b['publisher'], b['author'], b['title'], b['edition'], b['isbn'], b['priceRangeDisplay']))
            book_tree = Frame()
            book_tree.pack()
            books_tbl = ttk.Treeview(book_tree)
            books_tbl['columns'] = ('For course', 'Publisher', 'Author', 'Title', 'Edition', 'ISBN', 'Price')
            books_tbl.heading('#0', text='', anchor=CENTER)
            books_tbl.column('#0', width=0, stretch=NO)
            for c in books_tbl['columns']:
                books_tbl.heading(c, text=c, anchor=CENTER)
                books_tbl.column(c, anchor=CENTER, stretch=NO)
            for x,b in enumerate(books):
                data = [b.forclass, b.publisher, b.author, b.title, b.edition, b.isbn, b.pricerange]
                books_export.append(data)
                books_tbl.insert(parent='',index='end',iid=x,text='', values=data)
            for e in self.all_optional_frames:
                e.pack_forget()
            self.course_entry_lbl.config(text="Your required materials:")
            books_tbl.pack()
            post_frame = Frame()
            post_frame.pack()
            spreadsheet_btn = Button(post_frame, text="Spreadsheet", bg=self.colors['good'], command = lambda: self.to_spreadsheet(books_export))
            spreadsheet_btn.pack(side=LEFT)
            amazon_btn = Button(post_frame, text="Amazon", bg=self.colors['skeptical'], command = lambda: self.amazon_isbn_search(books_export))
            amazon_btn.pack(side=LEFT)
            startover_btn = Button(post_frame, text="Start over", bg=self.colors['bad'], command = lambda: self.start_over(book_div, book_tree, post_frame))
            startover_btn.pack(side=LEFT)
    
    def portal_import(self):
        filetypes = [
        ('HTML files', '*.html')
        ]

        filename = fd.askopenfilename(
            title='Import Connect HTML',
            initialdir='/',
            filetypes=filetypes)

        courses = bsh.portal_parse(filename)
        if not courses:
            tkinter.messagebox.showinfo('Unable to parse','A problem was encountered parsing the HTML. Your education system may not be supported for this feature.')
            
        for c in courses:
            self.add_course(None, c, None)

    def init_course_select(self, term):
        instructional_div = Frame()
        instructional_div.pack()
        self.all_optional_frames.append(instructional_div)
        course_select_frame = Frame()
        course_select_frame.pack()
        self.all_optional_frames.append(course_select_frame)
        self.termid = term
        self.term_btn.config(state=DISABLED)
        self.term_options.config(state=DISABLED)
        self.course_entry_lbl = ttk.Label(instructional_div, text="Enter your course in a format such as CISC-371-DFA, then hit add.")
        self.course_entry_lbl.pack()
        course_entry = Entry(course_select_frame)
        course_entry.pack(side=LEFT)
        course_add_btn = Button(course_select_frame, text="Add", bg=self.colors['skeptical'], command = lambda: self.add_course(None, course_entry.get(), course_entry))
        course_add_btn.pack(side=LEFT)
        self.done_btn = Button(course_select_frame, text="Done", bg=self.colors['good'], command = lambda: self.book_search(self.courses))
        self.done_btn.pack(side=LEFT)
        connect_import_frame = Frame()
        connect_import_frame.pack()
        self.all_optional_frames.append(connect_import_frame)
        connect_import_btn = Button(connect_import_frame, text="Import from portal", bg=self.colors['magenta'], command = self.portal_import)
        connect_import_btn.pack(side=LEFT)
        course_div = Frame()
        course_div.pack()
        self.all_optional_frames.append(course_div)
        course_entry_lbl = ttk.Label(course_div, text="Currently added courses:")
        course_entry_lbl.pack()
        self.root.unbind('<Return>')
        self.root.bind('<Return>', lambda a: self.add_course(None, course_entry.get(), course_entry))

    def search_from_box(self, a):
        search = bsh.search(self.c_search.get(), self.colleges)
        if search:
            search_res_frame = Frame(self.root)
            search_res_frame.pack()
            self.all_optional_frames.append(search_res_frame)
            self.c_search_btn.config(state=DISABLED)
            self.c_search.config(state=DISABLED)
            self.c_search.delete(0, END)
            self.c_search.insert(0, search.storename)
            self.college = search
            term_label = ttk.Label(search_res_frame, text="Select what term you're attending: ")
            term_label.pack(side=LEFT)
            terms = bsh.get_terms(search)
            selected_term = StringVar()
            selected_term.set("")
            self.term_options = OptionMenu(search_res_frame, selected_term, *terms.keys())
            self.term_options.config(width=max([len(t) for t in terms.keys()]))
            self.term_options.pack(side=LEFT)
            self.term_btn = Button(search_res_frame, text="Next", bg=self.colors['good'], command = lambda: self.init_course_select(terms[selected_term.get()]))
            self.term_btn.pack(side=LEFT)
        else:
            tkinter.messagebox.showinfo('College not found','Unfortunately, your college was not found. If the spelling is correct, it may not be on bkstr.com.')

BookshelfGui()