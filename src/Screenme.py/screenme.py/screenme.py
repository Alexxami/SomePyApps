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
        # Paleta Catppuccin Mocha
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
        # Frame para opciones de captura
        capture_frame = Gtk.Frame()
        capture_frame.get_style_context().add_class("frame")
        self.main_box.pack_start(capture_frame, False, False, 0)
        
        capture_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        capture_frame.add(capture_box)
        
        # Título
        capture_title = Gtk.Label(label="<b>Modo de Captura</b>")
        capture_title.set_use_markup(True)
        capture_title.get_style_context().add_class("title")
        capture_title.set_halign(Gtk.Align.START)
        capture_box.pack_start(capture_title, False, False, 0)
        
        # Botones de modo de captura
        mode_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        capture_box.pack_start(mode_box, False, False, 0)
        
        self.full_button = Gtk.Button(label="Pantalla Completa")
        self.full_button.connect("clicked", self.on_capture_mode_changed, "full")
        self.full_button.get_style_context().add_class("mode-button")
        self.full_button.get_style_context().add_class("active")
        mode_box.pack_start(self.full_button, True, True, 0)
        
        self.area_button = Gtk.Button(label="Seleccionar Área")
        self.area_button.connect("clicked", self.on_capture_mode_changed, "area")
        self.area_button.get_style_context().add_class("mode-button")
        mode_box.pack_start(self.area_button, True, True, 0)
        
        # Checkbox para incluir cursor
        self.cursor_check = Gtk.CheckButton(label="Incluir cursor")
        self.cursor_check.connect("toggled", self.on_cursor_toggled)
        self.cursor_check.get_style_context().add_class("checkbutton")
        capture_box.pack_start(self.cursor_check, False, False, 8)
        
        # Frame para temporizador
        timer_frame = Gtk.Frame()
        timer_frame.get_style_context().add_class("frame")
        self.main_box.pack_start(timer_frame, False, False, 8)
        
        timer_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        timer_box.get_style_context().add_class("timer-box")
        timer_frame.add(timer_box)
        
        # Título
        timer_title = Gtk.Label(label="<b>Temporizador (segundos)</b>")
        timer_title.set_use_markup(True)
        timer_title.get_style_context().add_class("title")
        timer_title.set_halign(Gtk.Align.START)
        timer_box.pack_start(timer_title, False, False, 0)
        
        # Entrada para temporizador
        self.timer_entry = Gtk.SpinButton.new_with_range(0, 60, 1)
        self.timer_entry.set_value(0)
        timer_box.pack_start(self.timer_entry, False, False, 8)
        
        # Frame para formato de imagen
        format_frame = Gtk.Frame()
        format_frame.get_style_context().add_class("frame")
        self.main_box.pack_start(format_frame, False, False, 8)
        
        format_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        format_frame.add(format_box)
        
        # Título
        format_title = Gtk.Label(label="<b>Formato de Imagen</b>")
        format_title.set_use_markup(True)
        format_title.get_style_context().add_class("title")
        format_title.set_halign(Gtk.Align.START)
        format_box.pack_start(format_title, False, False, 0)
        
        # Botones de formato
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
        
        # Frame para nombre y ruta
        path_frame = Gtk.Frame()
        path_frame.get_style_context().add_class("frame")
        self.main_box.pack_start(path_frame, False, False, 8)
        
        path_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        path_frame.add(path_box)
        
        # Título
        path_title = Gtk.Label(label="<b>Nombre y Ruta</b>")
        path_title.set_use_markup(True)
        path_title.get_style_context().add_class("title")
        path_title.set_halign(Gtk.Align.START)
        path_box.pack_start(path_title, False, False, 0)
        
        # Entrada para nombre de archivo
        self.filename_entry = Gtk.Entry()
        self.filename_entry.set_text(self.default_filename())
        self.filename_entry.get_style_context().add_class("entry")
        path_box.pack_start(self.filename_entry, False, False, 0)
        
        # Botón de captura
        self.capture_button = Gtk.Button(label="Capturar Pantalla")
        self.capture_button.connect("clicked", self.on_capture_clicked)
        self.capture_button.get_style_context().add_class("capture-button")
        self.main_box.pack_start(self.capture_button, False, False, 12)

    def default_filename(self):
        now = datetime.now()
        return f"captura_{now.strftime('%Y%m%d_%H%M%S')}.{self.image_format}"

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
            self.capture_button.set_label(f"Capturando en {self.timer_delay}...")
            
            # Iniciar cuenta regresiva
            threading.Thread(target=self.countdown_and_capture, args=(filename,), daemon=True).start()
        else:
            self.take_screenshot(filename)

    def countdown_and_capture(self, filename):
        for i in range(self.timer_delay, 0, -1):
            GLib.idle_add(self.update_button_label, i)
            time.sleep(1)
        
        GLib.idle_add(self.take_screenshot, filename)

    def update_button_label(self, seconds):
        self.capture_button.set_label(f"Capturando en {seconds}...")
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
                            self.show_message("Captura cancelada", "No se seleccionó ningún área")
                        else:
                            self.show_message("Error en slurp", error_msg)
                    self.reset_capture_button()
                    return
                
                selection = stdout.decode().strip()
                cmd.extend(["-g", selection])
            except FileNotFoundError:
                self.show_message("Error", "slurp no está instalado. Es necesario para seleccionar áreas.")
                self.reset_capture_button()
                return
        
        cmd.append(filename)
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            self.show_message("Captura exitosa", f"Imagen guardada como:\n{filename}")
            self.filename_entry.set_text(self.default_filename())
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else str(e)
            self.show_message("Error al capturar", error_msg)
        except FileNotFoundError:
            self.show_message("Error", "grim no está instalado. Instálalo con:\nsudo apt install grim slurp")
        finally:
            self.reset_capture_button()

    def reset_capture_button(self):
        self.capture_button.set_label("Capturar Pantalla")
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