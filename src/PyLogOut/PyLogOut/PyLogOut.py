#!/usr/bin/env python3

import gi
import subprocess
import os

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib

class LogoutMenu(Gtk.Window):
    def __init__(self):
        super().__init__(title="Menú de Logout")
        self.set_wmclass("PyLogOut", "Logout Menu")
        
        # Configurar para pantalla completa en Hyprland
        self.set_default_size(1920, 1080)
        self.fullscreen()
        
        # Configurar el color de fondo principal #1e1e2e
        bg_color = Gdk.RGBA()
        bg_color.parse("#1e1e2e")
        self.override_background_color(Gtk.StateFlags.NORMAL, bg_color)
        
        # Crear un grid 2x2 para los botones
        grid = Gtk.Grid()
        grid.set_row_spacing(10)
        grid.set_column_spacing(10)
        grid.set_margin_top(10)
        grid.set_margin_bottom(10)
        grid.set_margin_start(10)
        grid.set_margin_end(10)
        self.add(grid)
        
        # Estilo CSS para los botones con fondo #1e1e2e
        css_provider = Gtk.CssProvider()
        css = """
        button {
            font-size: 200px;
            color: white;
            background-color: #1e1e2e;
            border-radius: 20px;
            border-width: 3px;
            border-color: #f38ba8;
            padding: 20px;
            margin: 10px;
        }
        button:hover {
            background-color: #45475a;
        }
        window {
            background-color: rgba(0, 0, 0, 0);
        }
        """
        css_provider.load_from_data(css.encode())
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        
        # Botón de Logout
        btn_logout = Gtk.Button(label="󰍃")
        btn_logout.connect("clicked", self.on_logout_clicked)
        btn_logout.set_hexpand(True)
        btn_logout.set_vexpand(True)
        
        # Botón de Apagar
        btn_poweroff = Gtk.Button(label="󰐥")
        btn_poweroff.connect("clicked", self.on_poweroff_clicked)
        btn_poweroff.set_hexpand(True)
        btn_poweroff.set_vexpand(True)
        
        # Botón de Reiniciar
        btn_reboot = Gtk.Button(label="")
        btn_reboot.connect("clicked", self.on_reboot_clicked)
        btn_reboot.set_hexpand(True)
        btn_reboot.set_vexpand(True)
        
        # Botón de Suspender
        btn_suspend = Gtk.Button(label="")
        btn_suspend.connect("clicked", self.on_suspend_clicked)
        btn_suspend.set_hexpand(True)
        btn_suspend.set_vexpand(True)
        
        # Añadir botones al grid
        grid.attach(btn_logout, 0, 0, 1, 1)
        grid.attach(btn_poweroff, 1, 0, 1, 1)
        grid.attach(btn_reboot, 0, 1, 1, 1)
        grid.attach(btn_suspend, 1, 1, 1, 1)
        
        # Conectar tecla Escape para cerrar
        self.connect("key-press-event", self.on_key_press)
        
    def on_key_press(self, widget, event):
        # Cerrar con Escape
        if event.keyval == Gdk.KEY_Escape:
            self.close()
    
    def on_logout_clicked(self, button):
        # Comando para cerrar sesión en Hyprland
        subprocess.run(["hyprctl", "dispatch", "exit"])
        self.close()
    
    def on_poweroff_clicked(self, button):
        # Comando para apagar
        subprocess.run(["poweroff"])
        self.close()
    
    def on_reboot_clicked(self, button):
        # Comando para reiniciar
        subprocess.run(["reboot"])
        self.close()
    
    def on_suspend_clicked(self, button):
        # Comando para suspender
        subprocess.run(["suspend"])
        self.close()

def main():
    win = LogoutMenu()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()