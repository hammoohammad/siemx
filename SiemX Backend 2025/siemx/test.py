import wmi
import pythoncom
import threading
import time

class UserGroupMonitor(threading.Thread):
    def __init__(self, callback):
        super().__init__(daemon=True)
        self.callback = callback
        self.running = True

    def run(self):
        # IMPORTANT FIX — initialize COM inside this thread
        pythoncom.CoInitialize()

        c = wmi.WMI()

        self.callback("🔍 Monitoring User & Group changes...\n")

        user_create = c.watch_for(notification_type="Creation", wmi_class="Win32_UserAccount")
        user_delete = c.watch_for(notification_type="Deletion", wmi_class="Win32_UserAccount")
        group_create = c.watch_for(notification_type="Creation", wmi_class="Win32_Group")
        group_delete = c.watch_for(notification_type="Deletion", wmi_class="Win32_Group")

        while self.running:
            try:
                event = user_create(timeout_ms=500)
                self.callback(f"[USER CREATED] {event.Name} ({event.Domain})")
            except wmi.x_wmi_timed_out:
                pass

            try:
                event = user_delete(timeout_ms=500)
                self.callback(f"[USER DELETED] {event.Name} ({event.Domain})")
            except wmi.x_wmi_timed_out:
                pass

            try:
                event = group_create(timeout_ms=500)
                self.callback(f"[GROUP CREATED] {event.Name} ({event.Domain})")
            except wmi.x_wmi_timed_out:
                pass

            try:
                event = group_delete(timeout_ms=500)
                self.callback(f"[GROUP DELETED] {event.Name} ({event.Domain})")
            except wmi.x_wmi_timed_out:
                pass

        pythoncom.CoUninitialize()

    def stop(self):
        self.running = False



def print_log(msg):
    print(msg)

monitor = UserGroupMonitor(print_log)
monitor.start()

# Now your main program continues running normally
while True:
    time.sleep(1)
