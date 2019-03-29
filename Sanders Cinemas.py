import sqlite3
import tkinter.messagebox
import tkinter.ttk
from datetime import datetime, date
from functools import partial
from random import randrange
from tkinter import *

from PIL import Image, ImageTk


# Please note, as shown in the video, the password for Montgomery_Burns has been changed to abcd
# If this code is being ran in isolation (without the database files in the directory),
# uncomment lines 923 and 946 once to create and add values to the databases

class Error(Exception):
    """Base class for other exceptions"""
    pass


class UsernameNotUniqueError(Error):
    """Raised when the username is not unique"""
    pass


class InvalidEmailError(Error):
    """Raised when the email address does not contain an @ symbol or has an empty username or domain name"""
    pass


class PasswordsDoNotMatchError(Error):
    """Raised when the entered passwords for a new account do not match"""
    pass


class EmptyCellsError(Error):
    """Raised when at least one of the required input fields is empty"""


class MainPage(Frame):
    """Main page when the GUI is ran. Allows the user to select customer or employee"""

    def __init__(self, master):
        self.master = master
        self.frame = Frame(self.master)
        self.label = Label(self.master, image=back_pic)
        self.label.place(x=0, y=0, relwidth=1, relheight=1)
        self.title_label = Label(self.master, font=("Helvetica", 16),
                                 text="Welcome to Sanders Cinemas!! Please select whether"
                                      " you are a customer or employee:").pack(pady='3')
        self.cust_button = Button(self.master, font=("Helvetica", 16), text="Customer", bg="green",
                                  command=self.customer_window).pack(pady='3')
        self.emp_button = Button(self.master, font=("Helvetica", 16), text="Employee", bg="blue",
                                 command=self.employee_window).pack(pady='3')
        self.quit = Button(self.master, font=("Helvetica", 12), text="Quit", bg="black", fg='white',
                           command=self.master.quit).pack(pady='3')
        self.frame.pack()

    def customer_window(self):
        self.newWindow = Toplevel(self.master)
        self.newWindow.geometry('1096x720')
        self.app = Customer(self.newWindow)
        self.master.withdraw()

    def employee_window(self):
        self.newWindow = Toplevel(self.master)
        self.newWindow.geometry('1096x720')
        self.app = Employee(self.newWindow)
        self.master.withdraw()


class Customer(MainPage):
    """Customer login page"""

    def __init__(self, master):
        self.master = master
        self.frame = Frame(self.master)
        self.label = Label(self.master, image=back_pic)
        self.label.place(x=0, y=0, relwidth=1, relheight=1)
        self.frame.grid(row=0, column=0)
        self.title = Label(self.master, font=("Helvetica", 16), text='Please enter your username and password')
        self.title.grid(row=0, columnspan=6)
        self.usr = Label(self.master, text="Username:", width=15).grid(row=1, column=0, pady='3')
        self.username = Entry(self.master, width=30)
        self.username.grid(row=1, column=1, pady='3')
        self.psd = Label(self.master, text="Password:", width=15).grid(row=2, column=0, pady='3')
        self.password = Entry(self.master, show="*", width=30)
        self.password.grid(row=2, column=1, pady='3')
        self.checkbox = Checkbutton(self.master, text="Keep me logged in")
        self.checkbox.grid(row=3, column=0, columnspan=2, pady='3')
        self.loginbutton = Button(self.master, text="Login", command=self.login).grid(row=4, column=1, pady='3')
        self.back = Button(self.master, text="Back", command=self.back).grid(row=4, column=0, pady='3')
        self.createnewaccount = Button(self.master, text="Create New Customer Account", command=self.create).grid(row=5,
                                                                                                                  column=0,
                                                                                                                  columnspan=2,
                                                                                                                  pady='3')

    def create(self):
        self.newWindow = Toplevel(self.master)
        self.newWindow.geometry('1096x720')
        self.app = NewAccount(self.newWindow)
        self.master.withdraw()

    def login(self):
        global username
        global password
        username = self.username.get()
        password = self.password.get()
        c.execute('SELECT * FROM customers WHERE username = ? AND password = ?', (username, password))
        login1 = c.fetchone()
        if login1:
            self.newWindow = Toplevel(self.master)
            self.newWindow.geometry('1096x720')
            self.app = CustMain(self.newWindow)
            self.master.withdraw()
            tkinter.messagebox.showinfo("-- COMPLETE --", "You Have Now Logged In.", icon="info")
        else:
            tkinter.messagebox.showinfo("-- ERROR --", "Please enter valid infomation!", icon="warning")

    def back(self):
        self.newWindow = Toplevel(self.master)
        self.newWindow.geometry('1096x720')
        self.app = MainPage(self.newWindow)
        self.master.withdraw()


class CustMain(Customer):
    '''Customer main menu page. Allows user to update profile, see booking history, and search for films by date'''

    def __init__(self, master):
        self.master = master
        self.frame = Frame(self.master)
        self.label = Label(self.master, image=back_pic)
        self.label.place(x=0, y=0, relwidth=1, relheight=1)
        self.frame.pack()
        self.up = Button(self.master, font=("Helvetica", 16), text="Update Profile", bg="yellow",
                         command=self.Update_Profile_window).pack(pady='5')
        self.bh = Button(self.master, font=("Helvetica", 16), text="Booking History", bg="yellow",
                         command=self.Booking_History_window).pack(pady='5')
        self.search = Label(self.master, font=("Helvetica", 16), text='Search for films by date:').pack()
        self.defdate1 = StringVar(self.master)
        self.defdate1.set("Monday 14/01/19")  # default value
        self.datelist1 = OptionMenu(master, self.defdate1, "Monday 14/01/19", "Tuesday 15/01/19", "Wednesday 16/01/19",
                                    "Thursday 17/01/19", "Friday 18/01/19", "Saturday 19/01/19", "Sunday 20/01/19")
        self.datelist1.pack()
        self.searching = Button(self.master, text="Search", command=self.sch).pack()
        self.log = Button(self.master, font=("Helvetica", 12), text="Logout", fg="white", bg='black',
                          command=self.logout).pack(pady='5')

    def sch(self):
        search_date = self.defdate1.get()
        c2.execute("""SELECT * FROM movies WHERE
                            date = ? ORDER BY time='1pm' DESC,
                                                time='2pm' DESC,
                                                time='3pm' DESC,
                                                time='4pm' DESC,
                                                time='5pm' DESC,
                                                time='6pm' DESC,
                                                time='7pm' DESC,
                                                time='8pm' DESC,
                                                time='9pm' DESC,
                                                time='10pm' DESC """, (search_date,))
        output = c2.fetchall()
        self.newWindow = Toplevel(self.master)
        self.newWindow.geometry('1096x720')
        self.app = SearchResults(self.newWindow, output, search_date)
        self.master.withdraw()

    def Update_Profile_window(self):
        self.newWindow = Toplevel(self.master)
        self.newWindow.geometry('1096x720')
        self.app = CustProfile(self.newWindow)
        self.master.withdraw()

    def Booking_History_window(self):
        self.newWindow = Toplevel(self.master)
        self.newWindow.geometry('1096x720')
        self.app = BookHist(self.newWindow)
        self.master.withdraw()

    def logout(self):
        msg = tkinter.messagebox.askyesno('Logout', 'Are you sure you want to log out?')
        if msg:
            self.newWindow = Toplevel(self.master)
            self.newWindow.geometry('1096x720')
            self.app = MainPage(self.newWindow)
            self.master.withdraw()


class SearchResults(CustMain):
    def __init__(self, master, output, search_date):
        self.search_date = search_date
        self.master = master
        self.output = output
        self.frame = Frame(self.master)
        self.label = Label(self.master, image=back_pic)
        self.label.place(x=0, y=0, relwidth=1, relheight=1)
        self.frame.grid(row=0, column=0)
        self.date = Label(self.master, text='Date', font=("Helvetica", 16), width=8).grid(row=0, column=1, pady='1')
        self.time = Label(self.master, text='Time', font=("Helvetica", 16), width=6).grid(row=0, column=2, pady='1')
        self.title = Label(self.master, text='Title', font=("Helvetica", 16), width=15).grid(row=0, column=3, pady='1')
        self.description = Label(self.master, text='Description', font=("Helvetica", 16), width=30).grid(row=0,
                                                                                                         column=4,
                                                                                                         pady='1')
        self.booked = Label(self.master, text='Booked', font=("Helvetica", 16), width=8).grid(row=0, column=5, pady='1')
        self.available = Label(self.master, text='Available', font=("Helvetica", 16), width=8).grid(row=0, column=6,
                                                                                                    pady='1')
        self.book = Label(self.master, text='Book ticket', font=("Helvetica", 16), width=12).grid(row=0, column=7,
                                                                                                  pady='1')
        widths = (15, 6, 35, 60, 8, 8, 12)
        for i in self.output:
            for j in i:
                b = Label(self.master, text=j, font=("Helvetica", 6), width=widths[i.index(j)])
                b.grid(row=output.index(i) + 1, column=i.index(j) + 1, pady='1')
            # c2.execute('SELECT booked FROM movies WHERE rowid=?', (output.index(i) + 1,))
            # self.taken = c2.fetchone()[0]  # returns the number of available seats for that movie
            # c2.execute('SELECT date, time FROM movies WHERE date=? AND rowid=?',
            # (self.search_date, output.index(i) + 1,))
            # self.datetime = c2.fetchone()  # returns the date and time of the movie
            self.taken = i[4]
            self.datetime = (i[0], i[1])
            d = Button(self.master, text='Book', command=partial(self.boo, self.taken, self.datetime),
                       font=("Helvetica", 7))
            d.grid(row=output.index(i) + 1, column=7, pady='1')
        self.back = Button(self.master, font=("Helvetica", 12), text="Back", bg="black", fg="white",
                           command=self.back).grid(row=10, column=1, pady='1')
        self.log = Button(self.master, font=("Helvetica", 12), text="Logout", fg="white", bg='black',
                          command=self.logout).grid(row=10, column=2, pady='1')

    def boo(self, gone, datetime7):
        msg = tkinter.messagebox.askyesno('Book', 'Do you want to confirm this booking?')
        if msg:
            self.gone = gone
            self.datetime = datetime7
            self.usr = username.split('_')
            c3.execute("""SELECT * FROM bookings WHERE
            username = ? AND
            date = ? AND
            time = ?""", (username, self.datetime[0], self.datetime[1]))
            alr = c3.fetchone()
            if alr:
                tkinter.messagebox.showinfo("---- ERROR ----", "You are already booked into this film", icon="warning")
            elif self.gone == 100:
                tkinter.messagebox.showinfo("---- ERROR ----", "Movie showing full", icon="warning")
            else:
                td_hour = datetime.today().hour - 12
                td_day = date.today().day
                td_month = date.today().month
                td_year = date.today().year
                new_time = int(self.datetime[1][:-2])
                temp_date = self.datetime[0].split()
                new_date = int(temp_date[1][:2])
                # print(new_time, new_date)
                if td_year > 2019 or \
                        td_year == 2019 and td_month > 1 or \
                        td_year == 2019 and td_month == 1 and td_day > new_date or \
                        td_year == 2019 and td_month == 1 and td_day == new_date and td_hour >= new_time:
                    tkinter.messagebox.showinfo("---- ERROR ----", "Date and time of showing has passed!",
                                                icon="warning")
                else:
                    with conn2:
                        c2.execute('''UPDATE movies SET booked = ?, available = ? WHERE
                        date = ? AND time = ?''', (self.gone + 1, 100 - (self.gone + 1), datetime7[0], datetime7[1]))
                    self.newWindow = Toplevel(self.master)
                    self.newWindow.geometry('1096x720')
                    self.app = Booked(self.newWindow, self.datetime)
                    self.master.withdraw()

    def back(self):
        self.newWindow = Toplevel(self.master)
        self.newWindow.geometry('1096x720')
        self.app = CustMain(self.newWindow)
        self.master.withdraw()


class CustProfile(CustMain):
    '''Allows the customer to update their profile'''

    def __init__(self, master):
        self.master = master
        self.frame = Frame(self.master)
        self.label = Label(self.master, image=back_pic)
        self.label.place(x=0, y=0, relwidth=1, relheight=1)
        self.frame.grid(row=0, column=0)
        self.usr = username.split('_')
        c.execute('SELECT * FROM customers WHERE username = ?', (username,))

        self.title = Label(self.master, text="Please update your details below:", font=("Helvetica", 16)).grid(row=0,
                                                                                                               column=0,
                                                                                                               columnspan=2,
                                                                                                               pady='3')

        self.output = c.fetchone()
        self.first = Label(self.master, text="First Name:", width='15').grid(row=1, column=0, pady='3')
        self.firstname = Entry(self.master, width='30')
        self.firstname.insert(END, self.output[0])
        self.firstname.grid(row=1, column=1, pady='3')

        self.last = Label(self.master, text="Last Name:", width='15').grid(row=2, column=0, pady='3')
        self.lastname = Entry(self.master, width='30')
        self.lastname.insert(END, self.output[1])
        self.lastname.grid(row=2, column=1, pady='3')

        self.email = Label(self.master, text="Email Address:", width='15').grid(row=3, column=0, pady='3')
        self.emailadd = Entry(self.master, width='30')
        self.emailadd.insert(END, self.output[2])
        self.emailadd.grid(row=3, column=1, pady='3')

        self.ag = Label(self.master, text="Age:", width='15').grid(row=4, column=0, pady='3')
        self.age = Entry(self.master, width='30')
        self.age.insert(END, self.output[3])
        self.age.grid(row=4, column=1, pady='3')

        self.ps1 = Label(self.master, text="Password:", width='15').grid(row=5, column=0, pady='3')
        self.firstpassword = Entry(self.master, width='30', show='*')
        self.firstpassword.insert(END, self.output[5])
        self.firstpassword.grid(row=5, column=1, pady='3')

        self.ps2 = Label(self.master, text="Confirm Password:", width='15').grid(row=6, column=0, pady='3')
        self.secondpassword = Entry(self.master, width='30', show='*')
        self.secondpassword.insert(END, self.output[5])
        self.secondpassword.grid(row=6, column=1, pady='3')

        self.update = Button(self.master, text="Update Details", command=self.change).grid(row=7, columnspan=2,
                                                                                           pady='3')

        self.back = Button(self.master, font=("Helvetica", 12), text="Back", fg="white", bg='black',
                           command=self.back).grid(row=8, column=0, pady='3')
        self.log = Button(self.master, font=("Helvetica", 12), text="Logout", fg="white", bg='black',
                          command=self.logout).grid(row=8, column=1, pady='3')

    def change(self):
        msg = tkinter.messagebox.askyesno('Update Profile', 'Confirm changes?')
        if msg:
            new_first = self.firstname.get()
            new_last = self.lastname.get()
            new_email = self.emailadd.get()
            new_age = self.age.get()
            new_firstpassword = self.firstpassword.get()
            new_secondpassword = self.secondpassword.get()

            try:
                if not new_first or not new_last or not new_email or not new_age:
                    raise EmptyCellsError
                new_age = int(new_age)
                if new_age < 0:
                    raise ValueError
                if '@' and '.' in new_email:
                    s = new_email.split('@')
                    t = s[1].split('.')
                    if not (s[0] and t[0] and t[1]):
                        raise InvalidEmailError
                else:
                    raise InvalidEmailError
                if new_firstpassword != new_secondpassword:
                    raise PasswordsDoNotMatchError

            except EmptyCellsError:
                tkinter.messagebox.showinfo("---- ERROR ----", "Please fill in all of the cells.", icon="warning")
            except InvalidEmailError:
                tkinter.messagebox.showinfo("---- ERROR ----", "Invalid email format!", icon="warning")
            except PasswordsDoNotMatchError:
                tkinter.messagebox.showinfo("---- ERROR ----", "Passwords do not match!", icon="warning")
            except ValueError:
                tkinter.messagebox.showinfo("---- ERROR ----", "Invalid age format!", icon="warning")
            else:
                with conn:
                    c.execute("""UPDATE customers
                            SET first = ?,
                                last = ?,
                                email = ?,
                                age = ?,
                                password = ?
                            WHERE username = ?""",
                              (new_first, new_last, new_email, new_age, new_firstpassword, username))
                self.newWindow = Toplevel(self.master)
                self.newWindow.geometry('1096x720')
                self.app = CustProfile(self.newWindow)
                self.master.withdraw()
                tkinter.messagebox.showinfo("---- SUCCESSFUL ----", "Profile successfully updated.",
                                            icon="info")

    def back(self):
        self.newWindow = Toplevel(self.master)
        self.newWindow.geometry('1096x720')
        self.app = CustMain(self.newWindow)
        self.master.withdraw()


class NewAccount(Customer):
    def __init__(self, master):
        self.master = master
        self.frame = Frame(self.master)
        self.label = Label(self.master, image=back_pic)
        self.label.place(x=0, y=0, relwidth=1, relheight=1)
        self.frame.grid(row=0, column=0)

        self.title = Label(self.master, text="Please enter your details below:", font=("Helvetica", 16)).grid(row=0,
                                                                                                              column=0,
                                                                                                              columnspan=2,
                                                                                                              pady='3')

        self.first = Label(self.master, text="First Name:", width='15').grid(row=1, column=0, pady='3')
        self.firstname = Entry(self.master, width='30')
        self.firstname.grid(row=1, column=1, pady='3')

        self.last = Label(self.master, text="Last Name:", width='15').grid(row=2, column=0, pady='3')
        self.lastname = Entry(self.master, width='30')
        self.lastname.grid(row=2, column=1, pady='3')

        self.email = Label(self.master, text="Email Address:", width='15').grid(row=3, column=0, pady='3')
        self.emailadd = Entry(self.master, width='30')
        self.emailadd.grid(row=3, column=1, pady='3')

        self.ag = Label(self.master, text="Age:", width='15').grid(row=4, column=0, pady='3')
        self.age = Entry(self.master, width='30')
        self.age.grid(row=4, column=1, pady='3')

        self.newusrname = Label(self.master, text="Username:", width='15').grid(row=5, column=0, pady='3')
        self.newusername = Entry(self.master, width='30')
        self.newusername.grid(row=5, column=1, pady='3')

        self.newpasswd1 = Label(self.master, text="Password:", width='15').grid(row=6, column=0, pady='3')
        self.newpassword1 = Entry(self.master, width='30', show="*")
        self.newpassword1.grid(row=6, column=1, pady='3')

        self.newpasswd2 = Label(self.master, text="Confirm Password:", width='15').grid(row=7, column=0, pady='3')
        self.newpassword2 = Entry(self.master, width='30', show="*")
        self.newpassword2.grid(row=7, column=1, pady='3')

        self.update = Button(self.master, text="Create new account", command=self.change).grid(row=8, columnspan=2,
                                                                                               pady='3')

        self.back = Button(self.master, font=("Helvetica", 12), text="Back", fg="white", bg='black',
                           command=self.back).grid(row=9, column=0, pady='3')

    def change(self):
        new_first = self.firstname.get()
        new_last = self.lastname.get()
        new_email = self.emailadd.get()
        new_age = self.age.get()
        new_username = self.newusername.get()
        new_password1 = self.newpassword1.get()
        new_password2 = self.newpassword2.get()
        try:
            if not new_first or not new_last or not new_email or not new_age or not new_username or not new_password1 or not new_password2:
                raise EmptyCellsError
            new_age = int(new_age)
            if new_age < 0:
                raise ValueError
            if '@' and '.' in new_email:
                s = new_email.split('@')
                t = s[1].split('.')
                if not (s[0] and t[0] and t[1]):
                    raise InvalidEmailError
            else:
                raise InvalidEmailError
            if new_password1 != new_password2:
                raise PasswordsDoNotMatchError
            c.execute('SELECT * FROM customers WHERE username = ?', (new_username,))
            possibleunique = c.fetchone()
            if possibleunique:
                raise UsernameNotUniqueError

        except EmptyCellsError:
            tkinter.messagebox.showinfo("---- ERROR ----", "Please fill in all of the cells.", icon="warning")
        except InvalidEmailError:
            tkinter.messagebox.showinfo("---- ERROR ----", "Invalid email format!", icon="warning")
        except UsernameNotUniqueError:
            tkinter.messagebox.showinfo("---- ERROR ----", "Username already taken!", icon="warning")
        except PasswordsDoNotMatchError:
            tkinter.messagebox.showinfo("---- ERROR ----", "Passwords do not match!", icon="warning")
        except ValueError:
            tkinter.messagebox.showinfo("---- ERROR ----", "Invalid age format!", icon="warning")
        else:
            with conn:
                c.execute("""INSERT INTO customers VALUES (?, ?, ?, ?, ?, ?)""",
                          (new_first, new_last, new_email, new_age, new_username, new_password1))
            self.newWindow = Toplevel(self.master)
            self.newWindow.geometry('1096x720')
            self.app = Customer(self.newWindow)
            self.master.withdraw()
            tkinter.messagebox.showinfo("---- SUCCESSFUL ----", "Account successfully created.",
                                        icon="info")

    def back(self):
        self.newWindow = Toplevel(self.master)
        self.newWindow.geometry('1096x720')
        self.app = Customer(self.newWindow)
        self.master.withdraw()


class Booked(CustProfile, SearchResults):
    def __init__(self, master, datetime1):
        self.datetime1 = datetime1
        self.master = master
        self.frame = Frame(self.master)
        self.label = Label(self.master, image=back_pic)
        self.label.place(x=0, y=0, relwidth=1, relheight=1)
        self.frame.grid(row=0, column=0, pady='1')
        self.usr = username.split('_')

        c.execute('SELECT * FROM customers WHERE username = ?', (username,))

        self.heading = Label(self.master, text='Booking successful! booking details are below:', width=45,
                             font=("Helvetica", 16)).grid(row=0, columnspan=2, pady='5')

        self.output = c.fetchone()
        self.first = Label(self.master, text="First Name:", width=15).grid(row=1, column=0, pady='3')
        self.firstname = Label(self.master, text=self.output[0], width=30)
        self.firstname.grid(row=1, column=1, pady='3')

        self.last = Label(self.master, text="Last Name:", width=15).grid(row=2, column=0, pady='3')
        self.lastname = Label(self.master, text=self.output[1], width=30)
        self.lastname.grid(row=2, column=1, pady='3')

        self.email = Label(self.master, text="Email Address:", width=15).grid(row=3, column=0, pady='3')
        self.emailadd = Label(self.master, text=self.output[2], width=30)
        self.emailadd.grid(row=3, column=1, pady='3')

        self.ag = Label(self.master, text="Age:", width=15).grid(row=4, column=0, pady='3')
        self.age = Label(self.master, text=self.output[3], width=30)
        self.age.grid(row=4, column=1, pady='3')

        self.da = Label(self.master, text="Date:", width=15).grid(row=5, column=0, pady='3')
        self.date = Label(self.master, text=self.datetime1[0], width=30)
        self.date.grid(row=5, column=1, pady='3')

        self.ti = Label(self.master, text="Time:", width=15).grid(row=6, column=0, pady='3')
        self.time = Label(self.master, text=self.datetime1[1], width=30)
        self.time.grid(row=6, column=1, pady='3')

        c2.execute('''SELECT booked FROM movies WHERE
                    date = ? AND time = ?''', (self.datetime1[0], self.datetime1[1]))
        numb = str(c2.fetchone()[0])
        if len(numb) == 1:
            numb = '0' + str(numb)
        numb0 = int(numb[0])
        numb1 = int(numb[1])
        list_of_rows = ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J')
        seat_row = list_of_rows[numb0]
        seat_number = str(seat_row) + str(numb1)

        self.se = Label(self.master, text="Seat Number:", width=15).grid(row=7, column=0, pady='1')
        self.seat = Label(self.master, text=seat_number, width=30)
        self.seat.grid(row=7, column=1, pady='1')

        self.back = Button(self.master, font=("Helvetica", 12), text="Back", fg="white", bg='black',
                           command=self.back).grid(row=8, column=0, pady='1')
        self.log = Button(self.master, font=("Helvetica", 12), text="Logout", fg="white", bg='black',
                          command=self.logout).grid(row=8, column=1, pady='1')

        c.execute('SELECT first, last FROM customers WHERE username = ?', (username,))
        namess = c.fetchall()[0]
        with conn3:
            c3.execute('INSERT INTO bookings VALUES (?, ?, ?, ?, ?, ?)', (namess[0], namess[1], self.datetime1[0],
                                                                          self.datetime1[1], seat_number, username))


class BookHist(Booked):
    def __init__(self, master):
        self.master = master
        self.frame = Frame(self.master)
        self.label = Label(self.master, image=back_pic)
        self.label.place(x=0, y=0, relwidth=1, relheight=1)
        self.frame.grid(row=0, column=0)
        self.usr = username.split('_')

        self.date = Label(self.master, text='Date', font=("Helvetica", 16), width='15').grid(row=0, column=0)
        self.time = Label(self.master, text='Time', font=("Helvetica", 16), width='10').grid(row=0, column=1)
        self.title = Label(self.master, text='Title', font=("Helvetica", 16), width='33').grid(row=0, column=2)
        self.seatno = Label(self.master, text='Seat Number', font=("Helvetica", 16), width='15').grid(row=0, column=3)
        self.remo = Label(self.master, text='Remove Booking', font=("Helvetica", 16), width='15').grid(row=0, column=4)

        c3.execute('''SELECT date, time, seatno FROM bookings WHERE
                    username = ? ORDER BY date='Monday 14/01/19' DESC,
                                                    date='Tuesday 15/01/19' DESC,
                                                    date='Wednesday 16/01/19' DESC,
                                                    date='Thursday 17/01/19' DESC,
                                                    date='Friday 18/01/19' DESC,
                                                    date='Saturday 19/01/19' DESC,
                                                    date='Sunday 20/01/19' DESC,
                                                    time='1pm' DESC,
                                                    time='2pm' DESC,
                                                    time='3pm' DESC,
                                                    time='4pm' DESC,
                                                    time='5pm' DESC,
                                                    time='6pm' DESC,
                                                    time='7pm' DESC,
                                                    time='8pm' DESC,
                                                    time='9pm' DESC,
                                                    time='10pm' DESC''', (username,))
        tempresult = c3.fetchall()
        for i in tempresult:
            c2.execute('''SELECT title FROM movies WHERE
                        date = ? AND time = ?''', (i[0], i[1]))
            history = c2.fetchone()
            b0 = Label(self.master, text=i[0], font=("Helvetica", 12), width='17')
            b0.grid(row=tempresult.index(i) + 1, column=0)
            b1 = Label(self.master, text=i[1], font=("Helvetica", 12), width='10')
            b1.grid(row=tempresult.index(i) + 1, column=1)
            b2 = Label(self.master, text=history[0], font=("Helvetica", 12), width='40')
            b2.grid(row=tempresult.index(i) + 1, column=2)
            b4 = Label(self.master, text=i[2], font=("Helvetica", 12), width='15')
            b4.grid(row=tempresult.index(i) + 1, column=3)
            b3 = Button(self.master, text='remove', font=("Helvetica", 12), width='15',
                        command=partial(self.remove, i[0], i[1]))
            b3.grid(row=tempresult.index(i) + 1, column=4)

        self.back = Button(self.master, font=("Helvetica", 12), text="Back", fg="white", bg='black',
                           command=self.back).grid(row=20, column=0)
        self.log = Button(self.master, font=("Helvetica", 12), text="Logout", fg="white", bg='black',
                          command=self.logout).grid(row=20, column=1)

    def remove(self, date1, time):
        msg = tkinter.messagebox.askyesno('Remove', 'Are you sure you want remove this booking?')
        if msg:
            td_hour = datetime.today().hour - 12
            td_day = date.today().day
            td_month = date.today().month
            td_year = date.today().year
            new_time = int(time[:-2])
            temp_date = date1.split()
            new_date = int(temp_date[1][:2])
            if td_year > 2019 or \
                    td_year == 2019 and td_month > 1 or \
                    td_year == 2019 and td_month == 1 and td_day > new_date or \
                    td_year == 2019 and td_month == 1 and td_day == new_date and td_hour >= new_time:
                tkinter.messagebox.showinfo("---- ERROR ----", "Date and time of showing has passed!", icon="warning")
            else:
                with conn3:
                    c3.execute('''DELETE FROM bookings WHERE
                                username = ? AND date = ? AND time = ?''',
                               (username, date1, time))
                c2.execute('''SELECT booked FROM movies WHERE
                date = ? AND time = ?''', (date1, time))
                tempgone = c2.fetchone()
                with conn2:
                    c2.execute('''UPDATE movies SET booked = ?, available = ? WHERE
                    date = ? AND time = ?''', (tempgone[0] - 1, 100 - (tempgone[0] - 1), date1, time))
                tkinter.messagebox.showinfo("---- REMOVED ----", "Film removed from booking history.", icon="info")
                self.newWindow = Toplevel(self.master)
                self.newWindow.geometry('1096x720')
                self.app = BookHist(self.newWindow)
                self.master.withdraw()


class Employee(Customer):
    '''Employee login page'''

    def __init__(self, master):
        super().__init__(master)

    def login(self):
        username2 = self.username.get()
        password2 = self.password.get()
        lines = iter([line.rstrip('\n') for line in open('employees.txt', 'r')])
        for i in lines:
            j = i.split(': ')
            if username2 == j[0] and password2 == j[1]:
                self.newWindow = Toplevel(self.master)
                self.newWindow.geometry('1096x720')
                self.app = EmployeeMain(self.newWindow)
                self.master.withdraw()
                tkinter.messagebox.showinfo("---- SUCCESS ----", "You Have Now Logged In.", icon="info")
                break
        else:
            tkinter.messagebox.showinfo("---- ERROR ----", "Incorrect login! Please try again", icon="warning")


class EmployeeMain(Employee):
    '''Employee main menu page. Allows user to add films and see films'''

    def __init__(self, master):
        self.master = master
        self.frame = Frame(self.master)
        self.label = Label(self.master, image=back_pic)
        self.label.place(x=0, y=0, relwidth=1, relheight=1)
        self.frame.pack()
        self.showings = Button(self.master, font=("Helvetica", 16), text="See list of film showings", bg="yellow",
                               command=self.See_list).pack(pady='5')
        self.add = Button(self.master, font=("Helvetica", 16), text="Add film showings", bg="yellow",
                          command=self.Add_film_showings).pack(pady='5')
        self.log = Button(self.master, font=("Helvetica", 12), text="Logout", fg="white", bg='black',
                          command=self.logout).pack(pady='5')

    def logout(self):
        msg = tkinter.messagebox.askyesno('Logout', 'Are you sure you want to log out?')
        if msg:
            self.newWindow = Toplevel(self.master)
            self.newWindow.geometry('1096x720')
            self.app = MainPage(self.newWindow)
            self.master.withdraw()

    def See_list(self):
        self.newWindow = Toplevel(self.master)
        self.newWindow.geometry('1096x720')
        self.app = Showings(self.newWindow)
        self.master.withdraw()

    def Add_film_showings(self):
        self.newWindow = Toplevel(self.master)
        self.newWindow.geometry('1096x720')
        self.app = AddShowings(self.newWindow)
        self.master.withdraw()


class Showings(EmployeeMain):
    '''Shows a list of times and dates that have a film showing. The dates range from Monday 14th - Friday 20th
    January 2019, and times range from 1-11pm (with the last showing at 10pm). The shows are for exactly
    one hour'''

    def __init__(self, master):
        self.master = master
        self.frame = Frame(self.master)
        self.label = Label(self.master, image=back_pic)
        self.label.place(x=0, y=0, relwidth=1, relheight=1)
        self.frame.grid(row=0, column=0)
        self.date = Label(self.master, text='Date', font=("Helvetica", 16), width=8).grid(row=0, column=1, pady='1')
        self.time = Label(self.master, text='Time', font=("Helvetica", 16), width=6).grid(row=0, column=2, pady='1')
        self.title = Label(self.master, text='Title', font=("Helvetica", 16), width=18).grid(row=0, column=3, pady='1')
        self.description = Label(self.master, text='Description', font=("Helvetica", 16), width=32).grid(row=0,
                                                                                                         column=4,
                                                                                                         pady='1')
        self.booked = Label(self.master, text='Booked', font=("Helvetica", 16), width=8).grid(row=0, column=5, pady='1')
        self.available = Label(self.master, text='Available', font=("Helvetica", 16), width=8).grid(row=0, column=6,
                                                                                                    pady='1')
        self.seeseats = Label(self.master, text='Seating', font=("Helvetica", 16), width=8).grid(row=0, column=7,
                                                                                                 pady='1')
        c2.execute('''SELECT * FROM movies ORDER BY date='Monday 14/01/19' DESC,
                                                    date='Tuesday 15/01/19' DESC,
                                                    date='Wednesday 16/01/19' DESC,
                                                    date='Thursday 17/01/19' DESC,
                                                    date='Friday 18/01/19' DESC,
                                                    date='Saturday 19/01/19' DESC,
                                                    date='Sunday 20/01/19' DESC,
                                                    time='1pm' DESC,
                                                    time='2pm' DESC,
                                                    time='3pm' DESC,
                                                    time='4pm' DESC,
                                                    time='5pm' DESC,
                                                    time='6pm' DESC,
                                                    time='7pm' DESC,
                                                    time='8pm' DESC,
                                                    time='9pm' DESC,
                                                    time='10pm' DESC''')
        output = c2.fetchall()
        widths = (15, 6, 40, 60, 8, 8, 12)
        for i in output:
            for j in i:
                b = Label(self.master, text=j, font=("Helvetica", 6), width=widths[i.index(j)])
                b.grid(row=output.index(i) + 1, column=i.index(j) + 1, pady='1')
            # c2.execute('SELECT booked FROM movies WHERE rowid=?', (output.index(i)+1,))
            self.taken = i[4]
            # self.taken = c2.fetchone()[0]  # returns the number of available seats for that movie
            d = Button(self.master, text='See seats', command=partial(self.seats, self.taken), font=("Helvetica", 7),
                       width=8)
            # Using partial here allows a function to be called in a button with a parameter without the
            # function being called automatically
            d.grid(row=output.index(i) + 1, column=7, pady='1')
        self.exp = Button(self.master, font=("Helvetica", 12), text="Export films to text file", bg="yellow",
                          command=self.export).grid(row=35, column=3, pady='1')
        self.back = Button(self.master, font=("Helvetica", 12), text="Back", bg="black", fg="white",
                           command=self.back).grid(row=35, column=1, pady='1')
        self.log = Button(self.master, font=("Helvetica", 12), text="Logout", bg="black", fg="white",
                          command=self.logout).grid(row=35, column=2, pady='1')
        # self.canvas = Canvas(self.master, borderwidth=0, background="#ffffff")
        # scrollbar = Scrollbar(self.master, orient='vertical', command=self.canvas.yview)
        # scrollbar.grid(row=0, column=100, rowspan=30, sticky='NSW')

    def export(self):
        try:
            file = open('export.txt', 'w')
            print('Below is a list of dates and times with a film showing. The comma separated lines below'
                  ' are of the order: date, time, title, number of booked seats, number of available seats.', file=file)
            c2.execute('''SELECT * FROM movies ORDER BY date='Monday 14/01/19' DESC,
                                                    date='Tuesday 15/01/19' DESC,
                                                    date='Wednesday 16/01/19' DESC,
                                                    date='Thursday 17/01/19' DESC,
                                                    date='Friday 18/01/19' DESC,
                                                    date='Saturday 19/01/19' DESC,
                                                    date='Sunday 20/01/19' DESC,
                                                    time='1pm' DESC,
                                                    time='2pm' DESC,
                                                    time='3pm' DESC,
                                                    time='4pm' DESC,
                                                    time='5pm' DESC,
                                                    time='6pm' DESC,
                                                    time='7pm' DESC,
                                                    time='8pm' DESC,
                                                    time='9pm' DESC,
                                                    time='10pm' DESC''')
            every = c2.fetchall()
            for i in every:
                print(f'{i[0]}, {i[1]}, {i[2]}, {i[4]}, {i[5]}', file=file)
            tkinter.messagebox.showinfo("---- SUCCESSFUL ----", "Films successfully exported.",
                                        icon="info")
        except:
            tkinter.messagebox.showinfo("---- ERROR ----", "There was an error in exporting this file.",
                                        icon="warning")

    def back(self):
        self.newWindow = Toplevel(self.master)
        self.newWindow.geometry('1096x720')
        self.app = EmployeeMain(self.newWindow)
        self.master.withdraw()

    def seats(self, seatstaken):
        self.newWindow = Toplevel(self.master)
        self.newWindow.geometry('1096x720')
        self.app = SeeSeatsEmp(self.newWindow, seatstaken)
        self.master.withdraw()


class AddShowings(Showings):
    def __init__(self, master):
        self.master = master
        self.frame = Frame(self.master)
        self.label = Label(self.master, image=back_pic)
        self.label.place(x=0, y=0, relwidth=1, relheight=1)
        self.frame.grid(row=0, column=0)

        self.title = Label(self.master, text="Please add a new showing below",
                           font=("Helvetica", 16), width=45).grid(row=0, column=0, pady='5', columnspan=2)

        self.date = Label(self.master, text="Date:", width=15).grid(row=1, column=0, pady='3')
        self.defdate = StringVar(self.master)
        self.defdate.set("Monday 14/01/19")  # default value
        self.datelist = OptionMenu(master, self.defdate, "Monday 14/01/19", "Tuesday 15/01/19", "Wednesday 16/01/19",
                                   "Thursday 17/01/19", "Friday 18/01/19", "Saturday 19/01/19", "Sunday 20/01/19")
        # self.datelist.config(width=30)
        self.datelist.grid(row=1, column=1, pady='3')

        self.time = Label(self.master, text="Time:", width=15).grid(row=2, column=0, pady='3')
        self.deftime = StringVar(self.master)
        self.deftime.set("1pm")  # default value
        self.timelist = OptionMenu(master, self.deftime, "1pm", "2pm", "3pm", "4pm", "5pm", "6pm", "7pm", "8pm",
                                   "9pm", "10pm")
        # self.timelist.config(width=30)
        self.timelist.grid(row=2, column=1, pady='3')

        self.titl = Label(self.master, text="Title:", width=15).grid(row=3, column=0, pady='3')
        self.title = Entry(self.master, width='45')
        self.title.grid(row=3, column=1, pady='3')

        self.des = Label(self.master, text="Description:", width=15).grid(row=4, column=0, pady='3')
        self.description = Entry(self.master, width='45')
        self.description.grid(row=4, column=1, columnspan=4, pady='3')

        self.addfilm = Button(self.master, text="Add Film Showing", command=self.addnew).grid(row=5, columnspan=5,
                                                                                              pady='3')

        self.back = Button(self.master, font=("Helvetica", 12), text="Back", fg="white", bg='black',
                           command=self.back).grid(row=11, column=0, pady='3')
        self.log = Button(self.master, font=("Helvetica", 12), text="Logout", fg="white", bg='black',
                          command=self.logout).grid(row=11, column=1, pady='3')

    def addnew(self):
        msg = tkinter.messagebox.askyesno('Logout', 'Confirm new showing?')
        if msg:
            new_date = self.defdate.get()
            new_time = self.deftime.get()
            new_title = self.title.get()
            new_description = self.description.get()
            c2.execute("""SELECT * FROM movies WHERE
                        date = ? AND time = ?""", (new_date, new_time))
            if not new_date or not new_time or not new_title or not new_description:
                tkinter.messagebox.showinfo("---- ERROR ----", "Please complete all required fields.",
                                            icon="warning")
            else:
                if not c2.fetchall():
                    with conn2:
                        c2.execute("""INSERT INTO movies VALUES (?, ?, ?, ?, ?, ?)""", (
                            new_date, new_time, new_title, new_description, 0, 100))
                        tkinter.messagebox.showinfo("---- SUCCESSFUL ----",
                                                    "Showing successfully added to list of showings!",
                                                    icon="info")
                else:
                    tkinter.messagebox.showinfo("---- ERROR ----", "There is already a showing at this time!",
                                                icon="warning")


class SeeSeatsEmp(Showings):
    def __init__(self, master, booked):
        self.booked = booked  # booked is the same as taken from above
        self.master = master
        self.frame = Frame(self.master)
        self.label = Label(self.master, image=back_pic)
        self.label.place(x=0, y=0, relwidth=1, relheight=1)
        self.frame.grid(row=0, column=0)
        self.title = Label(self.master, text='Seat layout:    green = available,'
                                             ' red = unavailable', font=("Helvetica", 16)).grid(row=0, columnspan=94)
        tens = self.booked // 10
        rem = self.booked % 10
        for i in range(tens):
            for j in range(5):
                b = Button(self.master, bg="red", height=2, width=5)
                b.grid(row=i + 1, column=j)
            for j in range(5):
                b = Button(self.master, bg="red", height=2, width=5)
                b.grid(row=i + 1, column=j + 80)
        if tens != 10:
            if rem == 0:
                for j in range(5):
                    b = Button(self.master, bg="green", height=2, width=5)
                    b.grid(row=tens + 1, column=j)
                for j in range(5):
                    b = Button(self.master, bg="green", height=2, width=5)
                    b.grid(row=tens + 1, column=j + 80)
            elif rem <= 5:
                for j in range(rem):
                    b = Button(self.master, bg="red", height=2, width=5)
                    b.grid(row=tens + 1, column=j)
                for j in range(5 - rem):
                    b = Button(self.master, bg="green", height=2, width=5)
                    b.grid(row=tens + 1, column=rem + j)
                for j in range(5):
                    b = Button(self.master, bg="green", height=2, width=5)
                    b.grid(row=tens + 1, column=j + 80)
            else:
                for j in range(5):
                    b = Button(self.master, bg="red", height=2, width=5)
                    b.grid(row=tens + 1, column=j)
                for j in range(rem - 5):
                    b = Button(self.master, bg="red", height=2, width=5)
                    b.grid(row=tens + 1, column=j + 80)
                for j in range(10 - rem):
                    b = Button(self.master, bg="green", height=2, width=5)
                    b.grid(row=tens + 1, column=j + 80 + rem - 5)

        if tens != 10:
            for i in range(10 - tens - 1):
                for j in range(5):
                    b = Button(self.master, bg="green", height=2, width=5)
                    b.grid(row=tens + 2 + i, column=j)
                for j in range(5):
                    b = Button(self.master, bg="green", height=2, width=5)
                    b.grid(row=tens + 2 + i, column=j + 80)

        self.back = Button(self.master, text="Back", font=("Helvetica", 12), fg="white", bg='black',
                           command=self.See_list).grid(row=11, column=3, columnspan=90)
        self.log = Button(self.master, font=("Helvetica", 12), text="Logout", fg="white", bg='black',
                          command=self.logout).grid(row=11, columnspan=2)


def Customer_Database_Initialiser():
    '''Initialises the database for customers'''
    global conn
    conn = sqlite3.connect('customer.db')
    global c
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS customers(
                first text,
                last text,
                email text,
                age integer,
                username text,
                password text
                )''')

    def create():
        cust = iter([line.rstrip('\n') for line in open('customers.txt', 'r')])
        for i in cust:
            j = i.split(': ')
            k = j[0].split('_')
            c.execute('INSERT INTO customers VALUES (?, ?, ?, ?, ?, ?)',
                      (k[0], k[1], str(j[0] + '@simpsons.com'), randrange(10, 60), j[0], j[1]))

    # create() # Uncomment this line if you want to create the databases again from scratch
    conn.commit()


def Films_Database_Initialiser():
    '''Initialises the database for the film showings'''
    global conn2
    conn2 = sqlite3.connect('movies.db')
    global c2
    c2 = conn2.cursor()
    c2.execute('''CREATE TABLE IF NOT EXISTS movies(
                date text,
                time text,
                title text,
                description text,
                booked integer,
                available integer
                )''')

    def create():
        mov = iter([line.rstrip('\n') for line in open('MOVIES.txt', 'r')])
        for i in mov:
            j = i.split(': ')
            c2.execute('INSERT INTO movies VALUES (?, ?, ?, ?, ?, ?)', (j[0], j[1], j[4], j[5], j[2], j[3]))

    # create() # Uncomment this line if you want to create the databases again from scratch
    conn2.commit()


def Bookings_Database_Initialiser():
    '''Initlaises the database for film bookings'''
    global conn3
    conn3 = sqlite3.connect('bookings.db')
    global c3
    c3 = conn3.cursor()
    c3.execute('''CREATE TABLE IF NOT EXISTS bookings(
                    first text,
                    last text,
                    date text,
                    time text,
                    seatno text,
                    username text
                    )''')
    conn3.commit()


def main():
    window = Tk()
    window.title("Sanders Cinemas")
    window.geometry('1096x720')
    image = Image.open("Background.png")
    image = image.resize((1096, 720))
    Customer_Database_Initialiser()
    Films_Database_Initialiser()
    Bookings_Database_Initialiser()
    global back_pic
    back_pic = ImageTk.PhotoImage(image)
    label = Label(window, image=back_pic)
    label.place(x=0, y=0, relwidth=1, relheight=1)
    app = MainPage(window)
    window.mainloop()


if __name__ == '__main__':
    main()
