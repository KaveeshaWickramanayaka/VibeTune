import os
import json
import time
import pygame
import threading
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Callable

class Node:
    def __init__(self, data=None):
        self.data = data
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None
        self.size = 0

    def append(self, data):
        new_node = Node(data)
        if not self.head:
            self.head = new_node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node
        self.size += 1

    def get(self, index):
        if index < 0 or index >= self.size:
            return None
        current = self.head
        for _ in range(index):
            current = current.next
        return current.data

    def to_python_list(self):
        py_list = []
        current = self.head
        while current:
            py_list.append(current.data)
            current = current.next
        return py_list

    def __iter__(self):
        current = self.head
        while current:
            yield current.data
            current = current.next

    def __len__(self):
        return self.size

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

@dataclass
class Playlist:

    name: str
    songs: LinkedList = field(default_factory=LinkedList)

    def to_dict(self):
        return {'name': self.name, 'songs': [s.to_dict() for s in self.songs]}

    @classmethod
    def from_dict(cls, data):
        playlist = cls(name=data['name'])
        for s_data in data.get('songs', []):
            playlist.songs.append(Song.from_dict(s_data))
        return playlist

class Graph:
    def __init__(self):
        self.adjacency_list = {}

    def add_node(self, song: Song):
        if song.title not in self.adjacency_list:
            self.adjacency_list[song.title] = []

    def add_edge(self, song1: Song, song2: Song):
        if song1.title in self.adjacency_list and song2.title in self.adjacency_list:
            if song2 not in self.adjacency_list[song1.title]:
                self.adjacency_list[song1.title].append(song2)
            if song1 not in self.adjacency_list[song2.title]:
                self.adjacency_list[song2.title].append(song1)

    def build_graph(self, songs: LinkedList):
        song_list = list(songs)
        for song in song_list:
            self.add_node(song)

        for i in range(len(song_list)):
            for j in range(i + 1, len(song_list)):
                song1 = song_list[i]
                song2 = song_list[j]
                
                if song1.artist == song2.artist or song1.mood == song2.mood:
                    self.add_edge(song1, song2)
    
    def get_recommendations(self, start_song_title: str, num_recs: int) -> List[Song]:
        if start_song_title not in self.adjacency_list:
            return []
        recommendations = []
        queue = [start_song_title]
        visited = {start_song_title}
        while queue and len(recommendations) < num_recs:
            current_title = queue.pop(0)
            neighbors = self.adjacency_list.get(current_title, [])
            for neighbor_song in neighbors:
                if neighbor_song.title not in visited:
                    visited.add(neighbor_song.title)
                    recommendations.append(neighbor_song)
                    queue.append(neighbor_song.title)
                    if len(recommendations) == num_recs:
                        break
        return recommendations

class MusicPlayer:

    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.music_library = LinkedList()
        self.playlists: Dict[str, Playlist] = {}
        self.current_song_list = LinkedList()
        self.current_song_index: int = -1
        self.is_playing: bool = False
        
        self.song_graph = Graph()

        self._load_default_library()
        self._load_playlists()
        
        self.song_graph.build_graph(self.music_library)

    def _load_default_library(self):
        default_songs = [
            {'title': 'Happy', 'artist': 'Pharrell Williams', 'mood': 'Happy', 'duration': 233, 'filepath': None},
            {'title': 'Walking on Sunshine', 'artist': 'Katrina & The Waves', 'mood': 'Happy', 'duration': 238},
            {'title': 'Blinding Lights', 'artist': 'The Weeknd', 'mood': 'Energetic', 'duration': 200, 'filepath': None},
            {'title': 'Don\'t Stop Me Now', 'artist': 'Queen', 'mood': 'Energetic', 'duration': 209, 'filepath': None},
            {'title': 'Someone Like You', 'artist': 'Adele', 'mood': 'Sad', 'duration': 285, 'filepath': None},
            {'title': 'Fix You', 'artist': 'Coldplay', 'mood': 'Sad', 'duration': 295, 'filepath': None},
            {'title': 'Weightless', 'artist': 'Marconi Union', 'mood': 'Calm', 'duration': 488, 'filepath': None},
            {'title': 'Clair de Lune', 'artist': 'Claude Debussy', 'mood': 'Calm', 'duration': 303, 'filepath': None},
        ]
        for s in default_songs:
            self.music_library.append(Song(**s))

    def _load_playlists(self):
        if os.path.exists("playlists.json"):
            try:
                with open("playlists.json", "r") as f:
                    playlists_data = json.load(f)
                    for p_data in playlists_data:
                        playlist = Playlist.from_dict(p_data)
                        self.playlists[playlist.name] = playlist
            except (json.JSONDecodeError, TypeError):
                self.playlists = {};

    def save_playlists(self):
        with open("playlists.json", "w") as f:
            json.dump([p.to_dict() for p in self.playlists.values()], f, indent=4)

    def add_song_from_file(self, filepath: str, title: str, artist: str, mood: str):
        try:
            sound = pygame.mixer.Sound(filepath)
            duration = sound.get_length()
            song = Song(title=title, artist=artist, mood=mood, duration=duration, filepath=filepath)
            self.music_library.append(song)
            self.song_graph.build_graph(self.music_library)
            return song
        except pygame.error:
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
            is_duplicate = False
            for existing_song in playlist.songs:
                if existing_song.filepath and song.filepath and existing_song.filepath == song.filepath:
                    is_duplicate = True
                    break
            if not is_duplicate:
                playlist.songs.append(song)
                self.save_playlists()
                return True
        return False
        
    def get_songs_by_mood(self, mood: str) -> LinkedList:
        if mood == "All":
            return self.music_library
        
        mood_list = LinkedList()
        for song in self.music_library:
            if song.mood == mood:
                mood_list.append(song)
        return mood_list

    def play_song(self, song_list: LinkedList, song_index: int):
        self.current_song_list = song_list
        self.current_song_index = song_index
        song = self.get_current_song()

        pygame.mixer.music.stop()
        if song and song.filepath and os.path.exists(song.filepath):
            try:
                pygame.mixer.music.load(song.filepath)
                pygame.mixer.music.play()
                self.is_playing = True;
            except pygame.error:
                self.is_playing = False;
        elif song:
            self.is_playing = True;
        else:
            self.is_playing = False;

    def get_current_song(self) -> Optional[Song]:
        if self.current_song_list and 0 <= self.current_song_index < len(self.current_song_list):
            return self.current_song_list.get(self.current_song_index)
        return None

    def toggle_play_pause(self):
        song = self.get_current_song()
        if not song: return
        
        if song.filepath and os.path.exists(song.filepath):
            if self.is_playing:
                if pygame.mixer.music.get_busy(): pygame.mixer.music.pause()
            else:
                pygame.mixer.music.unpause()
        
        self.is_playing = not self.is_playing

    def next_song(self):
        if len(self.current_song_list) > 0:
            next_index = (self.current_song_index + 1) % len(self.current_song_list)
            self.play_song(self.current_song_list, next_index)

    def prev_song(self):
        if len(self.current_song_list) > 0:
            prev_index = (self.current_song_index - 1 + len(self.current_song_list)) % len(self.current_song_list)
            self.play_song(self.current_song_list, prev_index)

    def set_volume(self, volume_level):
        pygame.mixer.music.set_volume(float(volume_level))
        
    def get_playback_position(self):
        song = self.get_current_song()
        if song and song.filepath and os.path.exists(song.filepath) and pygame.mixer.music.get_busy():
            return pygame.mixer.music.get_pos() / 1000, song.duration
        return 0, song.duration if song else 0;

class SortingManager:
    def __init__(self, update_callback: Callable, stats_callback: Callable, finished_callback: Callable):
        self.update_callback = update_callback
        self.stats_callback = stats_callback
        self.finished_callback = finished_callback
        self.is_sorting = False;
        self.comparisons = 0;
        self.swaps = 0;
        self.delay = 0.1;

    def sort_in_thread(self, algorithm: str, songs: List[Song]):
        if self.is_sorting: return;
        self.is_sorting = True;
        self.comparisons = 0;
        self.swaps = 0;
        thread = threading.Thread(target=self._run_sort, args=(algorithm, songs))
        thread.daemon = True;
        thread.start();

    def _run_sort(self, algorithm: str, songs: List[Song]):
        sorter = getattr(self, f"_{algorithm.lower().replace(' ', '_')}")
        sorter(songs);
        self.update_callback(songs, {})
        self.is_sorting = False
        self.finished_callback()

    def _bubble_sort(self, songs: List[Song]):
        n = len(songs)
        for i in range(n):
            swapped = False
            for j in range(0, n - i - 1):
                if not self.is_sorting: return
                self.comparisons += 1; self.stats_callback(self.comparisons, self.swaps)
                self.update_callback(songs, {'compare': [j, j + 1]}); time.sleep(self.delay)
                if songs[j].title.lower() > songs[j + 1].title.lower():
                    songs[j], songs[j + 1] = songs[j + 1], songs[j]
                    self.swaps += 1
                    self.update_callback(songs, {'swap': [j, j + 1]}); time.sleep(self.delay)
            if not swapped: break

    def _selection_sort(self, songs: List[Song]):
        n = len(songs)
        for i in range(n):
            min_idx = i
            for j in range(i + 1, n):
                if not self.is_sorting: return
                self.comparisons += 1; self.stats_callback(self.comparisons, self.swaps)
                self.update_callback(songs, {'compare': [j, min_idx], 'min': min_idx}); time.sleep(self.delay)
                if songs[j].title.lower() < songs[min_idx].title.lower():
                    min_idx = j
            if min_idx != i:
                songs[i], songs[min_idx] = songs[min_idx], songs[i]
                self.swaps += 1
                self.update_callback(songs, {'swap': [i, min_idx]}); time.sleep(self.delay)

    def _insertion_sort(self, songs: List[Song]):
        for i in range(1, len(songs)):
            key_song = songs[i]
            j = i - 1
            while j >= 0:
                if not self.is_sorting: return
                self.comparisons += 1; self.stats_callback(self.comparisons, self.swaps)
                self.update_callback(songs, {'compare': [j, i]}); time.sleep(self.delay)
                if key_song.title.lower() < songs[j].title.lower():
                    songs[j + 1] = songs[j]
                    self.swaps += 1
                    self.update_callback(songs, {'swap': [j, j+1]}); time.sleep(self.delay)
                    j -= 1
                else: break
            songs[j + 1] = key_song
            self.update_callback(songs, {}); time.sleep(self.delay)

class DFSManager:
    def __init__(self, update_callback: Callable, finished_callback: Callable):
        self.update_callback = update_callback
        self.finished_callback = finished_callback
        self.is_running = False

    def find_path_in_thread(self, graph: Graph, start_title: str, end_title: str):
        if self.is_running: return
        self.is_running = True
        thread = threading.Thread(target=self._run_dfs, args=(graph, start_title, end_title))
        thread.daemon = True
        thread.start()

    def _run_dfs(self, graph: Graph, start_title: str, end_title: str):
        stack = [(start_title, [start_title])]
        visited = {start_title}
        path_found = None

        while stack:
            current_title, path = stack.pop()
            self.update_callback({'visiting': {current_title}, 'path': set(path)}, None)
            time.sleep(0.3)

            if current_title == end_title:
                path_found = path
                break

            neighbors = graph.adjacency_list.get(current_title, [])
            sorted_neighbors = sorted(neighbors, key=lambda s: s.title, reverse=True)

            for neighbor_song in sorted_neighbors:
                if neighbor_song.title not in visited:
                    visited.add(neighbor_song.title)
                    new_path = path + [neighbor_song.title]
                    stack.append((neighbor_song.title, new_path))
        
        if path_found:
            self.update_callback({'path': set(path_found)}, f"Path found via DFS! (Length: {len(path_found)})")
        else:
            self.update_callback({}, "No path found between the selected songs.")

        self.is_running = False
        self.finished_callback()