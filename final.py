import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog
import pyodbc

# 连接数据库
conn = pyodbc.connect('DRIVER={SQL Server};SERVER=localhost;DATABASE=dy;UID=1;PWD=1')
cursor = conn.cursor()


# 创建主窗口
root = tk.Tk()
root.title("电影票售卖系统")
root.geometry("400x300")


def register(username, password):
    cursor.execute('SELECT * FROM users WHERE username=?', (username,))
    existing_user = cursor.fetchone()
    if existing_user:
        messagebox.showerror("注册失败", "该用户名已被注册！")
    else:
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        messagebox.showinfo("注册成功", "注册成功！")


def login(username, password):
    if username == 'admin':
        admin_login()
    else:
        cursor.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
        user = cursor.fetchone()
        if user:
            messagebox.showinfo("登录成功", "登录成功！")
            show_movies()
        else:
            messagebox.showerror("登录失败", "用户名或密码错误！")


def get_current_movies():
    cursor.execute('SELECT movie_id, movie_name, movie_type, movie_nation FROM movie')
    return cursor.fetchall()


def show_movies():
    movies = get_current_movies()
    if movies:
        movie_info = "现在正在上映的电影：\n"
        for movie in movies:
            movie_id, movie_name, movie_type, movie_nation = movie
            movie_info += f"电影ID：{movie_id}，名称：{movie_name}，类型：{movie_type}，国家：{movie_nation}\n"
        messagebox.showinfo("当前电影信息", movie_info)
        purchase_tickets(movies)
    else:
        messagebox.showinfo("当前电影信息", "当前没有正在上映的电影。")


def purchase_tickets(movies):
    movie_selection_window = tk.Toplevel(root)
    movie_selection_window.title("选择电影")

    def on_movie_selected(movie_id):
        show_schedule(movie_id)

    for movie in movies:
        movie_id, movie_name, _, _ = movie
        movie_button = tk.Button(movie_selection_window, text=movie_name,
                                 command=lambda m=movie_id: on_movie_selected(m))
        movie_button.pack()


def get_movie_schedules(movie_id):
    cursor.execute('SELECT schedule_id, schedule_hall, movie_time FROM schedule WHERE movie_id=?', (movie_id,))
    return cursor.fetchall()


def show_schedule(movie_id):
    schedules = get_movie_schedules(movie_id)
    schedule_selection_window = tk.Toplevel(root)
    schedule_selection_window.title("选择排场")

    def on_schedule_selected(schedule_id, hall_id):
        show_seat_selection(schedule_id, hall_id)

    for schedule in schedules:
        schedule_id, hall_id, movie_time = schedule
        schedule_button = tk.Button(schedule_selection_window, text=f"时间：{movie_time}，影厅：{hall_id}",
                                    command=lambda s=schedule_id, h=hall_id: on_schedule_selected(s, h))
        schedule_button.pack()


def show_seat_selection(schedule_id, hall_id):
    seat_selection_window = tk.Toplevel(root)
    seat_selection_window.title("选择座位")

    def on_seat_selected(seat_id):
        purchase_ticket(schedule_id, seat_id)

    for row in range(1, 11):
        for column in range(1, 11):
            seat_id = f'{hall_id}{row:02d}{column:02d}'
            seat_button = tk.Button(seat_selection_window, text=seat_id, command=lambda s=seat_id: on_seat_selected(s))
            seat_button.grid(row=row, column=column, padx=2, pady=2)


def purchase_ticket(schedule_id, seat_id):
    cursor.execute('INSERT INTO orders (schedule_id, seat_id) VALUES (?, ?)', (schedule_id, seat_id))
    conn.commit()
    messagebox.showinfo("购票成功", "购票成功！")


def admin_login():
    admin_username = simpledialog.askstring("管理员登录", "请输入管理员用户名：")
    admin_password = simpledialog.askstring("管理员登录", "请输入管理员密码：", show='*')
    if admin_username and admin_password:
        cursor.execute('SELECT * FROM admin WHERE username=? AND password=?', (admin_username, admin_password))
        admin = cursor.fetchone()
        if admin:
            messagebox.showinfo("管理员登录成功", "管理员登录成功！")
            admin_menu()
        else:
            messagebox.showerror("管理员登录失败", "管理员用户名或密码错误！")


def admin_menu():
    admin_window = tk.Toplevel(root)
    admin_window.title("管理员界面")

    def add_movie():
        movie_name = simpledialog.askstring("添加电影", "请输入电影名称：")
        if movie_name:
            cursor.execute('INSERT INTO movie (movie_name) VALUES (?)', (movie_name,))
            conn.commit()
            messagebox.showinfo("添加成功", "电影添加成功！")

    def delete_movie():
        movie_id = simpledialog.askinteger("删除电影", "请输入要删除的电影ID：")
        if movie_id:
            cursor.execute('DELETE FROM movie WHERE movie_id=?', (movie_id,))
            conn.commit()
            messagebox.showinfo("删除成功", "电影删除成功！")

    def edit_movie():
        movie_id = simpledialog.askinteger("编辑电影", "请输入要编辑的电影ID：")
        movie_name = simpledialog.askstring("编辑电影", "请输入新的电影名称：")
        if movie_id and movie_name:
            cursor.execute('UPDATE movie SET movie_name=? WHERE movie_id=?', (movie_name, movie_id))
            conn.commit()
            messagebox.showinfo("编辑成功", "电影编辑成功！")

    def save_changes():
        conn.commit()
        messagebox.showinfo("保存成功", "更改已保存！")

    add_movie_button = tk.Button(admin_window, text="添加电影", command=add_movie)
    add_movie_button.pack()

    delete_movie_button = tk.Button(admin_window, text="删除电影", command=delete_movie)
    delete_movie_button.pack()

    edit_movie_button = tk.Button(admin_window, text="编辑电影", command=edit_movie)
    edit_movie_button.pack()

    save_changes_button = tk.Button(admin_window, text="保存更改", command=save_changes)
    save_changes_button.pack()


# 注册函数
def register_user():
    register_username = username_entry.get()
    register_password = password_entry.get()
    if register_username and register_password:
        register(register_username, register_password)
    else:
        messagebox.showerror("注册失败", "请输入用户名和密码！")


# 登录函数
def login_user():
    login_username = username_entry.get()
    login_password = password_entry.get()
    if login_username and login_password:
        login(login_username, login_password)
    else:
        messagebox.showerror("登录失败", "请输入用户名和密码！")


# 创建用户名标签和输入框
username_label = tk.Label(root, text="用户名：")
username_label.pack()
username_entry = tk.Entry(root)
username_entry.pack()

# 创建密码标签和输入框
password_label = tk.Label(root, text="密码：")
password_label.pack()
password_entry = tk.Entry(root, show="*")
password_entry.pack()

# 创建注册按钮
register_button = tk.Button(root, text="注册", command=register_user)
register_button.pack()

# 创建登录按钮
login_button = tk.Button(root, text="用户登录", command=login_user)
login_button.pack()

# 创建管理员登录按钮
admin_login_button = tk.Button(root, text="管理员登录", command=admin_login)
admin_login_button.pack()

# 运行主循环
root.mainloop()

# 关闭游标和连接
cursor.close()
conn.close()
