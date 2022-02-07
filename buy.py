import re
import books
import users

from tkinter import Tk, Menu, Entry, Frame, Label, StringVar, Button, Listbox, messagebox
from psycopg2 import IntegrityError

from database import cursor, conn


class Buy:
    def __init__(self):
        self.buy_window = Tk()
        self.buy_window.title('Users')
        self.buy_window.geometry('1080x720')
        self.buy_window.resizable(False, False)

        # User Menu
        self.buy_window_menu = Menu(self.buy_window)
        self.buy_window.config(menu=self.buy_window_menu)
        self.buy_menu_option = Menu(self.buy_window_menu)
        self.buy_menu_option.add_command(label='Add User', command=self.open_user_window)
        self.buy_menu_option.add_command(label='Add Book', command=self.open_book_window)
        self.buy_window_menu.add_cascade(label='Add', menu=self.buy_menu_option)

        self.list_container = Frame(self.buy_window)
        self.list_container.pack(fill='both', side='bottom', expand=True)
        self.input_container = Frame(self.buy_window)
        self.input_container.pack(side='bottom', fill='both', expand=True)

        self.user_email_container = Frame(self.input_container)
        self.user_email_label = Label(self.user_email_container, text='User Email: ')
        self.user_email_value = StringVar()
        self.user_email_entry = Entry(self.user_email_container, textvariable=self.user_email_value, width=50)

        self.book_name_container = Frame(self.input_container)
        self.book_name_label = Label(self.book_name_container, text='Book Name: ')
        self.book_name_value = StringVar()
        self.book_name_entry = Entry(self.book_name_container, textvariable=self.book_name_value, width=50)

        self.buy_container = Frame(self.input_container)
        self.buy_btn = Button(self.buy_container, text="Buy Book", command=self.buy_book)

        self.user_email_label.pack()
        self.user_email_entry.pack()
        self.user_email_container.place(x=380, y=20)

        self.book_name_label.pack()
        self.book_name_entry.pack()
        self.book_name_container.place(x=380, y=80)

        self.buy_btn.pack(side='left', padx=10, ipadx=15, ipady=3)
        self.buy_container.place(x=480, y=200)

        cursor.execute('select * from buy')
        buy_list_items = [list(i)[1:] for i in cursor.fetchall()]
        result_items = []
        for i in buy_list_items:
            cursor.execute('select email from users where id = %s', (i[0],))
            user_email = cursor.fetchall()[0][0]
            cursor.execute('select name from books where id = %s', (i[1],))
            book_name = cursor.fetchall()[0][0]
            result_items.append(f'{book_name},{user_email}')

        self.list_items = StringVar(value=result_items)
        self.buy_list = Listbox(self.list_container, listvariable=self.list_items)
        self.buy_list.pack(fill='both', side='left', expand=True)

        self.buy_window.mainloop()

    def open_user_window(self):
        self.buy_window.destroy()
        users.Users()

    def open_book_window(self):
        self.buy_window.destroy()
        books.Books()

    def buy_book(self):
        user_email = self.user_email_value.get()
        book_name = self.book_name_value.get()

        if user_email == '' or book_name == '':
            return messagebox.showerror('Fields Empty', 'Fill the Fields !')

        if not re.fullmatch(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', user_email):
            return messagebox.showerror('Invalid Email', 'Email is Not Valid !')

        try:
            cursor.execute('select id from users where email = %s', (user_email,))
            user_id = cursor.fetchall()[0][0]
            cursor.execute('select id from books where name = %s', (book_name,))
            book_id = cursor.fetchall()[0][0]
            cursor.execute('insert into buy(user_id, book_id) values(%s, %s)', (user_id, book_id))
            conn.commit()
        except IntegrityError:
            cursor.execute("ROLLBACK")
            conn.commit()
            return messagebox.showerror('Something Wrong !', 'Duplicate User and Book !')
        except Exception:
            cursor.execute("ROLLBACK")
            conn.commit()
            return messagebox.showerror('Something Wrong !', f'Check Book Name and User Email !')

        self.user_email_value.set('')
        self.book_name_value.set('')
        self.buy_list.insert(self.buy_list.size(), f'{book_name},{user_email}')


if __name__ == '__main__': Buy()
