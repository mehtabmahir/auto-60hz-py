from ctypes import windll, Structure, byref, c_int
import win32gui
import win32api
import win32con
import time

class RECT(Structure):
    _fields_ = [("left", c_int), ("top", c_int), ("right", c_int), ("bottom", c_int)]

def set_refresh_rate(rate):
    devmode = win32api.EnumDisplaySettings(None, win32con.ENUM_CURRENT_SETTINGS)
    devmode.DisplayFrequency = rate
    win32api.ChangeDisplaySettings(devmode, win32con.CDS_FULLSCREEN)

def is_any_full_screen():
    user32 = windll.user32
    dwmapi = windll.dwmapi
    user32.SetProcessDPIAware()  # Optional, makes functions return real pixel numbers instead of scaled values

    full_screen_rect = RECT(0, 0, user32.GetSystemMetrics(0), user32.GetSystemMetrics(1))

    def enum_windows_proc(hwnd, results):
        if win32gui.IsWindow(hwnd):
            rect = RECT()
            # DWMWA_EXTENDED_FRAME_BOUNDS = 9
            if dwmapi.DwmGetWindowAttribute(hwnd, 9, byref(rect), c_int(16)) == 0:  # c_int(16) is the size of RECT
                if (rect.left, rect.top, rect.right, rect.bottom) == (full_screen_rect.left, full_screen_rect.top, full_screen_rect.right, full_screen_rect.bottom):
                    class_name = win32gui.GetClassName(hwnd)
                    if class_name not in ["Progman", "SnippingTool", "MultitaskingViewFrame", "XamlExplorerHostIslandWindow", 
                                          "WindowsDashboard", "ApplicationFrameWindow", "TabletModeCoverWindow"]:
                        results.append((hwnd, class_name))

    try:
        results = []
        win32gui.EnumWindows(enum_windows_proc, results)
        if results:
            for hwnd, class_name in results:
                print(f"[DEBUG] Detected fullscreen window: Handle={hwnd}, Class={class_name}")
            return True
        else:
            print("[DEBUG] No fullscreen windows detected.")
            return False
    except Exception as e:
        print(f"[ERROR] Failed to detect fullscreen: {e}")
        return False

def main():
    print("[INFO] Starting fullscreen detection loop")
    while True:
        if is_any_full_screen():
            set_refresh_rate(60)
        else:
            set_refresh_rate(120)
        time.sleep(1)  # Check every second

if __name__ == "__main__":
    main()
