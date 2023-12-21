import json
import os
import logging

from tkinter import filedialog, messagebox
from pytube import YouTube
from moviepy.editor import VideoFileClip

import customtkinter as ctk

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_config():
	"""Load configuration from file, or create default config if not present."""
	default_config = {
		'default_output_folder': os.path.expanduser('~') + '\\Videos\\YouTube',
		'theme': 'dark',
		'color_theme': 'dark-blue'
	}
	try:
		with open("config.json", "r") as config_file:
			config = json.load(config_file)
	except FileNotFoundError or json.JSONDecodeError:
		logging.warning("Config file not found or corrupted, creating default config.")
		with open("config.json", "w") as config_file:
			json.dump(default_config, config_file, indent=4)
		config = default_config
	return config


# Set appearance mode based on the configuration
def set_appearance(config):
	ctk.set_appearance_mode(config['theme'])
	ctk.set_default_color_theme(config['color_theme'])


# Prompt the user to select an output folder and update the configuration
def set_output_folder(config):
	output_folder = filedialog.askdirectory()
	if output_folder:
		config["default_output_folder"] = output_folder
		with open("config.json", "w") as config_file:
			json.dump(config, config_file, indent=4)
		label_output_folder.configure(text="Save folder: " + output_folder)
		logging.info("Output folder set to: " + output_folder)


def download_video(url, formats, output_folder):
	try:
		youtube_object = YouTube(url)
		logging.info(f"Requesting video: {youtube_object.title} as {formats} in {output_folder}")
		# Filter and select the best progressive video stream
		video_stream = youtube_object.streams.filter(progressive=True, file_extension="mp4").get_highest_resolution()
		if video_stream:
			video_path = video_stream.download(output_folder)
			logging.info("Video successfully downloaded as " + video_path)
			if formats:
				convert_file(youtube_object, formats, video_path, output_folder)
		else:
			logging.error("No suitable video stream found.")
	except Exception as e:
		logging.error(f"Error downloading the video: {e}")


# Convert the downloaded video to the specified formats
def convert_file(youtube_object, formats, video_path, output_folder):
	for format in formats:
		audio_path = os.path.join(output_folder, youtube_object.title + f".{format}")
		try:
			with VideoFileClip(video_path) as video_clip:
				audio_file = video_clip.audio
				audio_file.write_audiofile(audio_path)
			logging.info("Video successfully converted as " + audio_path)
		except Exception as e:
			logging.error(f"Error converting to {format}: {e}")


# Get the YouTube URL and selected formats, then initiate the download
def on_download():
	url = entry_youtube_url.get()
	formats = []
	if checkbox_mp3.get():
		formats.append("mp3")
	if checkbox_wav.get():
		formats.append("wav")
	if url:
		download_video(url, formats, config["default_output_folder"])
	else:
		messagebox.showwarning("Warning", "Please enter a valid YouTube URL.")



# Create the GUI
config = load_config()
set_appearance(config)

root = ctk.CTk()
root.geometry("500x400")

frame = ctk.CTkFrame(master=root)
frame.pack(pady=20, padx=30, fill="both", expand=True)

label_title = ctk.CTkLabel(master=frame, text="Simple YouTube Downloader", font=("Roboto", 24))
label_title.pack(pady=10, padx=10)

entry_youtube_url = ctk.CTkEntry(master=frame, placeholder_text="YouTube video URL", width=300)
entry_youtube_url.pack()

checkbox_mp3 = ctk.CTkCheckBox(master=frame, text="MP3")
checkbox_wav = ctk.CTkCheckBox(master=frame, text="WAV")
checkbox_mp3.pack(pady=10, padx=10)
checkbox_wav.pack(pady=10, padx=10)

label_output_folder = ctk.CTkLabel(master=frame, text="Save folder: " + config["default_output_folder"],
								   font=("Roboto", 12))
label_output_folder.pack()

button_browse_output_folder = ctk.CTkButton(master=frame, text="Change output folder",
											command=lambda: set_output_folder(config))
button_browse_output_folder.pack(pady=10, padx=10)

button = ctk.CTkButton(master=frame, text="Download", command=on_download)
button.pack(pady=10, padx=10)


if __name__ == "__main__":
	root.mainloop()
