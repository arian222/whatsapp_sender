import customtkinter as ctk
from tkinter import messagebox, filedialog
import pywhatkit
from datetime import datetime, timedelta
import time
import math
import os
import logging
import json
import pyautogui
import keyboard
import csv
import pickle

# Configurare logging
log_directory = "logs"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

log_file = os.path.join(log_directory, f"whatsapp_log_{datetime.now().strftime('%Y%m%d')}.txt")
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Configurare PyAutoGUI pentru siguranță
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 1

def send_message_automatically():
    """Funcție pentru trimiterea automată a mesajului"""
    try:
        # Așteptăm să se încarce WhatsApp Web
        time.sleep(2)
        
        # Apăsăm Enter pentru trimitere
        pyautogui.press('enter')
        
        # Așteptăm puțin pentru a se trimite mesajul
        time.sleep(1)
        
        return True
    except Exception as e:
        print(f"Eroare la trimiterea automată: {str(e)}")
        return False

class LogViewer(ctk.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("ALECS Pro - Istoric Operațiuni")
        self.geometry("600x400")
        
        # Frame principal
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Titlu
        self.title_label = ctk.CTkLabel(
            self.main_frame,
            text="📋 Istoric Operațiuni",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.title_label.pack(pady=10)
        
        # Text box pentru log-uri
        self.log_text = ctk.CTkTextbox(
            self.main_frame,
            wrap="word",
            height=300
        )
        self.log_text.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Butoane
        self.button_frame = ctk.CTkFrame(self.main_frame)
        self.button_frame.pack(fill="x", padx=10, pady=5)
        
        self.refresh_button = ctk.CTkButton(
            self.button_frame,
            text="🔄 Reîmprospătează",
            command=self.refresh_logs,
            height=30,
            font=ctk.CTkFont(size=12),
            fg_color=("#00AA00", "#00AA00"),
            hover_color=("#008800", "#008800")
        )
        self.refresh_button.pack(side="left", padx=5)
        
        self.clear_button = ctk.CTkButton(
            self.button_frame,
            text="🗑️ Șterge Istoric",
            command=self.clear_logs,
            height=30,
            font=ctk.CTkFont(size=12),
            fg_color=("#AA0000", "#AA0000"),
            hover_color=("#880000", "#880000")
        )
        self.clear_button.pack(side="right", padx=5)
        
        self.refresh_logs()
        
    def refresh_logs(self):
        self.log_text.delete("0.0", "end")
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                logs = f.readlines()
                for log in logs[-1000:]:  # Afișăm ultimele 1000 de linii
                    self.log_text.insert("end", log)
            self.log_text.see("end")  # Scroll la ultima linie
        except:
            self.log_text.insert("end", "Nu există încă istoric de operațiuni.")
            
    def clear_logs(self):
        if messagebox.askyesno("ALECS Pro - Confirmare", "Sigur doriți să ștergeți tot istoricul?"):
            try:
                open(log_file, "w").close()
                self.refresh_logs()
                messagebox.showinfo("ALECS Pro - Succes", "Istoricul a fost șters cu succes!")
            except:
                messagebox.showerror("ALECS Pro - Eroare", "Nu s-a putut șterge istoricul!")

class WhatsAppSender:
    def __init__(self, root):
        self.root = root
        self.root.title("ALECS WhatsApp Pro")
        self.root.geometry("500x800")  # Mărit puțin pentru a încăpea toate elementele
        
        # Variabile pentru animație
        self.animation_counter = 0
        self.pulse_colors = [
            "#00FF00", "#00FF33", "#00FF66", "#00FF99", "#00FFCC", 
            "#00FFFF", "#00CCFF", "#0099FF", "#0066FF", "#0033FF",
            "#0000FF", "#3300FF", "#6600FF", "#9900FF", "#CC00FF",
            "#FF00FF", "#FF00CC", "#FF0099", "#FF0066", "#FF0033",
            "#FF0000", "#FF3300", "#FF6600", "#FF9900", "#FFCC00",
            "#FFFF00", "#CCFF00", "#99FF00", "#66FF00", "#33FF00"
        ]
        self.current_color_index = 0
        self.rotation_angle = 0
        
        # Container principal - schimbat din ScrollableFrame în Frame normal
        self.main_frame = ctk.CTkFrame(root)
        self.main_frame.pack(pady=5, padx=5, fill="both", expand=True)
        
        # Variabile pentru funcționalități
        self.templates = self.load_templates()
        self.recurring_schedule = None
        self.contacts = []
        self.attached_image = None
        self.group_id = None
        self.multiple_schedule = []
        
        # Organizăm elementele în tab-uri pentru o mai bună organizare
        self.tabview = ctk.CTkTabview(self.main_frame)
        self.tabview.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Creăm tab-urile principale
        self.tab_main = self.tabview.add("📱 Principal")
        self.tab_extra = self.tabview.add("🛠️ Extra")
        self.tab_logs = self.tabview.add("📋 Istoric")
        
        # Logo și animație în tab-ul principal
        self.setup_logo(self.tab_main)
        
        # Elementele principale în primul tab
        self.setup_main_elements(self.tab_main)
        
        # Funcții extra în al doilea tab
        self.setup_extra_functions(self.tab_extra)
        
        # Istoric și log-uri în al treilea tab
        self.setup_logs(self.tab_logs)
        
        # Footer și theme switch rămân în frame-ul principal
        self.setup_footer(self.main_frame)
        
        # Inițializare
        self.log_action("Aplicație pornită")
        
    def setup_logo(self, parent):
        """Configurare logo și animație"""
        logo_frame = ctk.CTkFrame(parent, fg_color="transparent")
        logo_frame.pack(pady=5)
        
        self.letters_frame = ctk.CTkFrame(logo_frame, fg_color="transparent")
        self.letters_frame.pack()
        
        self.letter_labels = []
        letters = "ALECS"
        for letter in letters:
            label = ctk.CTkLabel(
                self.letters_frame,
                text=letter,
                font=ctk.CTkFont(size=40, weight="bold"),
                text_color="#00FF00"
            )
            label.pack(side="left", padx=1)
            self.letter_labels.append(label)
        
        self.subtitle_label = ctk.CTkLabel(
            logo_frame,
            text="WhatsApp Automation Pro",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("gray70", "gray70")
        )
        self.subtitle_label.pack()
        
        # Pornește animația
        self.animate_logo()
        
    def animate_logo(self):
        # Actualizează culorile pentru fiecare literă
        for i, label in enumerate(self.letter_labels):
            color_index = (self.current_color_index + i * 6) % len(self.pulse_colors)
            label.configure(text_color=self.pulse_colors[color_index])
            
            # Adaugă și efect de rotație pentru fiecare literă
            angle = math.radians(self.rotation_angle + i * 72)
            scale = 1.0 + 0.15 * math.sin(angle)  # Redus efectul de scalare
            font_size = int(35 * scale)  # Micșorat dimensiunea de bază
            label.configure(font=ctk.CTkFont(size=font_size, weight="bold"))
        
        # Actualizează contoarele pentru animație
        self.current_color_index = (self.current_color_index + 1) % len(self.pulse_colors)
        self.rotation_angle = (self.rotation_angle + 5) % 360
        
        # Programează următoarea actualizare
        self.root.after(100, self.animate_logo)  # Actualizează la fiecare 100ms
        
    def setup_main_elements(self, parent):
        """Configurare elemente principale"""
        # Frame pentru elementele principale
        main_elements = ctk.CTkFrame(parent)
        main_elements.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Număr telefon și butoane extra
        phone_frame = ctk.CTkFrame(main_elements)
        phone_frame.pack(fill="x", pady=2)
        
        # Label și entry pentru telefon într-un sub-frame
        phone_input_frame = ctk.CTkFrame(phone_frame)
        phone_input_frame.pack(side="left", fill="x", expand=True)
        
        ctk.CTkLabel(
            phone_input_frame,
            text="📱 Număr telefon:",
            font=ctk.CTkFont(size=12)
        ).pack(anchor="w")
        
        self.phone_entry = ctk.CTkEntry(
            phone_input_frame,
            placeholder_text="+40722123456",
            height=30
        )
        self.phone_entry.pack(fill="x", pady=2)
        
        # Butoane pentru grup și atașamente într-un sub-frame
        buttons_frame = ctk.CTkFrame(phone_frame)
        buttons_frame.pack(side="right", padx=5)
        
        self.group_button = ctk.CTkButton(
            buttons_frame,
            text="👥 Grup",
            command=self.send_to_group,
            width=100,
            height=30,
            font=ctk.CTkFont(size=12)
        )
        self.group_button.pack(pady=2)
        
        self.attach_button = ctk.CTkButton(
            buttons_frame,
            text="📎 Atașează",
            command=self.attach_file,
            width=100,
            height=30,
            font=ctk.CTkFont(size=12)
        )
        self.attach_button.pack(pady=2)
        
        # Label pentru fișier atașat
        self.attached_file_label = ctk.CTkLabel(
            main_elements,
            text="",
            font=ctk.CTkFont(size=10),
            text_color="gray70"
        )
        self.attached_file_label.pack(pady=2)
        
        # Mesaj
        message_frame = ctk.CTkFrame(main_elements)
        message_frame.pack(fill="x", pady=2)
        
        ctk.CTkLabel(
            message_frame,
            text="✉️ Mesaj:",
            font=ctk.CTkFont(size=12)
        ).pack(anchor="w")
        
        self.message_text = ctk.CTkTextbox(
            message_frame,
            height=80
        )
        self.message_text.pack(fill="x", pady=2)
        
        # Timp și repetări
        time_frame = ctk.CTkFrame(main_elements)
        time_frame.pack(fill="x", pady=2)
        
        # Grid pentru ora și minut
        time_grid = ctk.CTkFrame(time_frame)
        time_grid.pack(fill="x")
        
        # Ora
        hour_frame = ctk.CTkFrame(time_grid)
        hour_frame.pack(side="left", fill="x", expand=True, padx=2)
        
        ctk.CTkLabel(
            hour_frame,
            text="⏰ Ora:",
            font=ctk.CTkFont(size=12)
        ).pack(anchor="w")
        
        self.hour_entry = ctk.CTkEntry(
            hour_frame,
            placeholder_text="00-23",
            height=30
        )
        self.hour_entry.pack(fill="x")
        
        # Minut
        minute_frame = ctk.CTkFrame(time_grid)
        minute_frame.pack(side="left", fill="x", expand=True, padx=2)
        
        ctk.CTkLabel(
            minute_frame,
            text="⏰ Minut:",
            font=ctk.CTkFont(size=12)
        ).pack(anchor="w")
        
        self.minute_entry = ctk.CTkEntry(
            minute_frame,
            placeholder_text="00-59",
            height=30
        )
        self.minute_entry.pack(fill="x")
        
        # Repetări și delay
        repeat_frame = ctk.CTkFrame(main_elements)
        repeat_frame.pack(fill="x", pady=2)
        
        ctk.CTkLabel(
            repeat_frame,
            text="🔄 Repetări:",
            font=ctk.CTkFont(size=12)
        ).pack(anchor="w")
        
        self.repeat_entry = ctk.CTkEntry(
            repeat_frame,
            placeholder_text="1-100",
            height=30
        )
        self.repeat_entry.pack(fill="x", pady=2)
        self.repeat_entry.insert(0, "1")
        
        self.delay_var = ctk.BooleanVar(value=False)
        self.delay_checkbox = ctk.CTkCheckBox(
            repeat_frame,
            text="Interval 1 secundă",
            variable=self.delay_var,
            font=ctk.CTkFont(size=12)
        )
        self.delay_checkbox.pack(pady=2)
        
        # Buton trimitere
        self.send_button = ctk.CTkButton(
            main_elements,
            text="🚀 Trimite Mesaj",
            command=self.schedule_message,
            height=35,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.send_button.pack(pady=5)

    def setup_extra_functions(self, parent):
        """Configurare funcții adiționale"""
        extra_frame = ctk.CTkFrame(parent)
        extra_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Grid pentru butoane
        buttons_grid = ctk.CTkFrame(extra_frame)
        buttons_grid.pack(fill="x", pady=5)
        
        # Rând 1
        row1 = ctk.CTkFrame(buttons_grid)
        row1.pack(fill="x", pady=2)
        
        self.templates_button = ctk.CTkButton(
            row1,
            text="📝 Șabloane",
            command=self.manage_templates,
            width=150
        )
        self.templates_button.pack(side="left", padx=2)
        
        self.recurring_button = ctk.CTkButton(
            row1,
            text="🔄 Recurent",
            command=self.set_recurring,
            width=150
        )
        self.recurring_button.pack(side="left", padx=2)
        
        # Rând 2
        row2 = ctk.CTkFrame(buttons_grid)
        row2.pack(fill="x", pady=2)
        
        self.import_contacts_button = ctk.CTkButton(
            row2,
            text="👥 Import CSV",
            command=self.import_contacts,
            width=150
        )
        self.import_contacts_button.pack(side="left", padx=2)
        
        self.settings_button = ctk.CTkButton(
            row2,
            text="⚙️ Setări",
            command=self.manage_settings,
            width=150
        )
        self.settings_button.pack(side="left", padx=2)

    def setup_logs(self, parent):
        """Configurare secțiune de logging"""
        log_frame = ctk.CTkFrame(parent)
        log_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Text box pentru log-uri
        self.log_text = ctk.CTkTextbox(
            log_frame,
            height=300,
            font=ctk.CTkFont(size=12)
        )
        self.log_text.pack(fill="both", expand=True, pady=5)
        
        # Buton curățare
        self.clear_log_button = ctk.CTkButton(
            log_frame,
            text="🗑️ Curăță Istoric",
            command=self.clear_logs,
            height=30
        )
        self.clear_log_button.pack(pady=5)

    def setup_footer(self, parent):
        """Configurare footer și theme switch"""
        footer_frame = ctk.CTkFrame(parent)
        footer_frame.pack(fill="x", pady=5)
        
        # Modificat switch-ul pentru temă
        self.theme_switch = ctk.CTkSwitch(
            footer_frame,
            text="🌙 Mod Întunecat",
            command=self.toggle_theme,
            onvalue="dark",
            offvalue="light",
            button_color=("#00FF00", "#00FF00"),
            button_hover_color=("#00DD00", "#00DD00"),
            progress_color=("#2B2B2B", "#DBDBDB")
        )
        self.theme_switch.pack(side="left", padx=5)
        self.theme_switch.select()  # Implicit mod întunecat
        
        self.footer_label = ctk.CTkLabel(
            footer_frame,
            text="© 2024 ALECS WhatsApp Pro",
            font=ctk.CTkFont(size=10),
            text_color=("gray70", "gray70")
        )
        self.footer_label.pack(side="right", padx=5)

    def toggle_theme(self):
        """Comută între modul întunecat și luminos"""
        if self.theme_switch.get() == "dark":
            ctk.set_appearance_mode("dark")
            # Actualizăm culorile pentru modul întunecat
            self.update_theme_colors("dark")
        else:
            ctk.set_appearance_mode("light")
            # Actualizăm culorile pentru modul luminos
            self.update_theme_colors("light")
            
    def update_theme_colors(self, mode):
        """Actualizează culorile în funcție de temă"""
        if mode == "dark":
            text_color = "gray90"
            bg_color = "gray20"
            button_color = "#00AA00"
            hover_color = "#008800"
        else:
            text_color = "gray10"
            bg_color = "gray90"
            button_color = "#00CC00"
            hover_color = "#00AA00"
            
        # Actualizăm culorile pentru toate elementele relevante
        try:
            # Actualizare butoane
            for button in [self.send_button, self.templates_button, 
                         self.recurring_button, self.import_contacts_button, 
                         self.settings_button, self.clear_log_button]:
                button.configure(
                    fg_color=button_color,
                    hover_color=hover_color,
                    text_color=text_color
                )
            
            # Actualizare text boxes
            self.message_text.configure(text_color=text_color)
            self.log_text.configure(text_color=text_color)
            
            # Actualizare labels
            for label in self.letter_labels:
                if mode == "dark":
                    label.configure(text_color="#00FF00")
                else:
                    label.configure(text_color="#008800")
                    
            self.subtitle_label.configure(
                text_color=("gray70" if mode == "dark" else "gray40")
            )
            
            # Actualizare checkbox
            self.delay_checkbox.configure(
                text_color=text_color,
                fg_color=button_color,
                hover_color=hover_color
            )
            
            # Actualizare status label dacă există
            if hasattr(self, 'status_label'):
                self.status_label.configure(text_color=text_color)
                
        except Exception as e:
            self.log_action(f"Eroare la actualizarea temei: {str(e)}", level="ERROR")
        
    def log_action(self, action, level="INFO", details=None):
        """Înregistrează o acțiune în log și o afișează în interfață"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {action}\n"
        
        if details:
            log_entry += f"Detalii: {json.dumps(details, ensure_ascii=False)}\n"
            
        # Adaugă culoare în funcție de nivel
        if level == "ERROR":
            log_entry = "❌ " + log_entry
        elif level == "WARNING":
            log_entry = "⚠️ " + log_entry
        else:
            log_entry = "✅ " + log_entry
            
        # Adaugă în text box și scroll la ultima linie
        self.log_text.insert("end", log_entry)
        self.log_text.see("end")
        
        # Salvează și în fișier
        logging.info(json.dumps({
            "action": action,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "level": level,
            "details": details or {}
        }, ensure_ascii=False))
        
    def attach_file(self):
        """Atașează un fișier (imagine sau document)"""
        file_path = filedialog.askopenfilename(
            title="Selectează fișier",
            filetypes=[
                ("Toate fișierele suportate", "*.png *.jpg *.jpeg *.gif *.bmp *.pdf *.doc *.docx *.txt"),
                ("Imagini", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("Documente", "*.pdf *.doc *.docx *.txt")
            ]
        )
        if file_path:
            self.attached_image = file_path  # Folosim aceeași variabilă pentru toate tipurile de fișiere
            file_name = os.path.basename(file_path)
            file_ext = os.path.splitext(file_name)[1].lower()
            
            # Determinăm tipul fișierului pentru afișare
            if file_ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']:
                icon = "🖼️"
                type_text = "Imagine"
            else:
                icon = "📄"
                type_text = "Document"
                
            self.attached_file_label.configure(
                text=f"{icon} {type_text} atașat: {file_name}",
                text_color=("#00FF00", "#00FF00")
            )
            self.log_action(f"{type_text} atașat", details={"file": file_name})
            
    def send_to_group(self):
        """Activează modul de trimitere către grup"""
        group_id = messagebox.askstring(
            "ALECS Pro - Grup WhatsApp",
            "Introduceți ID-ul grupului WhatsApp\n(exemplu: AbCdEfGhIjKl):"
        )
        if group_id:
            self.group_id = group_id
            self.phone_entry.configure(state="disabled")
            self.group_button.configure(
                text="❌ Anulează Grup",
                fg_color=("#AA0000", "#AA0000"),
                hover_color=("#880000", "#880000")
            )
            self.attached_file_label.configure(
                text=f"👥 Grup selectat: {group_id}",
                text_color=("#00FF00", "#00FF00")
            )
            self.log_action("Grup selectat", details={"group_id": group_id})
        elif self.group_id:  # Dacă apăsăm butonul când avem deja un grup selectat
            self.group_id = None
            self.phone_entry.configure(state="normal")
            self.group_button.configure(
                text="👥 Grup",
                fg_color=("#1f538d", "#1f538d"),
                hover_color=("#14375e", "#14375e")
            )
            self.attached_file_label.configure(text="")
            self.log_action("Mod grup dezactivat")
            
    def schedule_message(self):
        try:
            message = self.message_text.get("0.0", "end").strip()
            repetitions = int(self.repeat_entry.get())
            use_delay = self.delay_var.get()
            
            if not message:
                messagebox.showerror("ALECS Pro - Eroare", "Introduceți un mesaj!")
                self.log_action("Eroare: mesaj lipsă", level="ERROR")
                return
                
            if not (1 <= repetitions <= 100):
                messagebox.showerror("ALECS Pro - Eroare", "Numărul de repetări trebuie să fie între 1 și 100!")
                self.log_action("Eroare: număr invalid de repetări", level="ERROR")
                return
                
            if not self.group_id and not self.phone_entry.get():
                messagebox.showerror("ALECS Pro - Eroare", "Introduceți un număr de telefon sau selectați un grup!")
                self.log_action("Eroare: destinatar nespecificat", level="ERROR")
                return

            success_count = 0
            total_attempts = repetitions * (len(self.multiple_schedule) if self.multiple_schedule else 1)
            
            # Log începere trimitere
            self.log_action("Începere trimitere mesaje", details={
                "total_attempts": total_attempts,
                "has_attachment": bool(self.attached_image),
                "is_group": bool(self.group_id),
                "use_delay": use_delay
            })
            
            # Procesăm programul multiplu sau ora singulară
            times_to_process = self.multiple_schedule if self.multiple_schedule else [(int(self.hour_entry.get()), int(self.minute_entry.get()))]
            
            for hour, minute in times_to_process:
                for i in range(repetitions):
                    try:
                        if i > 0 and use_delay:
                            minute = (minute * 60 + i) // 60
                            hour = (hour + minute // 60) % 24
                            minute = minute % 60
                        
                        # Trimitere în funcție de tipul mesajului și destinatar
                        if self.attached_image:
                            if self.group_id:
                                pywhatkit.sendwhats_image(self.group_id, self.attached_image, message, wait_time=15 if i == 0 else 2)
                            else:
                                pywhatkit.sendwhats_image(self.phone_entry.get(), self.attached_image, message, wait_time=15 if i == 0 else 2)
                        else:
                            if self.group_id:
                                pywhatkit.sendwhatmsg_to_group(self.group_id, message, hour, minute, wait_time=15 if i == 0 else 2)
                            else:
                                pywhatkit.sendwhatmsg(self.phone_entry.get(), message, hour, minute, wait_time=15 if i == 0 else 2)
                        
                        # Trimite mesajul automat
                        if send_message_automatically():
                            success_count += 1
                            self.log_action(f"Mesaj {success_count} trimis cu succes")
                        else:
                            self.log_action(f"Eroare la trimiterea mesajului {i+1}", level="ERROR")
                        
                        if use_delay and i < repetitions - 1:
                            time.sleep(1)
                            
                    except Exception as e:
                        self.log_action(f"Eroare la mesajul {i+1}: {str(e)}", level="ERROR")
                        continue
            
            # Actualizăm status
            status_text = f"✅ {success_count}/{total_attempts} mesaje programate"
            if self.multiple_schedule:
                times_str = ", ".join([f"{h:02d}:{m:02d}" for h, m in self.multiple_schedule])
                status_text += f"\nProgramate pentru: {times_str}"
            else:
                status_text += f"\nProgramate pentru: {hour:02d}:{minute:02d}"
            
            if self.attached_image:
                status_text += f"\nCu fișier atașat: {os.path.basename(self.attached_image)}"
            if self.group_id:
                status_text += f"\nTrimise în grupul: {self.group_id}"
            if use_delay:
                status_text += "\nCu interval de 1 secundă între mesaje"
                
            self.status_label.configure(
                text=status_text,
                text_color=("#00FF00", "#00FF00")
            )
            messagebox.showinfo("ALECS Pro - Succes", 
                              f"{success_count} din {total_attempts} mesaje au fost programate cu succes!")
            
            # Log finalizare trimitere
            self.log_action("Finalizare trimitere mesaje", details={
                "success_count": success_count,
                "total_attempts": total_attempts
            })
            
        except ValueError as e:
            self.status_label.configure(
                text=f"❌ Eroare: Verificați valorile introduse",
                text_color=("#FF0000", "#FF0000")
            )
            messagebox.showerror("ALECS Pro - Eroare", "Verificați că toate valorile sunt completate corect!")
            self.log_action("Eroare la validare valori", level="ERROR", details={"error": str(e)})
        except Exception as e:
            self.status_label.configure(
                text=f"❌ Eroare: {str(e)}",
                text_color=("#FF0000", "#FF0000")
            )
            messagebox.showerror("ALECS Pro - Eroare", f"A apărut o eroare: {str(e)}")
            self.log_action(f"Eroare la trimitere: {str(e)}", level="ERROR")

    def clear_logs(self):
        """Curăță istoricul din interfață"""
        if messagebox.askyesno("ALECS Pro - Confirmare", "Sigur doriți să ștergeți istoricul?"):
            self.log_text.delete("0.0", "end")
            self.log_action("Istoric curățat")
            
    def manage_templates(self):
        """Gestionează șabloanele de mesaje"""
        template_window = ctk.CTkToplevel(self.root)
        template_window.title("ALECS Pro - Șabloane Mesaje")
        template_window.geometry("400x500")
        
        # Lista de șabloane
        templates_frame = ctk.CTkFrame(template_window)
        templates_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Listbox pentru șabloane
        templates_listbox = ctk.CTkTextbox(templates_frame, height=200)
        templates_listbox.pack(fill="x", pady=5)
        
        # Populăm lista
        for name, content in self.templates.items():
            templates_listbox.insert("end", f"{name}: {content}\n")
        
        # Frame pentru adăugare șablon nou
        add_frame = ctk.CTkFrame(template_window)
        add_frame.pack(fill="x", padx=10, pady=5)
        
        name_entry = ctk.CTkEntry(add_frame, placeholder_text="Nume șablon")
        name_entry.pack(fill="x", pady=5)
        
        content_text = ctk.CTkTextbox(add_frame, height=100)
        content_text.pack(fill="x", pady=5)
        
        def add_template():
            name = name_entry.get().strip()
            content = content_text.get("0.0", "end").strip()
            if name and content:
                self.templates[name] = content
                self.save_templates()
                templates_listbox.insert("end", f"{name}: {content}\n")
                name_entry.delete(0, "end")
                content_text.delete("0.0", "end")
                self.log_action("Șablon adăugat", details={"name": name})
        
        add_button = ctk.CTkButton(
            add_frame,
            text="➕ Adaugă Șablon",
            command=add_template
        )
        add_button.pack(pady=5)
        
    def set_recurring(self):
        """Setează programare recurentă"""
        recurring_window = ctk.CTkToplevel(self.root)
        recurring_window.title("ALECS Pro - Programare Recurentă")
        recurring_window.geometry("400x300")
        
        options_frame = ctk.CTkFrame(recurring_window)
        options_frame.pack(fill="x", padx=10, pady=10)
        
        # Opțiuni pentru recurență
        recurrence_var = ctk.StringVar(value="daily")
        daily_radio = ctk.CTkRadioButton(
            options_frame,
            text="Zilnic",
            variable=recurrence_var,
            value="daily"
        )
        daily_radio.pack(anchor="w", pady=5)
        
        weekly_radio = ctk.CTkRadioButton(
            options_frame,
            text="Săptămânal",
            variable=recurrence_var,
            value="weekly"
        )
        weekly_radio.pack(anchor="w", pady=5)
        
        # Selectare zile pentru programare săptămânală
        days_frame = ctk.CTkFrame(options_frame)
        days_frame.pack(fill="x", pady=5)
        
        days = ["L", "M", "M", "J", "V", "S", "D"]
        day_vars = []
        
        for day in days:
            var = ctk.BooleanVar()
            day_vars.append(var)
            checkbox = ctk.CTkCheckBox(
                days_frame,
                text=day,
                variable=var
            )
            checkbox.pack(side="left", padx=5)
        
        def save_recurring():
            recurrence_type = recurrence_var.get()
            selected_days = [i for i, var in enumerate(day_vars) if var.get()]
            
            self.recurring_schedule = {
                "type": recurrence_type,
                "days": selected_days
            }
            
            self.log_action("Programare recurentă setată", details=self.recurring_schedule)
            recurring_window.destroy()
            
        save_button = ctk.CTkButton(
            options_frame,
            text="💾 Salvează Programare",
            command=save_recurring
        )
        save_button.pack(pady=10)
        
    def import_contacts(self):
        """Importă contacte din CSV"""
        file_path = filedialog.askopenfilename(
            title="Selectează fișierul CSV",
            filetypes=[("CSV files", "*.csv")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    self.contacts = list(reader)
                    
                self.log_action("Contacte importate", details={"count": len(self.contacts)})
                messagebox.showinfo(
                    "ALECS Pro - Import",
                    f"{len(self.contacts)} contacte au fost importate cu succes!"
                )
            except Exception as e:
                self.log_action("Eroare la import contacte", level="ERROR", details={"error": str(e)})
                messagebox.showerror(
                    "ALECS Pro - Eroare",
                    f"Eroare la importul contactelor: {str(e)}"
                )
                
    def manage_settings(self):
        """Gestionează salvarea/încărcarea setărilor"""
        settings_window = ctk.CTkToplevel(self.root)
        settings_window.title("ALECS Pro - Setări")
        settings_window.geometry("300x200")
        
        buttons_frame = ctk.CTkFrame(settings_window)
        buttons_frame.pack(fill="x", padx=10, pady=10)
        
        def save_settings():
            settings = {
                "templates": self.templates,
                "recurring_schedule": self.recurring_schedule,
                "theme": "dark" if self.theme_switch.get() == "dark" else "light"
            }
            
            try:
                with open("settings.pkl", "wb") as f:
                    pickle.dump(settings, f)
                self.log_action("Setări salvate")
                messagebox.showinfo("ALECS Pro - Setări", "Setările au fost salvate cu succes!")
            except Exception as e:
                self.log_action("Eroare la salvare setări", level="ERROR", details={"error": str(e)})
                messagebox.showerror("ALECS Pro - Eroare", f"Eroare la salvarea setărilor: {str(e)}")
        
        def load_settings():
            try:
                with open("settings.pkl", "rb") as f:
                    settings = pickle.load(f)
                    
                self.templates = settings.get("templates", {})
                self.recurring_schedule = settings.get("recurring_schedule", None)
                theme = settings.get("theme", "dark")
                
                if theme == "dark":
                    self.theme_switch.select()
                else:
                    self.theme_switch.deselect()
                
                self.log_action("Setări încărcate")
                messagebox.showinfo("ALECS Pro - Setări", "Setările au fost încărcate cu succes!")
            except Exception as e:
                self.log_action("Eroare la încărcare setări", level="ERROR", details={"error": str(e)})
                messagebox.showerror("ALECS Pro - Eroare", f"Eroare la încărcarea setărilor: {str(e)}")
        
        save_button = ctk.CTkButton(
            buttons_frame,
            text="💾 Salvează Setări",
            command=save_settings
        )
        save_button.pack(pady=5)
        
        load_button = ctk.CTkButton(
            buttons_frame,
            text="📂 Încarcă Setări",
            command=load_settings
        )
        load_button.pack(pady=5)
        
    def load_templates(self):
        """Încarcă șabloanele salvate"""
        try:
            with open("templates.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
            
    def save_templates(self):
        """Salvează șabloanele"""
        try:
            with open("templates.json", "w", encoding="utf-8") as f:
                json.dump(self.templates, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.log_action("Eroare la salvare șabloane", level="ERROR", details={"error": str(e)})

if __name__ == "__main__":
    root = ctk.CTk()
    app = WhatsAppSender(root)
    root.mainloop() 