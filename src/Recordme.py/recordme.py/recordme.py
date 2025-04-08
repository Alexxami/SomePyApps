import gi
import subprocess
import signal
from datetime import datetime

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib, Pango

class MochaRecorder:
    def __init__(self):
        self.process = None
        
        # Paleta Catppuccin Mocha
        self.colors = {
            "base": "#1e1e2e",          # Base
            "mantle": "#181825",         # Mantle
            "crust": "#11111b",          # Crust
            "text": "#cdd6f4",           # Text
            "subtext1": "#bac2de",      # Subtext1
            "green": "#a6e3a1",         # Green
            "blue": "#89b4fa",           # Blue
            "lavender": "#b4befe",       # Lavender
            "border": "#a6e3a1",        # Borde verde
            "input_bg": "#313244",       # Fondo del input
        }
        
        # Configurar ventana
        self.window = Gtk.Window(title="☕ Mocha Recorder")
        self.window.set_default_size(320, 240)  # Aumentado para íconos grandes
        self.window.set_resizable(False)
        self.window.connect("destroy", Gtk.main_quit)
        
        # Aplicar CSS
        self.apply_css()
        
        # Contenedor principal
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.box.set_margin_top(16)
        self.box.set_margin_bottom(16)
        self.box.set_margin_start(16)
        self.box.set_margin_end(16)
        self.window.add(self.box)
        
        # Icono principal (más grande)
        self.icon = Gtk.Label()
        self.icon.set_markup('<span font="28">󰄀</span>')  # Tamaño de fuente aumentado
        self.icon.set_margin_bottom(12)
        self.box.pack_start(self.icon, False, False, 0)
        
        # Campo de texto para el nombre del archivo
        self.file_frame = Gtk.Frame()
        self.file_frame.get_style_context().add_class("file-frame")
        
        self.file_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.file_box.set_margin_top(8)
        self.file_box.set_margin_bottom(8)
        self.file_box.set_margin_start(8)
        self.file_box.set_margin_end(8)
        
        self.file_label = Gtk.Label(label="Nombre:")
        self.file_entry = Gtk.Entry()
        self.file_entry.set_placeholder_text("grabacion.mkv")
        self.file_entry.set_text(self.default_filename())
        self.file_entry.get_style_context().add_class("file-entry")
        
        self.file_box.pack_start(self.file_label, False, False, 0)
        self.file_box.pack_start(self.file_entry, True, True, 0)
        self.file_frame.add(self.file_box)
        self.box.pack_start(self.file_frame, False, False, 8)
        
        # Botón con ícono más grande
        self.record_button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.record_button_icon = Gtk.Label()
        self.record_button_icon.set_markup('<span font="16">󰑭</span>')  # Ícono en el botón
        self.record_button_label = Gtk.Label(label="RECORD")
        self.record_button_box.pack_start(self.record_button_icon, False, False, 0)
        self.record_button_box.pack_start(self.record_button_label, False, False, 0)
        
        self.record_button = Gtk.Button()
        self.record_button.add(self.record_button_box)
        self.record_button.connect("clicked", self.toggle_recording)
        self.record_button.get_style_context().add_class("record-button")
        self.box.pack_start(self.record_button, False, False, 0)
        
        # Estado
        self.status_label = Gtk.Label(label="Preparado para grabar")
        self.status_label.get_style_context().add_class("status-label")
        self.box.pack_start(self.status_label, False, False, 12)
        
        self.window.show_all()
    
    def default_filename(self):
        """Genera un nombre de archivo por defecto con la fecha y hora"""
        now = datetime.now()
        return f"grabacion_{now.strftime('%Y%m%d_%H%M%S')}.mkv"
    
    def apply_css(self):
        css = f"""
        .window {{
            background-color: {self.colors["base"]};
            color: {self.colors["text"]};
            border-radius: 14px;
            border: 2px solid {self.colors["border"]};
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
        }}
        
        .file-frame {{
            background-color: {self.colors["mantle"]};
            border-radius: 8px;
            border: 1px solid {self.colors["border"]};
        }}
        
        .file-entry {{
            background-color: {self.colors["input_bg"]};
            color: {self.colors["text"]};
            border-radius: 6px;
            padding: 6px;
            border: 1px solid {self.colors["crust"]};
        }}
        
        .file-entry:focus {{
            border-color: {self.colors["green"]};
        }}
        
        .record-button {{
            background-color: {self.colors["mantle"]};
            color: {self.colors["text"]};
            border: 2px solid {self.colors["green"]};
            border-radius: 10px;
            padding: 12px 24px;
            font-weight: bold;
            font-size: 1.1em;
            transition: all 0.2s ease;
        }}
        
        .record-button:hover {{
            background-color: {self.colors["crust"]};
            border-color: {self.colors["lavender"]};
        }}
        
        .status-label {{
            color: {self.colors["subtext1"]};
            font-size: 0.95em;
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
    
    def toggle_recording(self, button):
        if self.process is None:
            try:
                filename = self.file_entry.get_text().strip()
                if not filename:
                    filename = self.default_filename()
                if not filename.endswith('.mkv'):
                    filename += '.mkv'
                
                self.process = subprocess.Popen(["wf-recorder", "-f", filename])
                # Actualizar íconos
                self.icon.set_markup('<span font="28">󰑋</span>')  # Ícono de grabación grande
                self.record_button_icon.set_markup('<span font="16">󰓛</span>')  # Ícono de stop
                self.record_button_label.set_text("STOP")
                self.status_label.set_markup(
                    f'<span foreground="{self.colors["green"]}" weight="bold">GRABANDO: {filename}</span>'
                )
            except FileNotFoundError:
                self.show_error_dialog()
        else:
            self.process.send_signal(signal.SIGINT)
            self.process = None
            # Restaurar íconos
            self.icon.set_markup('<span font="28">󰄀</span>')  # Ícono de cámara grande
            self.record_button_icon.set_markup('<span font="16">󰑭</span>')  # Ícono de record
            self.record_button_label.set_text("RECORD")
            self.status_label.set_markup(
                f'<span foreground="{self.colors["blue"]}">Grabación guardada</span>'
            )
            # Actualizar el nombre para la próxima grabación
            self.file_entry.set_text(self.default_filename())
    
    def show_error_dialog(self):
        dialog = Gtk.MessageDialog(
            parent=self.window,
            flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text="Error: wf-recorder no está instalado"
        )
        dialog.format_secondary_text("Instala con:\nsudo apt install wf-recorder")
        dialog.run()
        dialog.destroy()

if __name__ == "__main__":
    app = MochaRecorder()
    Gtk.main()