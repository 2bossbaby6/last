import tkinter as tk
from tkinter import ttk
import sqlite3

class ActiveAppScreenTimeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Active App Screen Time")

        self.label_title = tk.Label(root, text="Active App Screen Time", font=("Helvetica", 16))
        self.label_title.pack(pady=(10, 5))

        self.scrollbar = ttk.Scrollbar(root)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas = tk.Canvas(root, yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar.config(command=self.canvas.yview)

        self.scrollable_frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.retrieve_screen_time()

        self.scrollable_frame.bind("<Configure>", self.on_frame_configure)

    def retrieve_screen_time(self):
        conn = sqlite3.connect('screen_time.db')
        c = conn.cursor()

        c.execute("SELECT app, SUM(time) FROM ScreenTime GROUP BY app")
        screen_time_data = c.fetchall()

        for app, time in screen_time_data:
            self.create_app_frame(app, time)

        conn.close()

    def create_app_frame(self, app, total_time_seconds):
        total_hours = int(total_time_seconds) // 3600
        total_minutes = int((total_time_seconds % 3600) // 60)
        total_seconds = int(total_time_seconds % 60)
        time_str = f"{total_hours:02d}:{total_minutes:02d}:{total_seconds:02d}"

        app_frame = tk.Frame(self.scrollable_frame, borderwidth=2, relief="groove", padx=10, pady=5)
        app_frame.pack(pady=5, fill=tk.X)

        app_label = tk.Label(app_frame, text=f"App: {app}", font=("Helvetica", 12))
        app_label.pack(anchor="w")

        time_label = tk.Label(app_frame, text=f"Time: {time_str}", font=("Helvetica", 12))
        time_label.pack(anchor="w")

    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))


def main():
    root = tk.Tk()
    root.geometry("470x340")
    app = ActiveAppScreenTimeApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()