import tkinter as tk
import datetime
import json
import os

# Create the main window
root = tk.Tk()
root.title("Milestone Monitor")
root.configure(bg="#d8f3dc")
root.geometry("1900x500")

# Error-handled icon loading
try:
    icon_path = os.path.abspath("images/cgev.ico")
    if os.path.exists(icon_path):
        root.iconbitmap(icon_path)
    else:
        print("Icon file not found, using default icon")
except Exception as e:
    print(f"Couldn't load icon: {e}")

# Get today's date
today = datetime.date.today()
day_of_year = today.timetuple().tm_yday

# Progress stages colors
progress_stages = ["#b7efc5", "#6ede8a", "#25a244", "#1a7431", "#04471c"]
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
buttons = []
tasks = {}

# Task management widgets
task_entry = tk.Entry(root, font=("Helvetica", 12))
submit_task_button = tk.Button(root, text="Add Task", command=lambda: add_task(), bg="#f07167")
tasks_display = tk.Text(root, height=6, width=100, state="disabled", wrap=tk.WORD)

# Layout adjustments
task_entry.grid(row=12, column=0, columnspan=40, padx=5, pady=5, sticky="ew")
submit_task_button.grid(row=12, column=40, padx=5, pady=5)
tasks_display.grid(row=13, column=0, columnspan=50, padx=10, pady=10, sticky="nsew")

def create_row(week):
    for i in range(0, 12):
        month = tk.Label(root, text=months[i], font=("Helvetica", 10), bg="#d8f3dc")
        month.grid(row=0, column=(1+i)*4, padx=2, pady=2)

    for i in range(1, 8):
        btn = tk.Button(root, bg="#ffffff", width=1, height=0)
        btn.bind("<Button-1>", change_button_color)
        btn.grid(row=i, column=week, padx=6, pady=2)
        buttons.append(btn)

def change_button_color(event):
    button = event.widget
    bg_color = button.cget("background")
    
    for index, color in enumerate(progress_stages):
        if bg_color == color and index < len(progress_stages)-1:
            button.configure(bg=progress_stages[index+1])
            break
        elif bg_color not in progress_stages:
            button.configure(bg=progress_stages[0])

def save_data():
    data = {
        "colors": [btn.cget("background") for btn in buttons],
        "tasks": tasks
    }
    with open("app_data.json", "w") as f:
        json.dump(data, f)
    root.destroy()

def load_data():
    try:
        if os.path.exists("app_data.json"):
            with open("app_data.json", "r") as f:
                data = json.load(f)
                return data.get("colors", []), data.get("tasks", {})
    except Exception as e:
        print(f"Error loading data: {e}")
    return [], {}

def process_overdue_tasks():
    current_day = day_of_year
    for day in list(tasks.keys()):
        try:
            day_int = int(day)
            if day_int < current_day:
                btn_idx = day_int - 1
                if btn_idx < len(buttons) and buttons[btn_idx].cget("background") != progress_stages[-1]:
                    tasks.setdefault(str(current_day), []).extend(tasks[day])
                    del tasks[day]
        except ValueError:
            continue

def add_task():
    task_text = task_entry.get().strip()
    if task_text:
        current_day_str = str(day_of_year)
        tasks.setdefault(current_day_str, []).append(task_text)
        task_entry.delete(0, tk.END)
        update_tasks_display()

def update_tasks_display():
    tasks_display.config(state="normal")
    tasks_display.delete(1.0, tk.END)
    current_tasks = tasks.get(str(day_of_year), [])
    for task in current_tasks:
        tasks_display.insert(tk.END, f"• {task}\n")
    tasks_display.config(state="disabled")

edit_mode = False

def toggle_edit_mode():
    global edit_mode
    edit_mode = not edit_mode
    
    for idx, btn in enumerate(buttons):
        if idx == day_of_year - 1:
            btn.config(state="normal")
            btn.bind("<Button-1>", change_button_color)
        else:
            btn.config(state="disabled" if edit_mode else "normal")
            btn.unbind("<Button-1>")
    
    task_entry.config(state="normal" if edit_mode else "disabled")
    submit_task_button.config(state="normal" if edit_mode else "disabled")
    update_tasks_display()

# Initialize UI
for i in range(1, 52):
    create_row(i)

# Load saved data
button_colors, loaded_tasks = load_data()
for btn, color in zip(buttons, button_colors):
    btn.config(bg=color)
tasks = loaded_tasks
process_overdue_tasks()

# Control buttons
edit_button = tk.Button(root, text="Edit Mode", command=toggle_edit_mode, bg="#f07167")
exit_button = tk.Button(root, text="Save & Exit", command=save_data, bg="#f07167")
edit_button.grid(row=9, column=50, padx=5, pady=5)
exit_button.grid(row=9, column=51, padx=5, pady=5)

# Initial setup
toggle_edit_mode()
update_tasks_display()

root.mainloop()