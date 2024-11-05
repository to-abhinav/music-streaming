import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from tkcalendar import Calendar
from datetime import date

# Database connection
conn = sqlite3.connect('employee_management.db')
cursor = conn.cursor()

# Creating necessary tables
cursor.execute('''CREATE TABLE IF NOT EXISTS employee (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    department TEXT NOT NULL,
                    designation TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    email TEXT,
                    salary REAL)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS attendance (
                    id INTEGER,
                    date TEXT NOT NULL,
                    status TEXT NOT NULL,
                    visiting_hour TEXT,
                    leaving_hour TEXT,
                    FOREIGN KEY(id) REFERENCES employee(id))''')

cursor.execute('''CREATE TABLE IF NOT EXISTS holidays (
                    date TEXT NOT NULL,
                    description TEXT NOT NULL)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    deadline TEXT,
                    status TEXT)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS leave_requests (
                    id INTEGER,
                    start_date TEXT NOT NULL,
                    end_date TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    status TEXT DEFAULT 'Pending',
                    FOREIGN KEY(id) REFERENCES employee(id))''')

conn.commit()

# Login Page Class
class LoginPage(tk.Tk):
    def init(self):
        super().init()

        self.title("Login Page")
        self.geometry("400x300")
        self.configure(bg="#f0f4f7")  # Set background color

        # Creating login form
        tk.Label(self, text="Login", font=("Arial", 20, "bold"), bg="#f0f4f7", fg="#333").pack(pady=20)

        tk.Label(self, text="Username", font=("Arial", 14), bg="#f0f4f7").pack()
        self.username_entry = tk.Entry(self, font=("Arial", 12), width=25)
        self.username_entry.pack(pady=5)

        tk.Label(self, text="Password", font=("Arial", 14), bg="#f0f4f7").pack()
        self.password_entry = tk.Entry(self, font=("Arial", 12), width=25, show="*")
        self.password_entry.pack(pady=5)

        tk.Button(self, text="Login", font=("Arial", 14, "bold"), bg="#007BFF", fg="white", command=self.login).pack(pady=20)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        # Dummy check for username and password
        if username == "admin" and password == "password":
            self.destroy()  # Close login page
            app = EmployeeManagementApp()  # Open employee management system
            app.mainloop()
        else:
            messagebox.showerror("Error", "Invalid Credentials")

# Main Employee Management App
class EmployeeManagementApp(tk.Tk):
    def init(self):
        super().init()

        self.title("Employee Management System")
        self.geometry("900x600")
        self.configure(bg="#f0f4f7")  # Set background color

        # Top Bar
        top_frame = tk.Frame(self, bg="#007BFF", height=50)
        top_frame.pack(fill=tk.X)
        tk.Label(top_frame, text="Employee Management Dashboard", font=("Arial", 18, "bold"), bg="#007BFF", fg="white").pack(pady=10)

        # Side Navigation
        self.create_navigation()

        # Placeholder for Main Content Area
        self.main_content = tk.Frame(self, bg="white", width=700, height=500)
        self.main_content.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Load Employee Dashboard by default
        self.load_employee_dashboard()

    def create_navigation(self):
        nav_frame = tk.Frame(self, bg="#333333", width=200, height=600)
        nav_frame.pack(side=tk.LEFT, fill=tk.Y)

        add_emp_button = tk.Button(nav_frame, text="Add Employee", command=self.load_add_employee,
                                   font=("Arial", 12, "bold"), bg="#444444", fg="white", bd=0, padx=20, pady=10)
        add_emp_button.pack(fill=tk.X)

        display_emp_button = tk.Button(nav_frame, text="Employee Details", command=self.load_employee_dashboard,
                                       font=("Arial", 12, "bold"), bg="#444444", fg="white", bd=0, padx=20, pady=10)
        display_emp_button.pack(fill=tk.X)

        attendance_button = tk.Button(nav_frame, text="Attendance", command=self.load_attendance_page,
                                      font=("Arial", 12, "bold"), bg="#444444", fg="white", bd=0, padx=20, pady=10)
        attendance_button.pack(fill=tk.X)

        leave_management_button = tk.Button(nav_frame, text="Leave Management", command=self.load_leave_management,
                                             font=("Arial", 12, "bold"), bg="#444444", fg="white", bd=0, padx=20, pady=10)
        leave_management_button.pack(fill=tk.X)

        holidays_button = tk.Button(nav_frame, text="Holidays Calendar", command=self.load_holidays_calendar,
                                     font=("Arial", 12, "bold"), bg="#444444", fg="white", bd=0, padx=20, pady=10)
        holidays_button.pack(fill=tk.X)

        notifications_button = tk.Button(nav_frame, text="Notifications", command=self.load_notifications,
                                          font=("Arial", 12, "bold"), bg="#444444", fg="white", bd=0, padx=20, pady=10)
        notifications_button.pack(fill=tk.X)

    # Employee Dashboard
    def load_employee_dashboard(self):
        self.clear_main_content()
        tk.Label(self.main_content, text="Employee Dashboard", font=("Arial", 20, "bold"), bg="white").pack(pady=20)

        # Create table for employee details
        self.tree = ttk.Treeview(self.main_content, columns=("ID", "Name", "Department", "Designation", "Phone", "Email", "Salary"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="NAME")
        self.tree.heading("Department", text="DEPARTMENT")
        self.tree.heading("Designation", text="DESIGNATION")
        self.tree.heading("Phone", text="PHONE")
        self.tree.heading("Email", text="EMAIL")
        self.tree.heading("Salary", text="SALARY")
        self.tree.pack(pady=20)

        # Load employees
        self.load_employees()

        # Add Update and Delete buttons
        tk.Button(self.main_content, text="Update Employee", command=self.update_employee, bg="#FFC107", font=("Arial", 12)).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(self.main_content, text="Delete Employee", command=self.delete_employee, bg="#DC3545", font=("Arial", 12)).pack(side=tk.LEFT, padx=5, pady=5)

    def load_employees(self):
        # Clear current items in the treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        cursor.execute("SELECT * FROM employee")
        employees = cursor.fetchall()
        for emp in employees:
            self.tree.insert("", tk.END, values=emp)

    # Add Employee Form
    def load_add_employee(self):
        self.clear_main_content()

        tk.Label(self.main_content, text="Add New Employee", font=("Arial", 20, "bold"), bg="white").pack(pady=20)

        tk.Label(self.main_content, text="Name", font=("Arial", 14, "bold"), bg="white").pack(anchor=tk.W, padx=50)
        self.name_entry = tk.Entry(self.main_content, font=("Arial", 14))
        self.name_entry.pack(padx=50, pady=5)

        tk.Label(self.main_content, text="Department", font=("Arial", 14, "bold"), bg="white").pack(anchor=tk.W, padx=50)
        self.department_entry = tk.Entry(self.main_content, font=("Arial", 14))
        self.department_entry.pack(padx=50, pady=5)

        tk.Label(self.main_content, text="Designation", font=("Arial", 14, "bold"), bg="white").pack(anchor=tk.W, padx=50)
        self.designation_entry = tk.Entry(self.main_content, font=("Arial", 14))
        self.designation_entry.pack(padx=50, pady=5)

        tk.Label(self.main_content, text="Phone", font=("Arial", 14, "bold"), bg="white").pack(anchor=tk.W, padx=50)
        self.phone_entry = tk.Entry(self.main_content, font=("Arial", 14))
        self.phone_entry.pack(padx=50, pady=5)

        tk.Label(self.main_content, text="Email", font=("Arial", 14, "bold"), bg="white").pack(anchor=tk.W, padx=50)
        self.email_entry = tk.Entry(self.main_content, font=("Arial", 14))
        self.email_entry.pack(padx=50, pady=5)

        tk.Label(self.main_content, text="Salary", font=("Arial", 14, "bold"), bg="white").pack(anchor=tk.W, padx=50)
        self.salary_entry = tk.Entry(self.main_content, font=("Arial", 14))
        self.salary_entry.pack(padx=50, pady=5)

        tk.Button(self.main_content, text="Add Employee", font=("Arial", 14, "bold"), bg="#28A745", fg="white",
                  command=self.save_employee).pack(pady=20)

    def save_employee(self):
        name = self.name_entry.get()
        department = self.department_entry.get()
        designation = self.designation_entry.get()
        phone = self.phone_entry.get()
        email = self.email_entry.get()
        salary = self.salary_entry.get()

        cursor.execute("INSERT INTO employee (name, department, designation, phone, email, salary) VALUES (?, ?, ?, ?, ?, ?)",
                       (name, department, designation, phone, email, salary))
        conn.commit()

        messagebox.showinfo("Success", "Employee Added Successfully")
        self.load_employee_dashboard()

    # Update Employee
    def update_employee(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Select Employee", "Please select an employee to update.")
            return

        emp_id = self.tree.item(selected_item)['values'][0]
        self.clear_main_content()

        tk.Label(self.main_content, text="Update Employee", font=("Arial", 20, "bold"), bg="white").pack(pady=20)

        tk.Label(self.main_content, text="ID", font=("Arial", 14), bg="white").pack(anchor=tk.W, padx=50)
        tk.Label(self.main_content, text=emp_id, font=("Arial", 14), bg="white").pack(anchor=tk.W, padx=50)

        tk.Label(self.main_content, text="Name", font=("Arial", 14, "bold"), bg="white").pack(anchor=tk.W, padx=50)
        self.name_entry = tk.Entry(self.main_content, font=("Arial", 14))
        self.name_entry.pack(padx=50, pady=5)

        tk.Label(self.main_content, text="Department", font=("Arial", 14, "bold"), bg="white").pack(anchor=tk.W, padx=50)
        self.department_entry = tk.Entry(self.main_content, font=("Arial", 14))
        self.department_entry.pack(padx=50, pady=5)

        tk.Label(self.main_content, text="Designation", font=("Arial", 14, "bold"), bg="white").pack(anchor=tk.W, padx=50)
        self.designation_entry = tk.Entry(self.main_content, font=("Arial", 14))
        self.designation_entry.pack(padx=50, pady=5)

        tk.Label(self.main_content, text="Phone", font=("Arial", 14, "bold"), bg="white").pack(anchor=tk.W, padx=50)
        self.phone_entry = tk.Entry(self.main_content, font=("Arial", 14))
        self.phone_entry.pack(padx=50, pady=5)

        tk.Label(self.main_content, text="Email", font=("Arial", 14, "bold"), bg="white").pack(anchor=tk.W, padx=50)
        self.email_entry = tk.Entry(self.main_content, font=("Arial", 14))
        self.email_entry.pack(padx=50, pady=5)

        tk.Label(self.main_content, text="Salary", font=("Arial", 14, "bold"), bg="white").pack(anchor=tk.W, padx=50)
        self.salary_entry = tk.Entry(self.main_content, font=("Arial", 14))
        self.salary_entry.pack(padx=50, pady=5)

        # Load current data into entries
        cursor.execute("SELECT * FROM employee WHERE id=?", (emp_id,))
        employee = cursor.fetchone()
        self.name_entry.insert(0, employee[1])
        self.department_entry.insert(0, employee[2])
        self.designation_entry.insert(0, employee[3])
        self.phone_entry.insert(0, employee[4])
        self.email_entry.insert(0, employee[5])
        self.salary_entry.insert(0, employee[6])

        tk.Button(self.main_content, text="Update Employee", font=("Arial", 14, "bold"), bg="#28A745", fg="white",
                  command=lambda: self.execute_update(emp_id)).pack(pady=20)

    def execute_update(self, emp_id):
        name = self.name_entry.get()
        department = self.department_entry.get()
        designation = self.designation_entry.get()
        phone = self.phone_entry.get()
        email = self.email_entry.get()
        salary = self.salary_entry.get()

        cursor.execute("UPDATE employee SET name=?, department=?, designation=?, phone=?, email=?, salary=? WHERE id=?",
                       (name, department, designation, phone, email, salary, emp_id))
        conn.commit()

        messagebox.showinfo("Success", "Employee Updated Successfully")
        self.load_employee_dashboard()

    def delete_employee(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Select Employee", "Please select an employee to delete.")
            return

        emp_id = self.tree.item(selected_item)['values'][0]
        cursor.execute("DELETE FROM employee WHERE id=?", (emp_id,))
        conn.commit()

        messagebox.showinfo("Success", "Employee Deleted Successfully")
        self.load_employee_dashboard()

    # Attendance Page
    def load_attendance_page(self):
        self.clear_main_content()
        tk.Label(self.main_content, text="Attendance", font=("Arial", 20, "bold"), bg="white").pack(pady=20)

        tk.Label(self.main_content, text="Employee ID", font=("Arial", 14, "bold"), bg="white").pack(anchor=tk.W, padx=50)
        emp_id_entry = tk.Entry(self.main_content, font=("Arial", 14))
        emp_id_entry.pack(padx=50, pady=5)

        tk.Label(self.main_content, text="Status (Present/Absent)", font=("Arial", 14, "bold"), bg="white").pack(anchor=tk.W, padx=50)
        status_entry = tk.Entry(self.main_content, font=("Arial", 14))
        status_entry.pack(padx=50, pady=5)

        tk.Label(self.main_content, text="Visiting Hour (HH:MM)", font=("Arial", 14, "bold"), bg="white").pack(anchor=tk.W, padx=50)
        visiting_entry = tk.Entry(self.main_content, font=("Arial", 14))
        visiting_entry.pack(padx=50, pady=5)

        tk.Label(self.main_content, text="Leaving Hour (HH:MM)", font=("Arial", 14, "bold"), bg="white").pack(anchor=tk.W, padx=50)
        leaving_entry = tk.Entry(self.main_content, font=("Arial", 14))
        leaving_entry.pack(padx=50, pady=5)

        # Button to mark attendance
        tk.Button(self.main_content, text="Mark Attendance", font=("Arial", 14, "bold"), bg="#28A745", fg="white",
                  command=lambda: self.save_attendance(emp_id_entry, status_entry, visiting_entry, leaving_entry)).pack(pady=20)

        # Attendance Table
        self.attendance_tree = ttk.Treeview(self.main_content, columns=("ID", "Date", "Status", "Visiting Hour", "Leaving Hour"), show="headings")
        self.attendance_tree.heading("ID", text="ID")
        self.attendance_tree.heading("Date", text="Date")
        self.attendance_tree.heading("Status", text="Status")
        self.attendance_tree.heading("Visiting Hour", text="Visiting Hour")
        self.attendance_tree.heading("Leaving Hour", text="Leaving Hour")
        self.attendance_tree.pack(pady=20)

        self.load_attendance()

    def save_attendance(self, emp_id_entry, status_entry, visiting_entry, leaving_entry):
        emp_id = emp_id_entry.get()
        status = status_entry.get()
        visiting_hour = visiting_entry.get()
        leaving_hour = leaving_entry.get()
        today = date.today().strftime("%Y-%m-%d")

        cursor.execute("INSERT INTO attendance (id, date, status, visiting_hour, leaving_hour) VALUES (?, ?, ?, ?, ?)",
                       (emp_id, today, status, visiting_hour, leaving_hour))
        conn.commit()

        messagebox.showinfo("Success", "Attendance Marked Successfully")
        self.load_attendance()

    def load_attendance(self):
        for item in self.attendance_tree.get_children():
            self.attendance_tree.delete(item)

        cursor.execute("SELECT * FROM attendance")
        attendance_records = cursor.fetchall()
        for record in attendance_records:
            self.attendance_tree.insert("", tk.END, values=record)

    # Leave Management Page
    def load_leave_management(self):
        self.clear_main_content()
        tk.Label(self.main_content, text="Leave Management", font=("Arial", 20, "bold"), bg="white").pack(pady=20)

        tk.Label(self.main_content, text="Employee ID", font=("Arial", 14, "bold"), bg="white").pack(anchor=tk.W, padx=50)
        emp_id_entry = tk.Entry(self.main_content, font=("Arial", 14))
        emp_id_entry.pack(padx=50, pady=5)

        tk.Label(self.main_content, text="Leave Start Date", font=("Arial", 14, "bold"), bg="white").pack(anchor=tk.W, padx=50)
        start_date_entry = Calendar(self.main_content)
        start_date_entry.pack(padx=50, pady=5)

        tk.Label(self.main_content, text="Leave End Date", font=("Arial", 14, "bold"), bg="white").pack(anchor=tk.W, padx=50)
        end_date_entry = Calendar(self.main_content)
        end_date_entry.pack(padx=50, pady=5)

        tk.Label(self.main_content, text="Reason", font=("Arial", 14, "bold"), bg="white").pack(anchor=tk.W, padx=50)
        reason_entry = tk.Entry(self.main_content, font=("Arial", 14))
        reason_entry.pack(padx=50, pady=5)

        tk.Button(self.main_content, text="Submit Leave Request", font=("Arial", 14, "bold"), bg="#28A745", fg="white",
                  command=lambda: self.save_leave_request(emp_id_entry, start_date_entry, end_date_entry, reason_entry)).pack(pady=20)

        # Leave Requests Table
        self.leave_tree = ttk.Treeview(self.main_content, columns=("ID", "Start Date", "End Date", "Reason", "Status"), show="headings")
        self.leave_tree.heading("ID", text="ID")
        self.leave_tree.heading("Start Date", text="Start Date")
        self.leave_tree.heading("End Date", text="End Date")
        self.leave_tree.heading("Reason", text="Reason")
        self.leave_tree.heading("Status", text="Status")
        self.leave_tree.pack(pady=20)

        self.load_leave_requests()

    def save_leave_request(self, emp_id_entry, start_date_entry, end_date_entry, reason_entry):
        emp_id = emp_id_entry.get()
        start_date = start_date_entry.get_date()
        end_date = end_date_entry.get_date()
        reason = reason_entry.get()

        cursor.execute("INSERT INTO leave_requests (id, start_date, end_date, reason) VALUES (?, ?, ?, ?)",
                       (emp_id, start_date, end_date, reason))
        conn.commit()

        messagebox.showinfo("Success", "Leave Request Submitted Successfully")
        self.load_leave_requests()

    def load_leave_requests(self):
        for item in self.leave_tree.get_children():
            self.leave_tree.delete(item)

        cursor.execute("SELECT * FROM leave_requests")
        leave_requests = cursor.fetchall()
        for request in leave_requests:
            self.leave_tree.insert("", tk.END, values=request)

    # Holidays Calendar
    def load_holidays_calendar(self):
        self.clear_main_content()
        tk.Label(self.main_content, text="Holidays Calendar", font=("Arial", 20, "bold"), bg="white").pack(pady=20)

        tk.Label(self.main_content, text="Date", font=("Arial", 14, "bold"), bg="white").pack(anchor=tk.W, padx=50)
        holiday_date_entry = Calendar(self.main_content)
        holiday_date_entry.pack(padx=50, pady=5)

        tk.Label(self.main_content, text="Description", font=("Arial", 14, "bold"), bg="white").pack(anchor=tk.W, padx=50)
        description_entry = tk.Entry(self.main_content, font=("Arial", 14))