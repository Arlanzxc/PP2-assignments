import pygame
import os

class MusicPlayer:


    def __init__(self):
        music_folder = "music"
        pygame.mixer.init()
        self.tracks = []
        #collect all exsisted tracks from folder music
        for file in sorted(os.listdir(music_folder)):
            if file.endswith((".wav", ".mp3")):
                self.tracks.append(os.path.join(music_folder, file))
        #Error handler
        if not self.tracks:
            print("No music files found in music folder!")
        self.current_index = 0
        self.is_playing = False

    def play(self):
        pygame.mixer.music.load(self.tracks[self.current_index])
        pygame.mixer.music.play()
        self.is_playing = True
    def stop(self):
        pygame.mixer.music.stop()
        self.is_playing = False
    def next(self):
        self.current_index = (self.current_index+1) % len(self.tracks)
        self.play()
    def previous(self):
        self.current_index = (self.current_index - 1) % len(self.tracks)
        self.play()
    def get_current_track(self):
        return os.path.basename(self.tracks[self.current_index])
    def get_position(self):
        return pygame.mixer.music.get_pos()