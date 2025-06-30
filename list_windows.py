"""
This script lists all visible windows on the desktop,
including their title, class, and process ID.
"""

from pywinauto import Desktop

def get_open_windows_info():
    """
    Retrieves information about all visible windows.

    Returns:
        A list of dictionaries, where each dictionary contains
        the 'title', 'class_name', and 'process_id' of a window.
    """
    windows = Desktop(backend="uia").windows()
    windows_info = []
    for w in windows:
        if w.window_text():
            windows_info.append({
                "title": w.window_text(),
                "class_name": w.class_name(),
                "process_id": w.process_id()
            })
    return windows_info

if __name__ == "__main__":
    print("Listing all open windows...")
    all_windows = get_open_windows_info()
    if all_windows:
        for info in all_windows:
            print(f"  - Title: {info['title']}, Class: {info['class_name']}, PID: {info['process_id']}")
    else:
        print("No visible windows found.")
