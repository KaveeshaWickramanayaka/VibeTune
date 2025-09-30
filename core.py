import os
import json
import time
import pygame
import threading
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Callable

@dataclass
class Song:
    title: str
    artist: str
    mood: str
    duration: float
    filepath: Optional[str] = None

    def to_dict(self):
        return self.__dict__

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class Node:
    def __init__(self, data: Song):
        self.data = data
        self.next: Optional["Node"] = None

class LinkedList:
    def __init__(self):
        self.head: Optional[Node] = None
        self.size = 0

    def append(self, song: Song):
        new_node = Node(song)
        if not self.head:
            self.head = new_node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node
        self.size += 1

    def to_list(self) -> List[Song]:
        songs = []
        current = self.head
        while current:
            songs.append(current.data)
            current = current.next
        return songs

    def __iter__(self):
        current = self.head
        while current:
            yield current.data
            current = current.next

    def __len__(self):
        return self.size

@dataclass
class Playlist:
    name: str
    songs: LinkedList = field(default_factory=LinkedList)

    def to_dict(self):
        return {"name": self.name, "songs": [s.to_dict() for s in self.songs]}

    @classmethod
    def from_dict(cls, data):
        playlist = cls(name=data["name"])
        for s_data in data.get("songs", []):
            playlist.songs.append(Song.from_dict(s_data))
        return playlist

class MusicPlayer:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.music_library: List[Song] = []
        self.playlists: Dict[str, Playlist] = {}
        self.current_song_list: List[Song] = []
        self.current_song_index: int = -1
        self.is_playing: bool = False
        self._load_default_library()
        self._load_playlists()

    def _load_default_library(self):
        default_songs = [
            {"title": "Happy", "artist": "Pharrell Williams", "mood": "Happy", "duration": 233},
            {"title": "Walking on Sunshine", "artist": "Katrina & The Waves", "mood": "Happy", "duration": 238},
            {"title": "Uptown Funk", "artist": "Mark Ronson ft. Bruno Mars", "mood": "Happy", "duration": 270},
            {"title": "Blinding Lights", "artist": "The Weeknd", "mood": "Energetic", "duration": 200},
            {"title": "Don't Stop Me Now", "artist": "Queen", "mood": "Energetic", "duration": 209},
            {"title": "Eye of the Tiger", "artist": "Survivor", "mood": "Energetic", "duration": 245},
            {"title": "Someone Like You", "artist": "Adele", "mood": "Sad", "duration": 285},
            {"title": "Hallelujah", "artist": "Jeff Buckley", "mood": "Sad", "duration": 415},
            {"title": "Fix You", "artist": "Coldplay", "mood": "Sad", "duration": 295},
            {"title": "Weightless", "artist": "Marconi Union", "mood": "Calm", "duration": 488},
            {"title": "Clair de Lune", "artist": "Claude Debussy", "mood": "Calm", "duration": 303},
            {"title": "Orinoco Flow", "artist": "Enya", "mood": "Calm", "duration": 266},
        ]
        self.music_library = [Song(**s) for s in default_songs]

    def _load_playlists(self):
        if os.path.exists("playlists.json"):
            try:
                with open("playlists.json", "r") as f:
                    playlists_data = json.load(f)
                    for p_data in playlists_data:
                        playlist = Playlist.from_dict(p_data)
                        self.playlists[playlist.name] = playlist
            except (json.JSONDecodeError, TypeError):
                self.playlists = {}

    def save_playlists(self):
        with open("playlists.json", "w") as f:
            json.dump([p.to_dict() for p in self.playlists.values()], f, indent=4)

    def add_song_from_file(self, filepath: str, title: str, artist: str, mood: str):
        try:
            sound = pygame.mixer.Sound(filepath)
            duration = sound.get_length()
            song = Song(title=title, artist=artist, mood=mood, duration=duration, filepath=filepath)
            self.music_library.append(song)
            return song
        except pygame.error as e:
            print(f"Error loading song from file: {e}")
            return None

    def create_playlist(self, name: str) -> bool:
        if name and name not in self.playlists:
            self.playlists[name] = Playlist(name=name)
            self.save_playlists()
            return True
        return False

    def delete_playlist(self, name: str):
        if name in self.playlists:
            del self.playlists[name]
            self.save_playlists()

    def add_song_to_playlist(self, playlist_name: str, song: Song) -> bool:
        if playlist_name in self.playlists:
            playlist = self.playlists[playlist_name]
            if not any(s.filepath == song.filepath for s in playlist.songs if s.filepath and song.filepath):
                playlist.songs.append(song)
                self.save_playlists()
                return True
        return False

    def get_songs_by_mood(self, mood: str) -> List[Song]:
        if mood == "All":
            return self.music_library[:]
        return [song for song in self.music_library if song.mood == mood]

    def play_song(self, song_list: List[Song], song_index: int):
        self.current_song_list = song_list
        self.current_song_index = song_index
        song = self.get_current_song()
        pygame.mixer.music.stop()
        if song and song.filepath and os.path.exists(song.filepath):
            try:
                pygame.mixer.music.load(song.filepath)
                pygame.mixer.music.play()
                self.is_playing = True
            except pygame.error as e:
                print(f"Error playing file {song.filepath}: {e}")
                self.is_playing = False
        elif song:
            print(f"Playing (dummy track): {song.title}")
            self.is_playing = True
        else:
            self.is_playing = False

    def get_current_song(self) -> Optional[Song]:
        if self.current_song_list and 0 <= self.current_song_index < len(self.current_song_list):
            return self.current_song_list[self.current_song_index]
        return None

    def toggle_play_pause(self):
        song = self.get_current_song()
        if not song:
            return
        if song.filepath and os.path.exists(song.filepath):
            if self.is_playing:
                if pygame.mixer.music.get_busy():
                    pygame.mixer.music.pause()
            else:
                pygame.mixer.music.unpause()
        self.is_playing = not self.is_playing

    def next_song(self):
        if self.current_song_list:
            next_index = (self.current_song_index + 1) % len(self.current_song_list)
            self.play_song(self.current_song_list, next_index)

    def prev_song(self):
        if self.current_song_list:
            prev_index = (self.current_song_index - 1 + len(self.current_song_list)) % len(self.current_song_list)
            self.play_song(self.current_song_list, prev_index)

    def set_volume(self, volume_level):
        pygame.mixer.music.set_volume(float(volume_level))

    def get_playback_position(self):
        song = self.get_current_song()
        if song and song.filepath and os.path.exists(song.filepath) and pygame.mixer.music.get_busy():
            return pygame.mixer.music.get_pos() / 1000, song.duration
        return 0, song.duration if song else 0

class SortingManager:
    def __init__(self, update_callback: Callable, stats_callback: Callable, finished_callback: Callable):
        self.update_callback = update_callback
        self.stats_callback = stats_callback
        self.finished_callback = finished_callback
        self.is_sorting = False
        self.comparisons = 0
        self.swaps = 0
        self.delay = 0.1

    def sort_in_thread(self, algorithm: str, songs_source):
        if isinstance(songs_source, list):
            linked = LinkedList()
            for song in songs_source:
                linked.append(song)
            songs = linked
        else:
            songs = songs_source
        if self.is_sorting:
            return
        self.is_sorting = True
        self.comparisons = 0
        self.swaps = 0
        thread = threading.Thread(target=self._run_sort, args=(algorithm, songs))
        thread.daemon = True
        thread.start()

    def _run_sort(self, algorithm: str, songs: LinkedList):
        sorter = getattr(self, f"_{algorithm.lower().replace(' ', '_')}")
        sorter(songs)
        self.update_callback(songs.to_list(), {})
        self.is_sorting = False
        self.finished_callback()

    def _bubble_sort(self, songs: LinkedList):
        if not songs.head or not songs.head.next:
            return
        end = None
        while end != songs.head:
            swapped = False
            current = songs.head
            while current.next != end:
                if not self.is_sorting:
                    return
                self.comparisons += 1
                self.stats_callback(self.comparisons, self.swaps)
                self.update_callback(songs.to_list(), {"compare": [current.data.title, current.next.data.title]})
                time.sleep(self.delay)
                if current.data.title.lower() > current.next.data.title.lower():
                    current.data, current.next.data = current.next.data, current.data
                    self.swaps += 1
                    self.update_callback(songs.to_list(), {"swap": [current.data.title, current.next.data.title]})
                    time.sleep(self.delay)
                    swapped = True
                current = current.next
            if not swapped:
                break
            end = current

    def _selection_sort(self, songs: LinkedList):
        start = songs.head
        while start:
            min_node = start
            current = start.next
            while current:
                if not self.is_sorting:
                    return
                self.comparisons += 1
                self.stats_callback(self.comparisons, self.swaps)
                self.update_callback(songs.to_list(), {"compare": [current.data.title, min_node.data.title]})
                time.sleep(self.delay)
                if current.data.title.lower() < min_node.data.title.lower():
                    min_node = current
                current = current.next
            if min_node != start:
                start.data, min_node.data = min_node.data, start.data
                self.swaps += 1
                self.update_callback(songs.to_list(), {"swap": [start.data.title, min_node.data.title]})
                time.sleep(self.delay)
            start = start.next

    def _insertion_sort(self, songs: LinkedList):
        if not songs.head or not songs.head.next:
            return
        sorted_head = songs.head
        current = sorted_head.next
        sorted_head.next = None
        while current:
            if not self.is_sorting:
                return
            key_node = current
            current = current.next
            if key_node.data.title.lower() < sorted_head.data.title.lower():
                key_node.next = sorted_head
                sorted_head = key_node
            else:
                search = sorted_head
                while search.next and search.next.data.title.lower() < key_node.data.title.lower():
                    self.comparisons += 1
                    self.stats_callback(self.comparisons, self.swaps)
                    self.update_callback(songs.to_list(), {"compare": [key_node.data.title, search.next.data.title]})
                    time.sleep(self.delay)
                    search = search.next
                key_node.next = search.next
                search.next = key_node
            songs.head = sorted_head
            self.update_callback(songs.to_list(), {})
            time.sleep(self.delay)
