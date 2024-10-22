import os
import subprocess
import customtkinter as ctk
from tkinter import filedialog, messagebox
from datetime import datetime

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue") 

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("wf-recorder GUI")
        self.geometry("900x400")

        # Output Name
        self.label_output_name = ctk.CTkLabel(self, text="Output Name:")
        self.label_output_name.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.entry_output_name = ctk.CTkEntry(self, width=250)
        self.entry_output_name.grid(row=0, column=1, padx=10, pady=10)

        current_time = datetime.now().strftime("%Y_%m_%d_%H-%M-%S")
        self.entry_output_name.insert(0, current_time)

        # Bitrate
        self.label_bitrate = ctk.CTkLabel(self, text="Bitrate:")
        self.label_bitrate.grid(row=0, column=2, padx=10, pady=10, sticky="w")

        self.spinbox_bitrate = ctk.CTkEntry(self, width=100)
        self.spinbox_bitrate.grid(row=0, column=3, padx=10, pady=10)
        self.spinbox_bitrate.insert(0, "500")  # Default bitrate

        # Output Location
        self.label_output_location = ctk.CTkLabel(self, text="Output location:")
        self.label_output_location.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        self.entry_output_location = ctk.CTkEntry(self, width=250)
        self.entry_output_location.grid(row=1, column=1, padx=10, pady=10)

        home = os.path.expanduser("~")
        self.entry_output_location.insert(0, home)

        self.button_browse = ctk.CTkButton(self, text="Browse", command=self.browse_folder)
        self.button_browse.grid(row=1, column=2, padx=10, pady=10)

        # Format Selection
        self.label_format = ctk.CTkLabel(self, text="Format:")
        self.label_format.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.frame = ctk.CTkFrame(self)
        self.frame.grid(row=2, column=1, padx=10, pady=10, sticky="w")
        self.radio_var = ctk.StringVar(value="MKV")
        self.radio_mkv = ctk.CTkRadioButton(self.frame, text="MKV", variable=self.radio_var, value="MKV")
        self.radio_mp4 = ctk.CTkRadioButton(self.frame, text="MP4", variable=self.radio_var, value="MP4")
        self.radio_webm = ctk.CTkRadioButton(self.frame, text="WEBM", variable=self.radio_var, value="WEBM")
        self.radio_mov = ctk.CTkRadioButton(self.frame, text="MOV", variable=self.radio_var, value="MOV")

        self.radio_mkv.grid(row=2, column=1, padx=0, sticky="w")
        self.radio_mp4.grid(row=2, column=2, padx=0, sticky="w")
        self.radio_webm.grid(row=2, column=3, padx=0, sticky="w")
        self.radio_mov.grid(row=2, column=4, padx=0, sticky="w")


        # Start and Stop Buttons
        self.button_start = ctk.CTkButton(self, text="Start Recording", command=self.start_recording)
        self.button_start.grid(row=3, column=0, padx=10, pady=10)

        self.button_stop = ctk.CTkButton(self, text="Stop Recording", command=self.stop_recording)
        self.button_stop.grid(row=3, column=1, padx=10, pady=10)

        self.recording_process = None 

    def askyesno_custom(self, title, message):
        dialog = ctk.CTkToplevel()
        dialog.title(title)
        dialog.geometry("300x150")
        label = ctk.CTkLabel(dialog, text=message)
        label.pack(pady=20)
        yes_button = ctk.CTkButton(dialog, text="Yes", command=lambda: dialog.destroy())
        no_button = ctk.CTkButton(dialog, text="No", command=lambda: (dialog.destroy(), setattr(dialog, 'result', False)))
        yes_button.pack(side="left", padx=20, pady=20)
        no_button.pack(side="right", padx=20, pady=20)
        dialog.result = True  
        dialog.grab_set()  
        dialog.wait_window()  
        return dialog.result


    def showerror_custom(self, title, message):
        dialog = ctk.CTkToplevel()
        dialog.title(title)
        dialog.geometry("300x150")
        label = ctk.CTkLabel(dialog, text=message)
        label.pack(pady=20)
        ok_button = ctk.CTkButton(dialog, text="OK", command=dialog.destroy)
        ok_button.pack(pady=20)
        dialog.grab_set()
        dialog.wait_window()


    def showinfo_custom(self, title, message):
        dialog = ctk.CTkToplevel()
        dialog.title(title)
        dialog.geometry("300x150")
        label = ctk.CTkLabel(dialog, text=message)
        label.pack(pady=20)
        ok_button = ctk.CTkButton(dialog, text="OK", command=dialog.destroy)
        ok_button.pack(pady=20)
        dialog.grab_set()
        dialog.wait_window()

    def browse_folder(self):
        folder = filedialog.askdirectory(title="Select Output Directory")
        if folder:
            self.entry_output_location.delete(0, "end")
            self.entry_output_location.insert(0, folder)

    def start_recording(self):
        output_name = self.entry_output_name.get().strip()
        output_location = self.entry_output_location.get().strip()
        bitrate = f"{self.spinbox_bitrate.get()}k"
        selected_format = self.radio_var.get()

        if not output_name or not output_location or not selected_format:
            self.showerror_custom("Error", "Please fill all fields.")
            return

        output_file = f"{output_location}/{output_name}.{selected_format.lower()}"
        if os.path.exists(output_file):
            overwrite = self.askyesno_custom("File Exists", f"The file '{output_file}' already exists. Do you want to overwrite it?")
            if not overwrite:
                return
            else:
                try:
                    os.remove(output_file)
                except Exception as e:
                    self.showerror_custom("Error", f"Failed to delete the existing file: {str(e)}")
                    return

        process_data(output_name, output_location, selected_format, bitrate)
        self.showinfo_custom("Recording", "Recording has started.")

        command = f"wf-recorder -f {output_file} -t {selected_format} --bitrate {bitrate}"
        self.recording_process = subprocess.Popen(command, shell=True)

    def stop_recording(self):
        if self.recording_process:
            self.recording_process.terminate()
            self.recording_process = None
            self.showinfo_custom("Recording", "Recording has stopped.")

def process_data(output_name, output_location, selected_format, bitrate):
    print(f"Output Name: {output_name}")
    print(f"Output Location: {output_location}")
    print(f"Selected Format: {selected_format}")
    print(f"Bitrate: {bitrate}")

if __name__ == "__main__":
    app = App()
    app.mainloop()
