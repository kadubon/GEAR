from pywinauto import Application, Desktop
from pywinauto.timings import TimeoutError
import time
import psutil
import subprocess
import pyautogui
import re
from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext # Import Playwright components

class GUIController:
    """
    Manages GUI automation tasks, encapsulating application lifecycle and element interactions.
    Uses pywinauto for robust UI Automation and includes pyautogui for screen-based operations.
    """

    def __init__(self, backend="uia"):
        """
        Initializes the GUIController with a specified pywinauto backend.
        :param backend: The pywinauto backend to use ('uia' for UI Automation, 'win32' for Win32 API).
        """
        self.backend = backend
        self.current_app = None # To hold the currently connected pywinauto application object

    def _get_process_id_by_name(self, app_exe_name: str, timeout: int = 10) -> int | None:
        """
        Gets the process ID of an application by its executable name, with a retry mechanism.
        :param app_exe_name: The executable name of the application (e.g., 'notepad.exe').
        :param timeout: How long to wait for the process to appear (in seconds).
        :return: The process ID if found, None otherwise.
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            for proc in psutil.process_iter(['name', 'pid']):
                if proc.info['name'] == app_exe_name:
                    print(f"DEBUG: Found process {app_exe_name} with PID: {proc.info['pid']}")
                    return proc.info['pid']
            time.sleep(0.5) # Wait a bit before retrying
        print(f"ERROR: Could not find process ID for {app_exe_name} within {timeout} seconds.")
        return None

    def _wait_for_app_window(self, title_re: str, timeout: int = 20, initial_pids: set = None) -> Application | None:
        """
        Waits for a new application window to appear and connects to it.
        This is particularly useful for UWP apps where direct connection by PID can be tricky.
        :param title_re: Regex for the main window title to wait for.
        :param timeout: How long to wait for the window to appear (in seconds).
        :param initial_pids: A set of PIDs that existed before the app launch, to identify new instances.
        :return: The Application object if connected, None otherwise.
        """
        if initial_pids is None:
            initial_pids = set()

        app = Application(backend=self.backend)
        start_time = time.time()
        while time.time() - start_time < timeout:
            for w in Desktop(backend=self.backend).windows():
                try:
                    # Check if it's a new window matching the title regex
                    if w.window_text() and re.match(title_re, w.window_text()) and w.process_id() not in initial_pids:
                        print(f"DEBUG: Found potential new window: Title='{w.window_text()}', PID={w.process_id()}")
                        # Attempt to connect to this window's process
                        app.connect(process=w.process_id(), timeout=1)
                        # Ensure the window is ready for interaction
                        app.top_window().wait('ready', timeout=5)
                        print(f"DEBUG: Successfully connected to app with PID: {w.process_id()}")
                        return app
                except Exception as e:
                    print(f"DEBUG: Error checking window or connecting: {e}")
            time.sleep(1) # Wait before retrying window enumeration
        print(f"ERROR: Could not find or connect to window with title_re '{title_re}' within {timeout} seconds.")
        return None

    def start_application(self, path: str = None, title_re: str = None, aumid: str = None, timeout: int = 20) -> bool:
        """
        Starts an application and connects to it.
        For UWP apps, use aumid. For Win32 apps, use path.
        Sets the connected application to self.current_app.
        :param path: The executable path of the application (for Win32 apps).
        :param title_re: Regex for the main window title to wait for (optional, but recommended for UWP).
        :param aumid: The AUMID of the UWP application (for UWP apps).
        :param timeout: How long to wait for the application/window to appear (in seconds).
        :return: True if the application started and connected successfully, False otherwise.
        """
        self.current_app = None
        try:
            if aumid:
                print(f"DEBUG: Launching UWP app with AUMID: {aumid}")
                launch_command = f"explorer.exe shell:AppsFolder\\{aumid}"
                subprocess.Popen(launch_command, shell=True)
                time.sleep(2) # Give it a moment to start

                # Workaround: Use pyautogui to bring the UWP app to foreground
                pyautogui.hotkey('win', 'r') # Open Run dialog
                time.sleep(0.5)
                pyautogui.typewrite(f"shell:AppsFolder\\{aumid}") # Type AUMID
                time.sleep(0.5)
                pyautogui.press('enter') # Press Enter to launch/focus
                time.sleep(2) # Give it time to focus

                # Now try to connect with pywinauto
                try:
                    app = Application(backend=self.backend)
                    app.connect(title_re=title_re, timeout=timeout)
                    self.current_app = app
                    print(f"DEBUG: Connected to UWP app: {aumid}")
                    return True
                except TimeoutError:
                    print(f"ERROR: Timeout while connecting to UWP app (AUMID: {aumid}, Title_re: {title_re}) after pyautogui workaround.")
                    return False
                except Exception as e:
                    print(f"ERROR: An unexpected error occurred while connecting to UWP app (AUMID: {aumid}) after pyautogui workaround: {e}")
                    return False

            elif path:
                print(f"DEBUG: Starting Win32 app from path: {path}")
                app = Application(backend=self.backend).start(path)
                app.wait_for_process(timeout=timeout) # Wait for the process to be ready
                self.current_app = app
                
                if title_re and self.current_app:
                    print(f"DEBUG: Waiting for main window with title_re: {title_re} to be ready.")
                    self.current_app.top_window().wait('ready', timeout=timeout)
                    print("DEBUG: Main window is ready.")
                print(f"DEBUG: Started and connected to Win32 app: {path}")
                return True
            else:
                print("ERROR: Either path or aumid must be provided to start an application.")
                return False
            
        except TimeoutError:
            print(f"ERROR: Timeout while starting/connecting to application (AUMID: {aumid}, Path: {path}, Title_re: {title_re}).")
            return False
        except Exception as e:
            print(f"ERROR: An unexpected error occurred while starting application (AUMID: {aumid}, Path: {path}): {e}")
            return False

    def close_current_application(self) -> bool:
        """
        Closes the currently connected application.
        :return: True if the application was closed successfully, False otherwise.
        """
        if self.current_app:
            try:
                self.current_app.kill()
                print(f"DEBUG: Closed application with PID: {self.current_app.process}")
                self.current_app = None
                return True
            except Exception as e:
                print(f"ERROR: Error closing current application: {e}")
                return False
        print("WARNING: No application is currently connected to close.")
        return False

    def close_application_by_name(self, app_exe_name: str) -> bool:
        """
        Closes all instances of an application by its executable name.
        :param app_exe_name: The executable name of the application (e.g., 'notepad.exe').
        :return: True if all instances were closed or none were found, False otherwise.
        """
        closed_any = False
        for proc in psutil.process_iter(['name', 'pid']):
            if proc.info['name'] == app_exe_name:
                try:
                    p = psutil.Process(proc.info['pid'])
                    p.terminate() # Try graceful termination first
                    p.wait(timeout=5) # Wait for process to terminate
                    if p.is_running():
                        p.kill() # Force kill if still running
                    closed_any = True
                    print(f"DEBUG: Closed process {app_exe_name} (PID: {proc.info['pid']})")
                except psutil.NoSuchProcess:
                    pass # Process already terminated
                except Exception as e:
                    print(f"ERROR: Error closing process {app_exe_name} (PID: {proc.info['pid']}): {e}")
                    return False
        if not closed_any:
            print(f"DEBUG: No instances of {app_exe_name} were found to close.")
        return True

    def click_element(self, control_identifiers: dict) -> bool:
        """
        Finds a GUI element within the current application and clicks it.
        :param control_identifiers: A dictionary of identifiers to find the control (e.g., {"control_type": "Button", "title": "OK"}).
        :return: True if the element was found and clicked, False otherwise.
        """
        if not self.current_app:
            print("ERROR: No application is connected. Cannot click element.")
            return False
        try:
            main_window = self.current_app.top_window()
            control = main_window.child_window(**control_identifiers)
            control.click_input()
            print(f"DEBUG: Clicked element with identifiers: {control_identifiers}")
            return True
        except TimeoutError:
            print(f"ERROR: Timeout: Could not find element with identifiers {control_identifiers} in current app.")
            return False
        except Exception as e:
            print(f"ERROR: Error finding or clicking element {control_identifiers}: {e}")
            return False

    def type_text_in_element(self, control_identifiers: dict, text: str) -> bool:
        """
        Finds a GUI element within the current application and types text into it.
        :param control_identifiers: Identifiers to find the control.
        :param text: The text to type.
        :return: True if text was typed successfully, False otherwise.
        """
        if not self.current_app:
            print("ERROR: No application is connected. Cannot type text.")
            return False
        try:
            main_window = self.current_app.top_window()
            control = main_window.child_window(**control_identifiers)
            control.set_text(text) # Use set_text for direct text input
            print(f"DEBUG: Typed text '{text}' into element with identifiers: {control_identifiers}")
            return True
        except TimeoutError:
            print(f"ERROR: Timeout: Could not find element with identifiers {control_identifiers} in current app.")
            return False
        except Exception as e:
            print(f"ERROR: Error typing text in element {control_identifiers}: {e}")
            return False

    def send_keys_to_app(self, keys: str) -> bool:
        """
        Sends keyboard keys to the currently connected application.
        :param keys: The keys to send (e.g., "^s" for Ctrl+S, "{ENTER}").
        :return: True if keys were sent successfully, False otherwise.
        """
        if not self.current_app:
            print("ERROR: No application is connected. Cannot send keys.")
            return False
        try:
            self.current_app.top_window().type_keys(keys)
            print(f"DEBUG: Sent keys '{keys}' to current application.")
            return True
        except TimeoutError:
            print(f"ERROR: Timeout: Could not connect to application to send keys.")
            return False
        except Exception as e:
            print(f"ERROR: Error sending keys to application: {e}")
            return False

    def print_app_control_identifiers(self) -> None:
        """
        Prints the control identifiers for all controls in the current application's main window.
        Useful for debugging and discovering UI elements.
        """
        if not self.current_app:
            print("ERROR: No application is connected. Cannot print control identifiers.")
            return
        try:
            main_window = self.current_app.top_window()
            print(f"DEBUG: Printing control identifiers for: {main_window.window_text()}")
            main_window.print_control_identifiers()
        except Exception as e:
            print(f"ERROR: Error printing control identifiers: {e}")

    def take_screenshot(self, file_path: str) -> bool:
        """
        Takes a screenshot of the entire screen and saves it to a file.
        This uses pyautogui, which is a screen-based operation.
        :param file_path: The path to save the screenshot file.
        :return: True if successful, False otherwise.
        """
        try:
            screenshot = pyautogui.screenshot()
            screenshot.save(file_path)
            print(f"DEBUG: Screenshot saved to: {file_path}")
            return True
        except Exception as e:
            print(f"ERROR: Error taking screenshot: {e}")
            return False

    def click_on_screen(self, x: int, y: int) -> bool:
        """
        Clicks on a specific coordinate on the screen using pyautogui.
        :param x: X-coordinate.
        :param y: Y-coordinate.
        :return: True if successful, False otherwise.
        """
        try:
            pyautogui.click(x, y)
            print(f"DEBUG: Clicked on screen at ({x}, {y}).")
            return True
        except Exception as e:
            print(f"ERROR: Error clicking on screen at ({x}, {y}): {e}")
            return False

    def click_image(self, image_path: str, confidence: float = 0.9, timeout: int = 10) -> bool:
        """
        Finds an image on the screen and clicks its center using pyautogui.
        :param image_path: Path to the image file to find.
        :param confidence: Confidence level for image recognition (0.0 to 1.0).
        :param timeout: How long to wait for the image to appear.
        :return: True if the image was found and clicked, False otherwise.
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                location = pyautogui.locateOnScreen(image_path, confidence=confidence)
                if location:
                    pyautogui.click(location)
                    print(f"DEBUG: Clicked image '{image_path}'.")
                    return True
            except Exception as e:
                print(f"DEBUG: Error locating image '{image_path}': {e}")
            time.sleep(1)
        print(f"ERROR: Image '{image_path}' not found within {timeout} seconds.")
        return False

    def type_text_pyautogui(self, text: str, interval: float = 0.05) -> bool:
        """
        Types the given text using pyautogui.
        :param text: The text to type.
        :param interval: The interval between key presses.
        :return: True if successful, False otherwise.
        """
        try:
            pyautogui.typewrite(text, interval=interval)
            print(f"DEBUG: Typed text '{text}' using pyautogui.")
            return True
        except Exception as e:
            print(f"ERROR: Error typing text with pyautogui: {e}")
            return False

    def wait_for_image(self, image_path: str, confidence: float = 0.9, timeout: int = 10) -> bool:
        """
        Waits for an image to appear on the screen using pyautogui.
        :param image_path: Path to the image file to find.
        :param confidence: Confidence level for image recognition (0.0 to 1.0).
        :param timeout: How long to wait for the image to appear.
        :return: True if the image appears within the timeout, False otherwise.
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                location = pyautogui.locateOnScreen(image_path, confidence=confidence)
                if location:
                    print(f"DEBUG: Image '{image_path}' found.")
                    return True
            except Exception as e:
                print(f"DEBUG: Error locating image '{image_path}': {e}")
            time.sleep(1)
        print(f"ERROR: Image '{image_path}' not found within {timeout} seconds.")
        return False

class WebController:
    """
    Manages web automation tasks using Playwright.
    """
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def launch_browser(self, browser_type: str = "chromium", headless: bool = True) -> bool:
        """
        Launches a browser instance.
        :param browser_type: Type of browser to launch ('chromium', 'firefox', 'webkit').
        :param headless: Whether to run the browser in headless mode.
        :return: True if successful, False otherwise.
        """
        try:
            self.playwright = sync_playwright().start()
            if browser_type == "chromium":
                self.browser = self.playwright.chromium.launch(headless=headless)
            elif browser_type == "firefox":
                self.browser = self.playwright.firefox.launch(headless=headless)
            elif browser_type == "webkit":
                self.browser = self.playwright.webkit.launch(headless=headless)
            else:
                print(f"ERROR: Unsupported browser type: {browser_type}")
                return False
            self.context = self.browser.new_context()
            self.page = self.context.new_page()
            print(f"DEBUG: Launched {browser_type} browser (headless={headless}).")
            return True
        except Exception as e:
            print(f"ERROR: Error launching browser: {e}")
            return False

    def navigate(self, url: str) -> bool:
        """
        Navigates to a specified URL.
        :param url: The URL to navigate to.
        :return: True if successful, False otherwise.
        """
        if not self.page:
            print("ERROR: No page available. Launch browser first.")
            return False
        try:
            self.page.goto(url)
            print(f"DEBUG: Navigated to URL: {url}")
            return True
        except Exception as e:
            print(f"ERROR: Error navigating to URL {url}: {e}")
            return False

    def type_text_web(self, selector: str, text: str) -> bool:
        """
        Types text into an element identified by a CSS selector.
        :param selector: CSS selector of the input element.
        :param text: The text to type.
        :return: True if successful, False otherwise.
        """
        if not self.page:
            print("ERROR: No page available. Launch browser first.")
            return False
        try:
            self.page.fill(selector, text)
            print(f"DEBUG: Typed text '{text}' into selector '{selector}'.")
            return True
        except Exception as e:
            print(f"ERROR: Error typing text into selector '{selector}': {e}")
            return False

    def click_element_web(self, selector: str) -> bool:
        """
        Clicks an element identified by a CSS selector.
        :param selector: CSS selector of the element to click.
        :return: True if successful, False otherwise.
        """
        if not self.page:
            print("ERROR: No page available. Launch browser first.")
            return False
        try:
            self.page.click(selector)
            print(f"DEBUG: Clicked element with selector '{selector}'.")
            return True
        except Exception as e:
            print(f"ERROR: Error clicking element with selector '{selector}': {e}")
            return False

    def get_text_content(self, selector: str) -> str | None:
        """
        Gets the text content of an element identified by a CSS selector.
        :param selector: CSS selector of the element.
        :return: The text content if found, None otherwise.
        """
        if not self.page:
            print("ERROR: No page available. Launch browser first.")
            return None
        try:
            text_content = self.page.text_content(selector)
            print(f"DEBUG: Got text content from selector '{selector}'.")
            return text_content
        except Exception as e:
            print(f"ERROR: Error getting text content from selector '{selector}': {e}")
            return None

    def wait_for_selector(self, selector: str, state: str = "visible", timeout: int = 30000) -> bool:
        """
        Waits for an element identified by a CSS selector to satisfy a certain state.
        :param selector: CSS selector of the element.
        :param state: The state to wait for ('attached', 'detached', 'hidden', 'visible').
        :param timeout: Maximum time to wait in milliseconds.
        :return: True if the selector satisfies the state within the timeout, False otherwise.
        """
        if not self.page:
            print("ERROR: No page available. Launch browser first.")
            return False
        try:
            self.page.wait_for_selector(selector, state=state, timeout=timeout)
            print(f"DEBUG: Waited for selector '{selector}' to be '{state}'.")
            return True
        except Exception as e:
            print(f"ERROR: Error waiting for selector '{selector}' to be '{state}': {e}")
            return False

    def close_browser(self) -> bool:
        """
        Closes the browser instance.
        :return: True if successful, False otherwise.
        """
        try:
            if self.browser:
                self.browser.close()
                self.browser = None
            if self.playwright:
                self.playwright.stop()
                self.playwright = None
            print("DEBUG: Browser closed.")
            return True
        except Exception as e:
            print(f"ERROR: Error closing browser: {e}")
            return False
