import re
import books
import buy
from psycopg2 import IntegrityError
from tkinter import Tk, Menu, Entry, Frame, Label, StringVar, Button, Listbox, messagebox

from database import cursor, conn


class Users:
    def __init__(self):
        self.users_window = Tk()
        self.users_window.title('Users')
        self.users_window.geometry('1080x720')
        self.users_window.resizable(False, False)

        # User Menu
        self.users_window_menu = Menu(self.users_window)
        self.users_window.config(menu=self.users_window_menu)
        self.book_menu_option = Menu(self.users_window_menu)
        self.book_menu_option.add_command(label='Add Book', command=self.open_book_window)
        self.book_menu_option2 = Menu(self.users_window_menu)
        self.book_menu_option2.add_command(label='Buy Book', command=self.open_buy_window)
        self.users_window_menu.add_cascade(label='Add', menu=self.book_menu_option)
        self.users_window_menu.add_cascade(label='Buy', menu=self.book_menu_option2)

        self.list_container = Frame(self.users_window)
        self.list_container.pack(fill='both', side='bottom', expand=True)
        self.data_container = Frame(self.users_window)
        self.data_container.pack(fill='both', side='bottom', expand=True)
        self.input_container = Frame(self.data_container)
        self.input_container.pack(side='left', fill='both', expand=True)
        self.search_container = Frame(self.data_container)
        self.search_container.pack(side='left', fill='both', expand=True)

        self.first_name_container = Frame(self.input_container)
        self.first_name_label = Label(self.first_name_container, text='FirstName: ')
        self.first_name_value = StringVar()
        self.first_name_entry = Entry(self.first_name_container, textvariable=self.first_name_value, width=50)

        self.last_name_container = Frame(self.input_container)
        self.last_name_label = Label(self.last_name_container, text='LastName: ')
        self.last_name_value = StringVar()
        self.last_name_entry = Entry(self.last_name_container, textvariable=self.last_name_value, width=50)

        self.email_container = Frame(self.input_container)
        self.email_label = Label(self.email_container, text='Email: ')
        self.email_value = StringVar()
        self.email_entry = Entry(self.email_container, textvariable=self.email_value, width=50)

        self.edit_container = Frame(self.input_container)
        self.add_btn = Button(self.edit_container, text="Add User", command=self.add_user)
        self.delete_btn = Button(self.edit_container, text="Delete", command=self.delete_user)
        self.update_btn = Button(self.edit_container, text="Update", command=self.update_user)

        self.first_name_label.pack()
        self.first_name_entry.pack()
        self.first_name_container.place(x=100, y=20)

        self.last_name_label.pack()
        self.last_name_entry.pack()
        self.last_name_container.place(x=100, y=80)

        self.email_label.pack()
        self.email_entry.pack()
        self.email_container.place(x=100, y=140)

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

        cursor.execute('select * from users')
        items = [','.join(list(user)[1:]) for user in cursor.fetchall()]

        self.list_items = StringVar(value=items)
        self.user_list = Listbox(self.list_container, listvariable=self.list_items)
        self.user_list.pack(fill='both', side='left', expand=True)

        # main loop
        self.users_window.mainloop()

    def add_list(self, item):
        self.user_list.insert(self.user_list.size(), item)

    def add_user(self):
        first_name = self.first_name_value.get()
        last_name = self.last_name_value.get()
        email = self.email_value.get()

        if first_name == '' or last_name == '' or email == '':
            return messagebox.showinfo('Fields Empty !', 'Please Fill Fields !')

        if not re.fullmatch(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', email):
            return messagebox.showerror('Email Invalid !', 'Your Email is Not Valid :( ')
        try:
            cursor.execute('INSERT INTO users(first_name, last_name, email) values(%s, %s, %s)',
                           (first_name, last_name, email))
            conn.commit()

        except IntegrityError:
            cursor.execute("ROLLBACK")
            conn.commit()
            return messagebox.showerror('Something Wrong !', 'Your Email is Duplicate !')
        except Exception as e:
            cursor.execute("ROLLBACK")
            conn.commit()
            return messagebox.showerror('Something Wrong !', f'{e}')

        self.first_name_value.set('')
        self.last_name_value.set('')
        self.email_value.set('')

        item = f'{first_name},{last_name},{email}'
        self.add_list(item)

    def update_user(self):
        user = self.delete_user()
        if user:
            self.first_name_value.set(user[0])
            self.last_name_value.set(user[1])
            self.email_value.set(user[2])
        return

    def delete_user(self):
        user_index = self.user_list.curselection()
        if len(user_index) == 0:
            messagebox.showinfo('Nothing Select !', 'Please Select Item !')
            return
        user = self.user_list.get(user_index).split(',')

        self.user_list.delete(user_index)
        try:
            cursor.execute('delete from users where email = %s', (user[2],))
            conn.commit()
        except Exception as e:
            cursor.execute("ROLLBACK")
            conn.commit()
            return messagebox.showerror('Something Wrong !', f'{e}')

        return user

    def search_user(self):
        search_query = self.search_value.get().strip()

        if search_query == '':
            self.search_res.set([])
            return messagebox.showinfo('Enter Something', 'Please Enter Query')

        try:
            cursor.execute('select * from users where email = %s or first_name = %s or last_name = %s',
                           (search_query, search_query, search_query))
            conn.commit()
        except Exception as e:
            self.search_res.set([])
            cursor.execute("ROLLBACK")
            conn.commit()
            return messagebox.showerror('Something Wrong !', f'{e}')

        result = [','.join(list(user)[1:]) for user in cursor.fetchall()]

        if len(result) == 0:
            self.search_res.set([])
            return messagebox.showinfo('Not Found !', 'Nothing Found !')

        self.search_value.set('')

        self.search_res.set(result)

    def open_book_window(self):
        self.users_window.destroy()
        books.Books()

    def open_buy_window(self):
        self.users_window.destroy()
        buy.Buy()


if __name__ == '__main__': Users()
