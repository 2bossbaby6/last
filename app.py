import tkinter as tk
import pygetwindow as gw
import time as tm


class ActiveAppScreenTimeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Active App Screen Time")

        self.active_app_screen_time = {}
        self.last_active_app = None
        self.last_active_time = tm.time()

        self.label_title = tk.Label(root, text="Active App Screen Time", font=("Helvetica", 16))
        self.label_title.pack(pady=(10, 5))

        self.app_frames = {}  # Dictionary to store frames for each app

        self.update_screen_time()

    def update_screen_time(self):
        current_active_app = gw.getActiveWindowTitle()
        current_time = tm.time()

        if current_active_app != self.last_active_app:
            if self.last_active_app:
                screen_time = current_time - self.last_active_time
                self.active_app_screen_time[self.last_active_app] = self.active_app_screen_time.get(
                    self.last_active_app, 0) + screen_time
                self.update_app_boxes()
            self.last_active_app = current_active_app
            self.last_active_time = current_time

        self.root.after(1000, self.update_screen_time)  # Update every second

    def update_app_boxes(self):
        for widget in self.app_frames.values():
            widget.destroy()

        row = 1
        for app, time in self.active_app_screen_time.items():
            total_time_seconds = int(time)
            total_hours = total_time_seconds // 3600
            total_minutes = (total_time_seconds % 3600) // 60
            total_seconds = total_time_seconds % 60
            time_str = f"{total_hours:02d}:{total_minutes:02d}:{total_seconds:02d}"

            app_frame = tk.Frame(self.root, borderwidth=2, relief="groove", padx=10, pady=5)
            app_frame.pack(pady=5)

            app_label = tk.Label(app_frame, text=f"App: {app}", font=("Helvetica", 12))
            app_label.pack(anchor="w")

            time_label = tk.Label(app_frame, text=f"Time: {time_str}", font=("Helvetica", 12))
            time_label.pack(anchor="w")

            self.app_frames[app] = app_frame


def main():
    root = tk.Tk()
    app = ActiveAppScreenTimeApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()