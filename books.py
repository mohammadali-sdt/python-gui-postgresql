import users
import buy
from psycopg2 import IntegrityError
from tkinter import Tk, Menu, Entry, Frame, Label, StringVar, Button, Listbox, messagebox

from database import cursor, conn


class Books:
    def __init__(self):
        self.books_window = Tk()
        self.books_window.title('Books')
        self.books_window.geometry('1080x720')
        self.books_window.resizable(False, False)

        # User Menu
        self.books_window_menu = Menu(self.books_window)
        self.books_window.config(menu=self.books_window_menu)
        self.book_menu_option = Menu(self.books_window_menu)
        self.book_menu_option.add_command(label='Buy Book', command=self.open_buy_window)
        self.book_menu_option2 = Menu(self.books_window_menu)
        self.book_menu_option2.add_command(label='Add User', command=self.open_user_window)
        self.books_window_menu.add_cascade(label='Add', menu=self.book_menu_option2)
        self.books_window_menu.add_cascade(label='Buy', menu=self.book_menu_option)

        self.list_container = Frame(self.books_window)
        self.list_container.pack(fill='both', side='bottom', expand=True)
        self.data_container = Frame(self.books_window)
        self.data_container.pack(fill='both', side='bottom', expand=True)
        self.input_container = Frame(self.data_container)
        self.input_container.pack(side='left', fill='both', expand=True)
        self.search_container = Frame(self.data_container)
        self.search_container.pack(side='left', fill='both', expand=True)

        self.name_container = Frame(self.input_container)
        self.name_label = Label(self.name_container, text='Name: ')
        self.name_value = StringVar()
        self.name_entry = Entry(self.name_container, textvariable=self.name_value, width=50)

        self.writer_container = Frame(self.input_container)
        self.writer_label = Label(self.writer_container, text='Writer: ')
        self.writer_value = StringVar()
        self.writer_entry = Entry(self.writer_container, textvariable=self.writer_value, width=50)

        self.price_container = Frame(self.input_container)
        self.price_label = Label(self.price_container, text='Price: ')
        self.price_value = StringVar()
        self.price_entry = Entry(self.price_container, textvariable=self.price_value, width=50)

        self.edit_container = Frame(self.input_container)
        self.add_btn = Button(self.edit_container, text="Add Book", command=self.add_book)
        self.delete_btn = Button(self.edit_container, text="Delete", command=self.delete_user)
        self.update_btn = Button(self.edit_container, text="Update", command=self.update_user)

        self.name_label.pack()
        self.name_entry.pack()
        self.name_container.place(x=100, y=20)

        self.writer_label.pack()
        self.writer_entry.pack()
        self.writer_container.place(x=100, y=80)

        self.price_label.pack()
        self.price_entry.pack()
        self.price_container.place(x=100, y=140)

        self.add_btn.pack(side='left', padx=10, ipadx=15, ipady=3)
        self.update_btn.pack(side='left', padx=10, ipadx=15, ipady=3)
        self.delete_btn.pack(side='left', padx=10, ipadx=15, ipady=3)
        self.edit_container.place(x=100, y=200)

        self.search_input_container = Frame(self.search_container)
        self.search_label = Label(self.search_input_container, text='Search: ')
        self.search_value = StringVar()
        self.search_entry = Entry(self.search_input_container, textvariable=self.search_value, width=50)
        self.search_btn = Button(self.search_container, text="Search", command=self.search_user)

        self.search_res = StringVar()
        self.search_list = Listbox(self.search_container, listvariable=self.search_res, width=50)

        self.search_label.pack()
        self.search_entry.pack()
        self.search_input_container.place(x=100, y=20)
        self.search_btn.place(x=230, y=70)

        self.search_list.place(x=100, y=100)

        cursor.execute('select * from books')
        items = [list(book)[1:] for book in cursor.fetchall()]
        _items = [f'{i[0]},{i[1]},{str(i[2])}' for i in items]
        self.list_items = StringVar(value=_items)
        self.book_list = Listbox(self.list_container, listvariable=self.list_items)
        self.book_list.pack(fill='both', side='left', expand=True)

        # main loop
        self.books_window.mainloop()

    def add_list(self, item):
        self.book_list.insert(self.book_list.size(), item)

    def add_book(self):
        name = self.name_value.get()
        wirter = self.writer_value.get()
        price = self.price_value.get()

        if name == '' or wirter == '' or price == '':
            return messagebox.showinfo('Fields Empty !', 'Please Fill Fields !')

        try:
            cursor.execute('INSERT INTO books(name, writer, price) values(%s, %s, %s)',
                           (name, wirter, price))
            conn.commit()
        except IntegrityError:
            cursor.execute("ROLLBACK")
            conn.commit()
            return messagebox.showerror('Duplicate Name', 'Name of Book is Duplicate !')
        except Exception as e:
            cursor.execute("ROLLBACK")
            conn.commit()
            return messagebox.showerror('Something Wrong !', f'{e}')

        self.name_value.set('')
        self.writer_value.set('')
        self.price_value.set('')

        item = f'{name},{wirter},{price}'
        self.add_list(item)

    def update_user(self):
        book = self.delete_user()
        if book:
            self.name_value.set(book[0])
            self.writer_value.set(book[1])
            self.price_value.set(book[2])
        return

    def delete_user(self):
        book_index = self.book_list.curselection()
        if len(book_index) == 0:
            messagebox.showinfo('Nothing Select !', 'Please Select Item !')
            return
        book = self.book_list.get(book_index).split(',')

        self.book_list.delete(book_index)
        try:
            cursor.execute('delete from books where name = %s and writer = %s', (book[0], book[1]))
            conn.commit()
        except Exception as e:
            cursor.execute("ROLLBACK")
            conn.commit()
            return messagebox.showerror('Something Wrong !', f'{e}')

        return book

    def search_user(self):
        search_query = self.search_value.get().strip()

        if search_query == '':
            self.search_res.set([])
            return messagebox.showinfo('Enter Something', 'Please Enter Query')

        try:
            cursor.execute('select * from books where name = %s or writer = %s', (search_query, search_query))
            conn.commit()
        except Exception as e:
            self.search_res.set([])
            cursor.execute("ROLLBACK")
            conn.commit()
            return messagebox.showerror('Something Wrong !', f'{e}')

        result = [list(book)[1:] for book in cursor.fetchall()]
        book_result = [f'{i[0]},{i[1]},{str(i[2])}' for i in result]
        print(book_result)

        if len(book_result) == 0:
            self.search_res.set([])
            return messagebox.showinfo('Not Found !', 'Nothing Found !')

        self.search_value.set('')

        self.search_res.set(book_result)

    def open_user_window(self):
        self.books_window.destroy()
        users.Users()

    def open_buy_window(self):
        self.books_window.destroy()
        buy.Buy()


if __name__ == '__main__': Books()
