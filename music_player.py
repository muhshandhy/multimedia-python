"""
Proyek Mini: Aplikasi Pemutar Musik Sederhana
==============================================
Integrasi konsep dari:
- Chapter 1: Penggunaan pustaka multimedia Python
- Chapter 2: Manipulasi audio dengan Pydub (AudioSegment, volume dB)
- Chapter 3: Pembuatan GUI dengan Tkinter (widget, layout, event)
- Chapter 4: Penggabungan seluruh konsep dalam satu aplikasi

Dependensi:
    pip install pydub
    (ffmpeg harus terinstal di sistem untuk dukungan format mp3)
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import threading
from pydub import AudioSegment
from pydub.playback import play

# ============================================================
# Variabel global untuk menyimpan state aplikasi
# ============================================================
audio_segment = None       # Objek AudioSegment dari file yang dimuat
current_file_name = None   # Nama file yang sedang dimuat
is_playing = False         # Flag untuk menandai apakah audio sedang diputar
play_thread = None         # Thread terpisah untuk playback agar GUI tidak freeze


# ============================================================
# Fungsi load_file()
# - Membuka dialog pemilihan file (mp3/wav)
# - Memuat file sebagai AudioSegment
# - Memperbarui label nama file di GUI
# ============================================================
def load_file():
    global audio_segment, current_file_name

    # Buka file dialog, filter hanya mp3 dan wav
    file_path = filedialog.askopenfilename(
        title="Pilih File Audio",
        filetypes=[
            ("Audio Files", "*.mp3 *.wav"),
            ("MP3 Files", "*.mp3"),
            ("WAV Files", "*.wav"),
        ]
    )

    # Jika user membatalkan dialog, file_path akan kosong
    if not file_path:
        return

    try:
        # Memuat file audio sebagai objek AudioSegment (konsep Chapter 2)
        audio_segment = AudioSegment.from_file(file_path)

        # Simpan nama file (tanpa path lengkap) untuk ditampilkan
        current_file_name = file_path.split("/")[-1].split("\\")[-1]
        label_file_name.config(text=f"File: {current_file_name}")

        # Reset slider volume ke posisi tengah (0 dB = volume asli)
        volume_slider.set(0)
    except Exception as e:
        messagebox.showerror("Error", f"Gagal memuat file:\n{e}")


# ============================================================
# Fungsi play_audio()
# - Menerapkan perubahan volume (dB) dari slider ke AudioSegment
# - Memutar audio di thread terpisah agar GUI tetap responsif
# ============================================================
def play_audio():
    global is_playing, play_thread

    # Validasi: pastikan file sudah dimuat sebelum memutar
    if audio_segment is None:
        messagebox.showwarning("Peringatan", "Belum ada file yang dimuat!\nKlik 'Load File' terlebih dahulu.")
        return

    # Jika sudah ada audio yang sedang diputar, hentikan dulu
    if is_playing:
        stop_audio()

    # Ambil nilai volume dari slider dan terapkan ke audio (konsep Chapter 2: operasi dB)
    volume_db = volume_slider.get()
    adjusted_audio = audio_segment + volume_db  # Pydub: tambah/kurang dB

    # Set flag playing
    is_playing = True
    label_status.config(text="Status: Sedang Memutar...")

    # Jalankan playback di thread terpisah agar GUI tidak freeze (konsep threading)
    play_thread = threading.Thread(target=_play_in_thread, args=(adjusted_audio,), daemon=True)
    play_thread.start()


def _play_in_thread(audio):
    """Fungsi internal yang dijalankan di thread terpisah untuk memutar audio."""
    global is_playing
    try:
        play(audio)
    except Exception:
        pass  # Playback dihentikan atau terjadi error
    finally:
        # Setelah selesai memutar, update status di GUI thread
        is_playing = False
        root.after(0, lambda: label_status.config(text="Status: Selesai"))


# ============================================================
# Fungsi stop_audio()
# - Menghentikan playback audio yang sedang berjalan
# - Menggunakan pendekatan membunuh proses ffplay yang dibuat pydub
# ============================================================
def stop_audio():
    global is_playing

    if not is_playing:
        return

    is_playing = False
    label_status.config(text="Status: Dihentikan")

    # pydub.playback.play() menggunakan subprocess (ffplay/avplay),
    # kita hentikan melalui modul internal pydub
    try:
        import subprocess
        import signal
        import os

        # Cari dan hentikan proses ffplay/avplay yang sedang berjalan
        if os.name == "nt":  # Windows
            os.system("taskkill /f /im ffplay.exe >nul 2>&1")
        else:  # Linux/macOS
            os.system("pkill -f ffplay 2>/dev/null")
    except Exception:
        pass


# ============================================================
# Fungsi update_volume()
# - Dipanggil setiap kali slider volume digeser
# - Memperbarui label yang menampilkan nilai dB saat ini
# ============================================================
def update_volume(value):
    db_value = int(float(value))
    label_volume_value.config(text=f"{db_value:+d} dB")


# ============================================================
# Pembuatan GUI dengan Tkinter (konsep Chapter 3)
# ============================================================

# Jendela utama
root = tk.Tk()
root.title("Pemutar Musik Sederhana")
root.geometry("420x320")
root.resizable(False, False)
root.configure(bg="#2b2b2b")

# -- Styling umum --
FONT_TITLE = ("Helvetica", 16, "bold")
FONT_NORMAL = ("Helvetica", 11)
FONT_SMALL = ("Helvetica", 9)
BG_COLOR = "#2b2b2b"
FG_COLOR = "#e0e0e0"
BTN_BG = "#3c3f41"
BTN_FG = "#e0e0e0"
BTN_ACTIVE_BG = "#505356"

# -- Judul aplikasi --
label_title = tk.Label(
    root, text="Pemutar Musik", font=FONT_TITLE,
    bg=BG_COLOR, fg="#61afef"
)
label_title.pack(pady=(18, 4))

# -- Label nama file yang dimuat --
label_file_name = tk.Label(
    root, text="File: Belum ada file dipilih",
    font=FONT_NORMAL, bg=BG_COLOR, fg=FG_COLOR, wraplength=380
)
label_file_name.pack(pady=(4, 8))

# -- Frame untuk tombol-tombol kontrol --
frame_buttons = tk.Frame(root, bg=BG_COLOR)
frame_buttons.pack(pady=8)

btn_load = tk.Button(
    frame_buttons, text="Load File", command=load_file, width=10,
    font=FONT_NORMAL, bg=BTN_BG, fg=BTN_FG, activebackground=BTN_ACTIVE_BG,
    relief="flat", cursor="hand2"
)
btn_load.grid(row=0, column=0, padx=6)

btn_play = tk.Button(
    frame_buttons, text="Play", command=play_audio, width=10,
    font=FONT_NORMAL, bg="#2e7d32", fg="white", activebackground="#388e3c",
    relief="flat", cursor="hand2"
)
btn_play.grid(row=0, column=1, padx=6)

btn_stop = tk.Button(
    frame_buttons, text="Stop", command=stop_audio, width=10,
    font=FONT_NORMAL, bg="#c62828", fg="white", activebackground="#d32f2f",
    relief="flat", cursor="hand2"
)
btn_stop.grid(row=0, column=2, padx=6)

# -- Frame untuk kontrol volume --
frame_volume = tk.Frame(root, bg=BG_COLOR)
frame_volume.pack(pady=(14, 4))

label_volume = tk.Label(
    frame_volume, text="Volume:", font=FONT_NORMAL,
    bg=BG_COLOR, fg=FG_COLOR
)
label_volume.grid(row=0, column=0, padx=(0, 8))

# Slider volume: range -20 dB sampai +10 dB, default 0 dB (volume asli)
volume_slider = tk.Scale(
    frame_volume, from_=-20, to=10, orient=tk.HORIZONTAL,
    length=220, command=update_volume,
    bg=BG_COLOR, fg=FG_COLOR, troughcolor="#3c3f41",
    highlightthickness=0, showvalue=False
)
volume_slider.set(0)
volume_slider.grid(row=0, column=1)

label_volume_value = tk.Label(
    frame_volume, text="+0 dB", font=FONT_NORMAL, width=7,
    bg=BG_COLOR, fg="#e5c07b"
)
label_volume_value.grid(row=0, column=2, padx=(8, 0))

# -- Label status playback --
label_status = tk.Label(
    root, text="Status: Siap", font=FONT_SMALL,
    bg=BG_COLOR, fg="#98c379"
)
label_status.pack(pady=(14, 4))

# -- Label informasi --
label_info = tk.Label(
    root, text="Mendukung format: MP3, WAV",
    font=FONT_SMALL, bg=BG_COLOR, fg="#5c6370"
)
label_info.pack(pady=(2, 0))

# ============================================================
# Menjalankan loop utama Tkinter
# ============================================================
if __name__ == "__main__":
    root.mainloop()
