import customtkinter as ctk
from tkinter import filedialog
import os
import threading
import subprocess
import time

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class FuturisticDownloader(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("YT MP3 Futuristlik Konverter")
        self.geometry("700x400")

        # Faili salvestamise kaust
        self.output_dir = os.path.join(os.getcwd(), "downloads")
        os.makedirs(self.output_dir, exist_ok=True)

        # Glow-effect Title
        self.title_label = ctk.CTkLabel(self, text="🔊 YT ➤ MP3/Video Konverter", font=("Orbitron", 24, "bold"), text_color="#00ffff")
        self.title_label.pack(pady=20)

        # Sisestusväli
        self.url_entry = ctk.CTkEntry(self, placeholder_text="📺 Sisesta YouTube'i URL siia", width=450)
        self.url_entry.pack(pady=10)

        # Vali kaust nupp
        self.browse_button = ctk.CTkButton(self, text="📁 Vali sihtkaust", command=self.choose_output_dir)
        self.browse_button.pack(pady=5)

        # Valik audio või video
        self.download_type_var = ctk.StringVar(value="audio")  # default is audio
        self.audio_radio_button = ctk.CTkRadioButton(self, text="Audio", variable=self.download_type_var, value="audio", command=self.update_options)
        self.audio_radio_button.pack(pady=5)
        self.video_radio_button = ctk.CTkRadioButton(self, text="Video", variable=self.download_type_var, value="video", command=self.update_options)
        self.video_radio_button.pack(pady=5)

        # Formaadi valikud (audio jaoks)
        self.format_label = ctk.CTkLabel(self, text="Vali formaat:", text_color="white")
        self.format_label.pack(pady=10)

        self.format_options = ctk.CTkOptionMenu(self, values=["mp3", "webm", "wav", "flac"], width=300)
        self.format_options.set("mp3")  # default to mp3
        self.format_options.pack(pady=5)

        # Video kvaliteedi valikud (video jaoks)
        self.quality_label = ctk.CTkLabel(self, text="Vali video kvaliteet:", text_color="white")
        self.quality_label.pack(pady=10)

        self.quality_options = ctk.CTkOptionMenu(self, values=["1440p", "1080p", "720p", "480p", "360p", "144p"], width=300)
        self.quality_options.set("1080p")  # default to 1080p
        self.quality_options.pack(pady=5)

        # Lae alla ja konverteeri nupp
        self.download_button = ctk.CTkButton(self, text="▼ Lae alla ja konverteeri", command=self.start_download_thread, fg_color="#00ffff", hover_color="#00ccff")
        self.download_button.pack(pady=20)

        # Teade
        self.status_label = ctk.CTkLabel(self, text="", text_color="white", font=("Consolas", 14))
        self.status_label.pack()

        # Käivita animatsioon
        self.animate_button_glow()

        # Algselt peidetakse kvaliteedi valik audio jaoks ja formaadi valik video jaoks
        self.update_options()

    def choose_output_dir(self):
        directory = filedialog.askdirectory()
        if directory:
            self.output_dir = directory
            self.status_label.configure(text=f"✅ Salvestuskaust valitud: {self.output_dir}", text_color="#00ff99")

    def update_options(self):
        # Kui valitakse video, siis peidetakse formaadi valik ja kuvatakse kvaliteedi valik
        download_type = self.download_type_var.get()
        if download_type == "audio":
            self.format_label.pack(pady=10)
            self.format_options.pack(pady=5)
            self.quality_label.pack_forget()
            self.quality_options.pack_forget()
        elif download_type == "video":
            self.quality_label.pack(pady=10)
            self.quality_options.pack(pady=5)
            self.format_label.pack_forget()
            self.format_options.pack_forget()

    def start_download_thread(self):
        threading.Thread(target=self.download_video, daemon=True).start()

    def download_video(self):
        url = self.url_entry.get()
        if not url.strip():
            self.status_label.configure(text="⚠️ Palun sisesta URL!", text_color="#ff4444")
            return

        download_type = self.download_type_var.get()
        format_choice = self.format_options.get()
        quality_choice = self.quality_options.get()

        self.status_label.configure(text="⏳ Allalaadimine ja konverteerimine käib...", text_color="#ffff00")

        if download_type == "audio":
            self.download_audio(url, format_choice)
        elif download_type == "video":
            self.download_video_with_quality(url, quality_choice)

    def download_audio(self, url, format_choice):
        try:
            command = [
                "yt-dlp",
                "-f", "bestaudio",
                "--extract-audio",
                f"--audio-format={format_choice}",
                "-o", os.path.join(self.output_dir, "%(title)s.%(ext)s"),
                url
            ]
            subprocess.run(command, check=True)
            self.status_label.configure(text="✅ Audio edukalt alla laetud ja konverteeritud!", text_color="#00ff00")
        except subprocess.CalledProcessError as e:
            self.status_label.configure(text=f"❌ Viga: Valitud formaat ei ole saadaval. Proovi mõnda muud formaati.", text_color="#ff4444")

    def download_video_with_quality(self, url, quality_choice):
        try:
            # Kõigepealt kontrolli, kas valitud kvaliteet on saadaval
            available_formats_command = ["yt-dlp", "-F", url]
            result = subprocess.run(available_formats_command, capture_output=True, text=True)
            available_formats = result.stdout

            # Kui kvaliteet on saadaval, siis laadige vastav formaat
            format_choice = None
            for line in available_formats.splitlines():
                if quality_choice in line:
                    format_choice = line.split()[0]  # võtab formaadi ID
                    break

            if not format_choice:
                self.status_label.configure(text="❌ Viga: Valitud kvaliteet ei ole saadaval. Valin parima kvaliteedi.", text_color="#ff4444")
                format_choice = "bestvideo+bestaudio"

            # Laadi video alla
            command = [
                "yt-dlp",
                "-f", format_choice,
                "-o", os.path.join(self.output_dir, "downloaded_video.mp4"),  # Määrame kindla nime "downloaded_video.mp4"
                url
            ]
            subprocess.run(command, check=True)

            # Kasutame ffmpeg konverteerimist, et muuta video sobivaks
            video_path = os.path.join(self.output_dir, "downloaded_video.mp4")  # Laaditud video asukoht
            converted_path = os.path.join(self.output_dir, "downloaded_video_converted.mp4")  # Muudetud video asukoht

            ffmpeg_command = [
                "ffmpeg", "-i", video_path, "-c:v", "libx264", "-c:a", "aac", "-strict", "experimental", converted_path
            ]
            subprocess.run(ffmpeg_command, check=True)

            self.status_label.configure(text="✅ Video edukalt alla laetud ja konverteeritud!", text_color="#00ff00")
        except subprocess.CalledProcessError as e:
            self.status_label.configure(text=f"❌ Viga: Midagi läks valesti. Palun proovi hiljem.", text_color="#ff4444")

    def animate_button_glow(self):
        def pulse():
            color_index = 0
            colors = ["#00ffff", "#00ccff", "#0099ff", "#00ccff"]
            while True:
                new_color = colors[color_index % len(colors)]
                self.download_button.configure(fg_color=new_color)
                color_index += 1
                time.sleep(0.6)

        threading.Thread(target=pulse, daemon=True).start()

if __name__ == "__main__":
    app = FuturisticDownloader()
    app.mainloop()
