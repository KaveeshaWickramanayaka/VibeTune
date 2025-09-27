import json
import os
import time
import threading
from dataclasses import dataclass
from typing import List, Dict, Optional, Callable

@dataclass
class Song:
    title: str
    artist: str
    mood: str
    energy: int
    valence: int
    duration: str
    
    def to_dict(self):
        return {
            'title': self.title,
            'artist': self.artist,
            'mood': self.mood,
            'energy': self.energy,
            'valence': self.valence,
            'duration': self.duration
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(**data)
    
    def __eq__(self, other):
        """Custom equality check based on title and artist"""
        if isinstance(other, Song):
            return self.title == other.title and self.artist == other.artist
        return False
    
    def __hash__(self):
        """Make Song hashable for use in sets/dicts"""
        return hash((self.title, self.artist))

class Playlist:
    def __init__(self, name: str):
        self.name = name
        self.songs: List[Song] = []
    
    def add_song(self, song: Song) -> bool:
        if song not in self.songs:
            self.songs.append(song)
            return True
        return False
    
    def remove_song(self, song: Song) -> bool:
        if song in self.songs:
            self.songs.remove(song)
            return True
        return False
    
    def to_dict(self):
        return {
            'name': self.name,
            'songs': [song.to_dict() for song in self.songs]
        }
    
    @classmethod
    def from_dict(cls, data):
        playlist = cls(data['name'])
        songs_data = data.get('songs', [])
        for song_data in songs_data:
            song = Song.from_dict(song_data)
            playlist.songs.append(song)
        return playlist

class MusicPlayer:
    def __init__(self):
        self.music_library: List[Song] = []
        self.playlists: Dict[str, Playlist] = {}
        self.current_playlist: List[Song] = []
        self.current_song_index: int = 0
        self.is_playing: bool = False
        self.current_mood: str = "All"
        self._load_default_library()
        self._load_playlists()
        self._ensure_default_playlists()
    
    def _ensure_default_playlists(self):
        """Create default playlists if they don't exist"""
        default_playlists = ["Liked Songs", "Workout", "Chill", "Focus"]
        for name in default_playlists:
            if name not in self.playlists:
                self.create_playlist(name)
    
    def _load_default_library(self):
        default_songs = [
            {"title": "Blinding Lights", "artist": "The Weeknd", "mood": "Energetic", "energy": 95, "valence": 85, "duration": "3:20"},
            {"title": "Someone Like You", "artist": "Adele", "mood": "Sad", "energy": 25, "valence": 15, "duration": "4:45"},
            {"title": "Happy", "artist": "Pharrell Williams", "mood": "Happy", "energy": 90, "valence": 95, "duration": "3:53"},
            {"title": "The Sound of Silence", "artist": "Simon & Garfunkel", "mood": "Melancholic", "energy": 20, "valence": 30, "duration": "3:05"},
            {"title": "Can't Stop the Feeling", "artist": "Justin Timberlake", "mood": "Happy", "energy": 85, "valence": 90, "duration": "3:56"},
            {"title": "Bohemian Rhapsody", "artist": "Queen", "mood": "Energetic", "energy": 80, "valence": 70, "duration": "5:55"},
            {"title": "Mad World", "artist": "Gary Jules", "mood": "Sad", "energy": 15, "valence": 10, "duration": "3:07"},
            {"title": "Good Vibrations", "artist": "The Beach Boys", "mood": "Happy", "energy": 75, "valence": 85, "duration": "3:36"},
            {"title": "Hurt", "artist": "Johnny Cash", "mood": "Melancholic", "energy": 30, "valence": 20, "duration": "3:38"},
            {"title": "I Want It That Way", "artist": "Backstreet Boys", "mood": "Energetic", "energy": 70, "valence": 80, "duration": "3:33"},
            {"title": "Tears in Heaven", "artist": "Eric Clapton", "mood": "Sad", "energy": 35, "valence": 25, "duration": "4:32"},
            {"title": "Walking on Sunshine", "artist": "Katrina and the Waves", "mood": "Happy", "energy": 88, "valence": 92, "duration": "3:58"},
            {"title": "Everybody Hurts", "artist": "R.E.M.", "mood": "Sad", "energy": 40, "valence": 20, "duration": "5:17"},
            {"title": "Don't Stop Me Now", "artist": "Queen", "mood": "Energetic", "energy": 92, "valence": 88, "duration": "3:29"},
            {"title": "Black", "artist": "Pearl Jam", "mood": "Melancholic", "energy": 45, "valence": 25, "duration": "5:43"}
        ]
        for song_data in default_songs:
            self.music_library.append(Song.from_dict(song_data))
    
    def _load_playlists(self):
        try:
            # Check current working directory first
            playlist_path = "playlists.json"
            
            # Try current directory first, then script directory
            if not os.path.exists(playlist_path):
                script_dir = os.path.dirname(os.path.abspath(__file__))
                playlist_path = os.path.join(script_dir, "playlists.json")
            
            if os.path.exists(playlist_path):
                with open(playlist_path, "r") as f:
                    playlist_data = json.load(f)
                    for name, data in playlist_data.items():
                        self.playlists[name] = Playlist.from_dict(data)
        except Exception as e:
            print(f"Failed to load playlists: {str(e)}")
    
    def save_playlists(self) -> bool:
        try:
            # Save in the same directory as the script
            script_dir = os.path.dirname(os.path.abspath(__file__))
            playlist_path = os.path.join(script_dir, "playlists.json")
            
            playlist_data = {name: playlist.to_dict() for name, playlist in self.playlists.items()}
            with open(playlist_path, "w") as f:
                json.dump(playlist_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Failed to save playlists: {str(e)}")
            return False
    
    def get_filtered_music(self) -> List[Song]:
        if self.current_mood == "All":
            return self.music_library.copy()
        return [song for song in self.music_library if song.mood == self.current_mood]
    
    def create_playlist(self, name: str) -> bool:
        if name not in self.playlists:
            self.playlists[name] = Playlist(name)
            return True
        return False
    
    def delete_playlist(self, name: str) -> bool:
        print(f"DEBUG: core.delete_playlist called with name: '{name}'")
        print(f"DEBUG: Available playlists: {list(self.playlists.keys())}")
        if name in self.playlists:
            print(f"DEBUG: Playlist '{name}' found, deleting...")
            del self.playlists[name]
            print(f"DEBUG: Playlist deleted. Remaining playlists: {list(self.playlists.keys())}")
            return True
        else:
            print(f"DEBUG: Playlist '{name}' not found!")
            return False
    
    def rename_playlist(self, old_name: str, new_name: str) -> bool:
        if old_name in self.playlists and new_name not in self.playlists:
            self.playlists[new_name] = self.playlists.pop(old_name)
            self.playlists[new_name].name = new_name
            return True
        return False
    
    def add_to_playlist(self, playlist_name: str, song: Song) -> bool:
        if playlist_name in self.playlists:
            return self.playlists[playlist_name].add_song(song)
        return False
    
    def remove_from_playlist(self, playlist_name: str, song: Song) -> bool:
        if playlist_name in self.playlists:
            return self.playlists[playlist_name].remove_song(song)
        return False
    
    def get_playlist_songs(self, playlist_name: str) -> List[Song]:
        if playlist_name in self.playlists:
            return self.playlists[playlist_name].songs.copy()
        return []
    
    def playlist_exists(self, playlist_name: str) -> bool:
        return playlist_name in self.playlists
    
    def toggle_like_song(self, song: Song) -> bool:
        """Add/remove song from 'Liked Songs' playlist"""
        print(f"DEBUG: core.toggle_like_song called with: {song.title} by {song.artist}")
        if "Liked Songs" not in self.playlists:
            print("DEBUG: 'Liked Songs' playlist not found, creating it...")
            self.create_playlist("Liked Songs")
        
        liked_playlist = self.playlists["Liked Songs"]
        print(f"DEBUG: Liked playlist has {len(liked_playlist.songs)} songs before toggle")
        
        if song in liked_playlist.songs:
            print("DEBUG: Song is already liked, removing...")
            result = liked_playlist.remove_song(song)  # Unlike
            print(f"DEBUG: Remove result: {result}")
            return result
        else:
            print("DEBUG: Song is not liked, adding...")
            result = liked_playlist.add_song(song)  # Like
            print(f"DEBUG: Add result: {result}")
            return result
    
    def is_song_liked(self, song: Song) -> bool:
        """Check if a song is in Liked Songs playlist"""
        if "Liked Songs" in self.playlists:
            return song in self.playlists["Liked Songs"].songs
        return False
    
    def get_playlist_stats(self, playlist_name: str) -> Dict:
        if playlist_name not in self.playlists:
            return {}
        
        playlist = self.playlists[playlist_name]
        if not playlist.songs:
            return {"total_songs": 0, "total_duration": "0:00"}
        
        total_seconds = sum(self._parse_duration(song.duration) for song in playlist.songs)
        moods = [song.mood for song in playlist.songs]
        artists = [song.artist for song in playlist.songs]
        
        return {
            "total_songs": len(playlist.songs),
            "total_duration": self._format_duration(total_seconds),
            "most_common_mood": max(set(moods), key=moods.count) if moods else "None",
            "most_common_artist": max(set(artists), key=artists.count) if artists else "None",
            "average_energy": round(sum(song.energy for song in playlist.songs) / len(playlist.songs), 1),
            "average_valence": round(sum(song.valence for song in playlist.songs) / len(playlist.songs), 1)
        }
    
    def _parse_duration(self, duration_str: str) -> int:
        """Convert "3:45" to seconds"""
        try:
            parts = duration_str.split(':')
            if len(parts) == 2:
                return int(parts[0]) * 60 + int(parts[1])
            return 0
        except:
            return 0
    
    def _format_duration(self, total_seconds: int) -> str:
        """Convert seconds to "HH:MM" format"""
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        if hours > 0:
            return f"{hours}:{minutes:02d}"
        return f"{minutes}"
    
    def play_song(self, song: Song) -> None:
        filtered_music = self.get_filtered_music()
        for i, s in enumerate(filtered_music):
            if s.title == song.title and s.artist == song.artist:
                self.current_playlist = filtered_music
                self.current_song_index = i
                self.is_playing = True
                break
    
    def next_song(self) -> Optional[Song]:
        if self.current_playlist and self.current_song_index < len(self.current_playlist) - 1:
            self.current_song_index += 1
            return self.current_playlist[self.current_song_index]
        return None
    
    def previous_song(self) -> Optional[Song]:
        if self.current_playlist and self.current_song_index > 0:
            self.current_song_index -= 1
            return self.current_playlist[self.current_song_index]
        return None
    
    def get_current_song(self) -> Optional[Song]:
        if self.current_playlist and 0 <= self.current_song_index < len(self.current_playlist):
            return self.current_playlist[self.current_song_index]
        return None

class SortingManager:
    def __init__(self, update_callback: Callable, stats_callback: Callable):
        self.update_callback = update_callback
        self.stats_callback = stats_callback
        self.is_sorting = False
        self.comparisons = 0
        self.swaps = 0
    
    def sort_music(self, algorithm: str, criteria: str, music_list: List[Dict]) -> None:
        if self.is_sorting:
            return
            
        self.is_sorting = True
        self.comparisons = 0
        self.swaps = 0
        
        sort_thread = threading.Thread(
            target=self._sort_thread, 
            args=(algorithm, criteria, music_list)
        )
        sort_thread.daemon = True
        sort_thread.start()
    
    def _sort_thread(self, algorithm: str, criteria: str, music_list: List[Dict]) -> None:
        try:
            if algorithm == "Bubble Sort":
                self._bubble_sort(music_list, criteria)
            elif algorithm == "Selection Sort":
                self._selection_sort(music_list, criteria)
            elif algorithm == "Insertion Sort":
                self._insertion_sort(music_list, criteria)
            
            self._update_status(f"Sorted by {criteria} ✅", '#27ae60')
        except Exception as e:
            self._update_status(f"Sorting error: {str(e)}", '#e74c3c')
        finally:
            self.is_sorting = False
    
    def _bubble_sort(self, music_list: List[Dict], criteria: str) -> None:
        n = len(music_list)
        
        for i in range(n):
            swapped = False
            for j in range(0, n - i - 1):
                if not self.is_sorting:
                    return
                    
                self.comparisons += 1
                self._update_stats()
                self._highlight_comparison([j, j + 1])
                time.sleep(0.3)
                
                if self._compare_songs(music_list[j], music_list[j + 1], criteria):
                    music_list[j], music_list[j + 1] = music_list[j + 1], music_list[j]
                    swapped = True
                    self.swaps += 1
                    self._highlight_swap([j, j + 1])
                    time.sleep(0.3)
                
                self._update_display()
                time.sleep(0.2)
            
            if not swapped:
                break
    
    def _selection_sort(self, music_list: List[Dict], criteria: str) -> None:
        n = len(music_list)
        
        for i in range(n):
            min_idx = i
            for j in range(i + 1, n):
                if not self.is_sorting:
                    return
                    
                self.comparisons += 1
                self._update_stats()
                self._highlight_comparison([min_idx, j])
                time.sleep(0.3)
                
                if self._compare_songs(music_list[min_idx], music_list[j], criteria):
                    min_idx = j
                
                self._update_display()
            
            if min_idx != i:
                music_list[i], music_list[min_idx] = music_list[min_idx], music_list[i]
                self.swaps += 1
                self._highlight_swap([i, min_idx])
                time.sleep(0.3)
                self._update_display()
                time.sleep(0.2)
    
    def _insertion_sort(self, music_list: List[Dict], criteria: str) -> None:
        for i in range(1, len(music_list)):
            key = music_list[i]
            j = i - 1
            
            while j >= 0:
                if not self.is_sorting:
                    return
                    
                self.comparisons += 1
                self._update_stats()
                self._highlight_comparison([j, j + 1])
                time.sleep(0.3)
                
                if not self._compare_songs(music_list[j], key, criteria):
                    break
                
                music_list[j + 1] = music_list[j]
                self.swaps += 1
                j -= 1
                self._update_display()
                time.sleep(0.2)
            
            music_list[j + 1] = key
            self._update_display()
    
    def _compare_songs(self, song1: Dict, song2: Dict, criteria: str) -> bool:
        if criteria == "Energy":
            return song1['energy'] > song2['energy']
        elif criteria == "Valence":
            return song1['valence'] > song2['valence']
        elif criteria == "Artist":
            return song1['artist'] > song2['artist']
        elif criteria == "Title":
            return song1['title'] > song2['title']
        return False
    
    def _highlight_comparison(self, indices: List[int]) -> None:
        highlight_dict = {idx: 'comparing' for idx in indices}
        self.update_callback(highlight_dict)
    
    def _highlight_swap(self, indices: List[int]) -> None:
        highlight_dict = {idx: 'swapping' for idx in indices}
        self.update_callback(highlight_dict)
    
    def _update_display(self) -> None:
        self.update_callback({})
    
    def _update_stats(self) -> None:
        self.stats_callback(self.comparisons, self.swaps)
    
    def _update_status(self, message: str, color: str) -> None:
        if hasattr(self.update_callback, '__self__'):
            self.update_callback.__self__.sort_status.config(text=message, fg=color)