import tkinter as tk
from tkinter import filedialog, messagebox
import os
import sys
import winsound


sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from scanner import scan_files
from database import init_db, log_event, get_baseline, update_file, delete_file

def get_files_in_folder(folder):
    file_list = []
    for filename in os.listdir(folder):
        full_path = os.path.join(folder, filename)
        if os.path.isfile(full_path):
            file_list.append(full_path)
    return file_list

def compare(folder, old, new):
    all_paths = set(old.keys()) | set(new.keys())
    events_found = False
    for path in all_paths:
        if path not in old:
            log_event(folder, path, "CREATED")
            event_listbox.insert(0, f"[CREATED] {path}")
            events_found = True
        elif path not in new:
            log_event(folder, path, "DELETED")
            delete_file(folder, path)
            winsound.Beep(1000, 500)
            messagebox.showwarning("檔案異動警告", f"{path} 被刪除")
            event_listbox.insert(0, f"[DELETED] {path}")
            events_found = True
        elif old[path] != new[path]:
            log_event(folder, path, "MODIFIED")
            messagebox.showwarning("檔案異動警告", f"{path} 被修改")
            event_listbox.insert(0, f"[MODIFIED] {path}")
            events_found = True
    return events_found

def scan_once():
    folder = folder_path.get()
    files_to_watch = get_files_in_folder(folder)
    baseline = get_baseline(folder)
    current = scan_files(files_to_watch)

    if not baseline:
        status_label.config(text="狀態:建立基準線中...")
    else:
        compare(folder, baseline, current)
        status_label.config(text="狀態:監控中")

    for path, sha256 in current.items():
        update_file(folder, path, sha256)

def scheduled_scan():
    global scan_job
    scan_once()
    scan_job = root.after(5000, scheduled_scan)  # 5 秒後再排程一次

def choose_folder():
    folder = filedialog.askdirectory()
    if folder:
        folder_path.set(folder)
        start_btn.config(state="normal")

def start_monitoring():
    status_label.config(text="狀態:監控中")
    start_btn.config(state="disabled")
    stop_btn.config(state="normal")
    scheduled_scan()  # 立刻開始第一次掃描,並啟動排程

def stop_monitoring():
    global scan_job
    if scan_job is not None:
        root.after_cancel(scan_job)  # 取消排程,停止繼續掃描
        scan_job = None
    status_label.config(text="狀態:已停止")
    start_btn.config(state="normal")
    stop_btn.config(state="disabled")

init_db()
scan_job = None


root = tk.Tk()
root.title("AI Workspace Guardian")
root.geometry("400x300")

folder_path = tk.StringVar()
folder_path.set("尚未選擇資料夾")

choose_btn = tk.Button(root, text="選擇監控資料夾", command=choose_folder)
choose_btn.pack(pady=10)

label = tk.Label(root, textvariable=folder_path, wraplength=350)
label.pack(pady=10)

start_btn = tk.Button(root, text="開始監控", command=start_monitoring, state="disabled")
start_btn.pack(pady=5)

stop_btn = tk.Button(root, text="停止監控", command=stop_monitoring, state="disabled")
stop_btn.pack(pady=5)

status_label = tk.Label(root, text="狀態:尚未開始")
status_label.pack(pady=10)

event_listbox = tk.Listbox(root, width=50, height=8)  # 放在 root 建立之後
event_listbox.pack(pady=10)

root.mainloop()