import gi
import subprocess
import os
from datetime import datetime
import time
import threading

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib

class GrimScreenshotTool:
    def __init__(self):
        # Catppuccin Mocha palette
        self.colors = {
            "base": "#1e1e2e",
            "mantle": "#181825",
            "crust": "#11111b",
            "text": "#cdd6f4",
            "subtext1": "#bac2de",
            "green": "#a6e3a1",
            "blue": "#89b4fa",
            "lavender": "#b4befe",
            "border": "#a6e3a1",
            "selection": "#585b70",
        }
        
        self.capture_mode = "full"
        self.include_cursor = False
        self.image_format = "png"
        self.timer_delay = 0
        self.setup_main_window()
        self.apply_styles()
        self.setup_ui()
        self.window.show_all()

    def setup_main_window(self):
        self.window = Gtk.Window(title="☕ Grim Screenshot")
        self.window.set_default_size(400, 350)
        self.window.set_resizable(False)
        self.window.connect("destroy", Gtk.main_quit)

        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.main_box.set_margin_top(12)
        self.main_box.set_margin_bottom(12)
        self.main_box.set_margin_start(12)
        self.main_box.set_margin_end(12)
        self.window.add(self.main_box)

    def apply_styles(self):
        css = f"""
        .window {{
            background-color: {self.colors["base"]};
            color: {self.colors["text"]};
            border-radius: 14px;
            border: 2px solid {self.colors["border"]};
        }}
        
        .frame {{
            background-color: {self.colors["mantle"]};
            border-radius: 8px;
            padding: 12px;
        }}
        
        .title {{
            font-weight: bold;
            margin-bottom: 8px;
        }}
        
        .mode-button {{
            background-color: {self.colors["mantle"]};
            color: {self.colors["text"]};
            border-radius: 6px;
            padding: 6px 12px;
            border: 1px solid {self.colors["border"]};
        }}
        
        .mode-button:hover {{
            background-color: {self.colors["selection"]};
        }}
        
        .mode-button.active {{
            background-color: {self.colors["green"]};
            color: {self.colors["base"]};
            font-weight: bold;
        }}
        
        .format-button {{
            background-color: {self.colors["mantle"]};
            color: {self.colors["text"]};
            border-radius: 6px;
            padding: 6px 12px;
            border: 1px solid {self.colors["border"]};
            margin-right: 6px;
        }}
        
        .format-button:hover {{
            background-color: {self.colors["selection"]};
        }}
        
        .format-button.active {{
            background-color: {self.colors["green"]};
            color: {self.colors["base"]};
            font-weight: bold;
        }}
        
        .capture-button {{
            background-color: {self.colors["green"]};
            color: {self.colors["base"]};
            border-radius: 8px;
            padding: 10px 24px;
            font-weight: bold;
            font-size: 1.1em;
            margin-top: 12px;
        }}
        
        .capture-button:hover {{
            background-color: {self.colors["lavender"]};
        }}
        
        .entry {{
            background-color: {self.colors["crust"]};
            color: {self.colors["text"]};
            border-radius: 6px;
            padding: 6px;
            border: 1px solid {self.colors["border"]};
        }}
        
        .checkbutton {{
            margin-top: 8px;
        }}
        
        .timer-box {{
            margin-top: 8px;
        }}
        
        .timer-label {{
            margin-right: 8px;
        }}
        
        spinbutton {{
            min-width: 50px;
        }}
        """

        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(css.encode())
        
        screen = Gdk.Screen.get_default()
        style_context = self.window.get_style_context()
        style_context.add_provider_for_screen(
            screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        style_context.add_class("window")

    def setup_ui(self):
        # Capture options frame
        capture_frame = Gtk.Frame()
        capture_frame.get_style_context().add_class("frame")
        self.main_box.pack_start(capture_frame, False, False, 0)
        
        capture_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        capture_frame.add(capture_box)
        
        # Title
        capture_title = Gtk.Label(label="<b>Capture Mode</b>")
        capture_title.set_use_markup(True)
        capture_title.get_style_context().add_class("title")
        capture_title.set_halign(Gtk.Align.START)
        capture_box.pack_start(capture_title, False, False, 0)
        
        # Capture mode buttons
        mode_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        capture_box.pack_start(mode_box, False, False, 0)
        
        self.full_button = Gtk.Button(label="Full Screen")
        self.full_button.connect("clicked", self.on_capture_mode_changed, "full")
        self.full_button.get_style_context().add_class("mode-button")
        self.full_button.get_style_context().add_class("active")
        mode_box.pack_start(self.full_button, True, True, 0)
        
        self.area_button = Gtk.Button(label="Select Area")
        self.area_button.connect("clicked", self.on_capture_mode_changed, "area")
        self.area_button.get_style_context().add_class("mode-button")
        mode_box.pack_start(self.area_button, True, True, 0)
        
        # Include cursor checkbox
        self.cursor_check = Gtk.CheckButton(label="Include Cursor")
        self.cursor_check.connect("toggled", self.on_cursor_toggled)
        self.cursor_check.get_style_context().add_class("checkbutton")
        capture_box.pack_start(self.cursor_check, False, False, 8)
        
        # Timer frame
        timer_frame = Gtk.Frame()
        timer_frame.get_style_context().add_class("frame")
        self.main_box.pack_start(timer_frame, False, False, 8)
        
        timer_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        timer_box.get_style_context().add_class("timer-box")
        timer_frame.add(timer_box)
        
        # Title
        timer_title = Gtk.Label(label="<b>Timer (seconds)</b>")
        timer_title.set_use_markup(True)
        timer_title.get_style_context().add_class("title")
        timer_title.set_halign(Gtk.Align.START)
        timer_box.pack_start(timer_title, False, False, 0)
        
        # Timer input
        self.timer_entry = Gtk.SpinButton.new_with_range(0, 60, 1)
        self.timer_entry.set_value(0)
        timer_box.pack_start(self.timer_entry, False, False, 8)
        
        # Image format frame
        format_frame = Gtk.Frame()
        format_frame.get_style_context().add_class("frame")
        self.main_box.pack_start(format_frame, False, False, 8)
        
        format_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        format_frame.add(format_box)
        
        # Title
        format_title = Gtk.Label(label="<b>Image Format</b>")
        format_title.set_use_markup(True)
        format_title.get_style_context().add_class("title")
        format_title.set_halign(Gtk.Align.START)
        format_box.pack_start(format_title, False, False, 0)
        
        # Format buttons
        format_buttons_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        format_box.pack_start(format_buttons_box, False, False, 0)
        
        formats = ["png", "jpg", "webp"]
        self.format_buttons = []
        
        for fmt in formats:
            btn = Gtk.Button(label=fmt.upper())
            btn.connect("clicked", self.on_format_changed, fmt)
            btn.get_style_context().add_class("format-button")
            if fmt == "png":
                btn.get_style_context().add_class("active")
            format_buttons_box.pack_start(btn, False, False, 0)
            self.format_buttons.append(btn)
        
        # Filename and path frame
        path_frame = Gtk.Frame()
        path_frame.get_style_context().add_class("frame")
        self.main_box.pack_start(path_frame, False, False, 8)
        
        path_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        path_frame.add(path_box)
        
        # Title
        path_title = Gtk.Label(label="<b>Filename and Path</b>")
        path_title.set_use_markup(True)
        path_title.get_style_context().add_class("title")
        path_title.set_halign(Gtk.Align.START)
        path_box.pack_start(path_title, False, False, 0)
        
        # Filename entry
        self.filename_entry = Gtk.Entry()
        self.filename_entry.set_text(self.default_filename())
        self.filename_entry.get_style_context().add_class("entry")
        path_box.pack_start(self.filename_entry, False, False, 0)
        
        # Capture button
        self.capture_button = Gtk.Button(label="Take Screenshot")
        self.capture_button.connect("clicked", self.on_capture_clicked)
        self.capture_button.get_style_context().add_class("capture-button")
        self.main_box.pack_start(self.capture_button, False, False, 12)

    def default_filename(self):
        now = datetime.now()
        return f"screenshot_{now.strftime('%Y%m%d_%H%M%S')}.{self.image_format}"

    def on_capture_mode_changed(self, button, mode):
        self.capture_mode = mode
        
        if mode == "full":
            self.full_button.get_style_context().add_class("active")
            self.area_button.get_style_context().remove_class("active")
        else:
            self.full_button.get_style_context().remove_class("active")
            self.area_button.get_style_context().add_class("active")

    def on_cursor_toggled(self, button):
        self.include_cursor = button.get_active()

    def on_format_changed(self, button, fmt):
        self.image_format = fmt
        
        for btn in self.format_buttons:
            if btn.get_label().lower() == fmt:
                btn.get_style_context().add_class("active")
            else:
                btn.get_style_context().remove_class("active")
        
        current_text = self.filename_entry.get_text()
        base = os.path.splitext(current_text)[0]
        self.filename_entry.set_text(f"{base}.{fmt}")

    def on_capture_clicked(self, button):
        filename = self.filename_entry.get_text().strip()
        if not filename:
            filename = self.default_filename()
        
        self.timer_delay = int(self.timer_entry.get_value())
        
        if self.timer_delay > 0:
            self.capture_button.set_sensitive(False)
            self.capture_button.set_label(f"Capturing in {self.timer_delay}...")
            
            # Start countdown
            threading.Thread(target=self.countdown_and_capture, args=(filename,), daemon=True).start()
        else:
            self.take_screenshot(filename)

    def countdown_and_capture(self, filename):
        for i in range(self.timer_delay, 0, -1):
            GLib.idle_add(self.update_button_label, i)
            time.sleep(1)
        
        GLib.idle_add(self.take_screenshot, filename)

    def update_button_label(self, seconds):
        self.capture_button.set_label(f"Capturing in {seconds}...")
        return False

    def take_screenshot(self, filename):
        cmd = ["grim"]
        
        if self.include_cursor:
            cmd.append("-c")
        
        if self.capture_mode == "area":
            try:
                slurp_process = subprocess.Popen(["slurp"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = slurp_process.communicate()
                
                if slurp_process.returncode != 0:
                    if stderr:
                        error_msg = stderr.decode().strip()
                        if "selection cancelled" in error_msg.lower():
                            self.show_message("Capture cancelled", "No area was selected")
                        else:
                            self.show_message("Slurp error", error_msg)
                    self.reset_capture_button()
                    return
                
                selection = stdout.decode().strip()
                cmd.extend(["-g", selection])
            except FileNotFoundError:
                self.show_message("Error", "slurp is not installed. Required for area selection.")
                self.reset_capture_button()
                return
        
        cmd.append(filename)
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            self.show_message("Success", f"Image saved as:\n{filename}")
            self.filename_entry.set_text(self.default_filename())
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else str(e)
            self.show_message("Capture error", error_msg)
        except FileNotFoundError:
            self.show_message("Error", "grim is not installed. Install with:\nsudo apt install grim slurp")
        finally:
            self.reset_capture_button()

    def reset_capture_button(self):
        self.capture_button.set_label("Take Screenshot")
        self.capture_button.set_sensitive(True)

    def show_message(self, title, message):
        dialog = Gtk.MessageDialog(
            parent=self.window,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text=title
        )
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()

if __name__ == "__main__":
    app = GrimScreenshotTool()
    Gtk.main()
