import tkinter as tk
from tkinter import filedialog

def choose_folder():
    folder = filedialog.askdirectory()
    if folder:
        print(f"你選擇了: {folder}")

root = tk.Tk()
root.title("AI Workspace Guardian")
root.geometry("400x300")

btn = tk.Button(root, text="選擇監控資料夾", command=choose_folder)
btn.pack(pady=20)

root.mainloop()