import os
import tkinter as tk
from tkinter import ttk, messagebox, font, simpledialog, filedialog
import pygame
from core import MusicPlayer, SortingManager, Song
from typing import List

class AddSongDialog(simpledialog.Dialog):
    """Dialog to get details for a new song."""
    def body(self, master):
        self.title("Add Song Details")
        tk.Label(master, text="Title:").grid(row=0, sticky='w')
        tk.Label(master, text="Artist:").grid(row=1, sticky='w')
        tk.Label(master, text="Mood:").grid(row=2, sticky='w')
        
        self.title_entry = tk.Entry(master)
        self.artist_entry = tk.Entry(master)
        
        self.mood_var = tk.StringVar(master)
        self.mood_var.set("Happy")
        self.mood_menu = ttk.Combobox(master, textvariable=self.mood_var, values=["Happy", "Energetic", "Sad", "Calm"], state="readonly")

        self.title_entry.grid(row=0, column=1)
        self.artist_entry.grid(row=1, column=1)
        self.mood_menu.grid(row=2, column=1)
        
        if hasattr(self, 'filename'):
            base = os.path.basename(self.filename)
            self.title_entry.insert(0, os.path.splitext(base)[0])

        return self.title_entry

    def apply(self):
        self.result = {
            "title": self.title_entry.get(),
            "artist": self.artist_entry.get(),
            "mood": self.mood_var.get()
        }

class VibeTuneApp:
    def __init__(self, root):
        self.root = root
        self.root.title("VibeTune - Your Personal Music Sorter")
        self.root.geometry("1200x700")
        self.root.configure(bg='#f8f9fa')
        
        self.music_player = MusicPlayer()
        self.sorting_manager = SortingManager(
            update_callback=self.schedule_tree_update,
            stats_callback=self.schedule_stats_update,
            finished_callback=self.on_sort_finished
        )
        self.current_view = "Library"
        self.current_view_name = "All"
        self.displayed_songs: List[Song] = []
        self.sort_algorithm_var = tk.StringVar(value="Bubble Sort")
        
        self.setup_ui()
        self.load_songs_by_mood("All")
        self.update_playlist_listbox()
        self.update_playback_progress()

    def setup_ui(self):
        main_frame = tk.Frame(self.root, bg='#f8f9fa')
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        sidebar = tk.Frame(main_frame, bg='#e9ecef', width=250)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(5,0), pady=5)
        sidebar.pack_propagate(False)
        self.setup_sidebar(sidebar)
        
        content_frame = tk.Frame(main_frame, bg='#f8f9fa')
        content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.setup_content(content_frame)

        player_bar = tk.Frame(self.root, bg='#ffffff', height=100, bd=1, relief=tk.RIDGE)
        player_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.setup_player_controls(player_bar)

    def setup_sidebar(self, parent):
        tk.Label(parent, text="Library", font=("Inter", 16, "bold"), bg='#e9ecef', fg='#343a40').pack(pady=10, padx=10, anchor='w')
        
        moods = ["All", "Happy", "Energetic", "Sad", "Calm"]
        for mood in moods:
            btn = tk.Button(parent, text=mood, font=("Inter", 11), bg='#e9ecef', relief=tk.FLAT, anchor='w', command=lambda m=mood: self.load_songs_by_mood(m))
            btn.pack(fill=tk.X, padx=15, pady=2)

        tk.Button(parent, text="➕ Add Song File", font=("Inter", 10, "bold"), bg='#d3d9df', relief=tk.FLAT, command=self.add_song_dialog).pack(fill=tk.X, padx=10, pady=10)

        playlist_header = tk.Frame(parent, bg='#e9ecef')
        playlist_header.pack(fill=tk.X, pady=(20, 5), padx=10)
        tk.Label(playlist_header, text="Playlists", font=("Inter", 16, "bold"), bg='#e9ecef', fg='#343a40').pack(side=tk.LEFT)
        tk.Button(playlist_header, text="🗑️", font=("Inter", 12), relief=tk.FLAT, bg='#e9ecef', command=self.delete_playlist).pack(side=tk.RIGHT)
        tk.Button(playlist_header, text="➕", font=("Inter", 12, "bold"), relief=tk.FLAT, bg='#e9ecef', command=self.create_playlist_dialog).pack(side=tk.RIGHT)
        
        playlist_frame = tk.Frame(parent, bg='white')
        playlist_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.playlist_listbox = tk.Listbox(playlist_frame, font=("Inter", 11), relief=tk.FLAT, highlightthickness=0, selectbackground='#ff5500')
        self.playlist_listbox.pack(fill=tk.BOTH, expand=True)
        self.playlist_listbox.bind('<<ListboxSelect>>', self.on_playlist_select)

    def setup_content(self, parent):
        parent.grid_rowconfigure(1, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        
        header_frame = tk.Frame(parent, bg='#f8f9fa')
        header_frame.grid(row=0, column=0, sticky='ew', pady=(0, 10))
        self.playlist_title_label = tk.Label(header_frame, text="", font=("Inter", 24, "bold"), fg='#212529', bg='#f8f9fa')
        self.playlist_title_label.pack(side=tk.LEFT, pady=(0, 10))
        
        controls_frame = tk.Frame(header_frame, bg='#f8f9fa')
        controls_frame.pack(side=tk.RIGHT)
        
        stats_frame = tk.Frame(controls_frame, bg='#e9ecef', bd=1, relief=tk.SUNKEN)
        stats_frame.pack(side=tk.LEFT, padx=10, ipady=2, ipadx=5)
        self.comparisons_label = tk.Label(stats_frame, text="Comparisons: 0", font=("Inter", 9), bg='#e9ecef')
        self.comparisons_label.pack(anchor='w')
        self.swaps_label = tk.Label(stats_frame, text="Swaps: 0", font=("Inter", 9), bg='#e9ecef')
        self.swaps_label.pack(anchor='w')
        
        sort_algo_dropdown = ttk.Combobox(controls_frame, textvariable=self.sort_algorithm_var, values=["Bubble Sort", "Selection Sort", "Insertion Sort"], state="readonly", width=15)
        sort_algo_dropdown.pack(side=tk.LEFT)
        self.sort_button = tk.Button(controls_frame, text="Visualize Sort", command=self.visualize_sort, bg='#ff5500', fg='white', font=("Inter", 10, "bold"), relief=tk.FLAT, padx=10, pady=5)
        self.sort_button.pack(side=tk.LEFT, padx=5)

        tree_frame = tk.Frame(parent)
        tree_frame.grid(row=1, column=0, sticky='nsew')
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="white", rowheight=30, fieldbackground="white", font=("Inter", 10))
        style.configure("Treeview.Heading", font=("Inter", 10, "bold"), background="#e9ecef", relief="flat")
        style.map('Treeview', background=[('selected', '#fed7aa')])
        self.song_tree = ttk.Treeview(tree_frame, columns=('Artist', 'Mood', 'Duration'), show='headings')
        self.song_tree.heading('#0', text='Title'); self.song_tree.column('#0', width=300)
        self.song_tree.heading('Artist', text='Artist'); self.song_tree.column('Artist', width=200)
        self.song_tree.heading('Mood', text='Mood'); self.song_tree.column('Mood', width=100, anchor=tk.CENTER)
        self.song_tree.heading('Duration', text='Duration'); self.song_tree.column('Duration', width=100, anchor=tk.E)
        self.song_tree.tag_configure('compare', background='#fff3cd'); self.song_tree.tag_configure('swap', background='#f5c6cb'); self.song_tree.tag_configure('min', background='#cce5ff')
        
        self.song_tree.bind('<Double-1>', self.play_selected_song)
        self.song_tree.bind('<Button-3>', self.show_context_menu)
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.song_tree.yview)
        vsb.pack(side='right', fill='y'); self.song_tree.configure(yscrollcommand=vsb.set)
        self.song_tree.pack(side='left', fill='both', expand=True)
    
    def setup_player_controls(self, parent):
        parent.grid_columnconfigure(1, weight=1)
        info_frame = tk.Frame(parent, bg='white'); info_frame.grid(row=0, column=0, rowspan=2, padx=20, sticky='w')
        self.current_song_label = tk.Label(info_frame, text="No Song Playing", font=("Inter", 12, "bold"), bg='white')
        self.current_song_label.pack(anchor='w')
        self.current_artist_label = tk.Label(info_frame, text="Select a song to play", font=("Inter", 9), bg='white')
        self.current_artist_label.pack(anchor='w')

        center_frame = tk.Frame(parent, bg='white'); center_frame.grid(row=0, column=1, rowspan=2)
        button_controls = tk.Frame(center_frame, bg='white'); button_controls.pack()
        tk.Button(button_controls, text="⏮", command=self.music_player.prev_song, font=("Arial", 16), relief=tk.FLAT, bg='white').pack(side=tk.LEFT, padx=10)
        self.play_pause_btn = tk.Button(button_controls, text="▶", command=self.toggle_play_pause, font=("Arial", 20, "bold"), relief=tk.FLAT, bg='#ff5500', fg='white', padx=10, width=3)
        self.play_pause_btn.pack(side=tk.LEFT, padx=10)
        tk.Button(button_controls, text="⏭", command=self.music_player.next_song, font=("Arial", 16), relief=tk.FLAT, bg='white').pack(side=tk.LEFT, padx=10)

        progress_controls = tk.Frame(center_frame, bg='white'); progress_controls.pack(fill=tk.X, padx=10, pady=5)
        self.current_time_label = tk.Label(progress_controls, text="0:00", font=("Inter", 9), bg='white'); self.current_time_label.pack(side=tk.LEFT)
        self.progress_bar = ttk.Scale(progress_controls, from_=0, to=100); self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        self.duration_label = tk.Label(progress_controls, text="0:00", font=("Inter", 9), bg='white'); self.duration_label.pack(side=tk.RIGHT)

        volume_frame = tk.Frame(parent, bg='white'); volume_frame.grid(row=0, column=2, rowspan=2, padx=20, sticky='e')
        tk.Label(volume_frame, text="🔊", bg='white', font=("Arial", 14)).pack(side=tk.LEFT)
        self.volume_slider = ttk.Scale(volume_frame, from_=0, to=1, command=self.music_player.set_volume); self.volume_slider.set(1.0)
        self.volume_slider.pack(side=tk.LEFT, padx=5)

    def add_song_dialog(self):
        filepath = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3 *.wav")])
        if not filepath: return
        
        dialog = AddSongDialog(self.root)
        dialog.filename = filepath
        if dialog.result:
            details = dialog.result
            if not details['title'] or not details['artist']:
                messagebox.showerror("Error", "Title and Artist cannot be empty.")
                return
            
            song = self.music_player.add_song_from_file(filepath, **details)
            if song:
                messagebox.showinfo("Success", f"Added '{song.title}' to the library.")
                self.load_songs_by_mood(self.current_view_name if self.current_view == "Library" else "All")

    def create_playlist_dialog(self):
        name = simpledialog.askstring("New Playlist", "Enter playlist name:")
        if name:
            if self.music_player.create_playlist(name):
                self.update_playlist_listbox()
            else:
                messagebox.showerror("Error", "A playlist with that name already exists.")
    
    def delete_playlist(self):
        selected = self.playlist_listbox.curselection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a playlist to delete.")
            return
        
        name = self.playlist_listbox.get(selected[0])
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the playlist '{name}'?"):
            self.music_player.delete_playlist(name)
            self.update_playlist_listbox()
            if self.current_view == "Playlist" and self.current_view_name == name:
                self.load_songs_by_mood("All")

    def update_playlist_listbox(self):
        self.playlist_listbox.delete(0, tk.END)
        for name in sorted(self.music_player.playlists.keys()):
            self.playlist_listbox.insert(tk.END, name)

    def on_playlist_select(self, event=None):
        selected = self.playlist_listbox.curselection()
        if not selected: return

        playlist_name = self.playlist_listbox.get(selected[0])
        self.current_view = "Playlist"
        self.current_view_name = playlist_name
        self.playlist_title_label.config(text=f"Playlist: {playlist_name}")
        self.sort_button.config(state=tk.DISABLED)
        
        self.displayed_songs = self.music_player.playlists[playlist_name].songs
        self.update_song_tree(self.displayed_songs, {})

    def show_context_menu(self, event):
        if not self.song_tree.focus(): return

        context_menu = tk.Menu(self.root, tearoff=0)
        add_to_playlist_menu = tk.Menu(context_menu, tearoff=0)

        if not self.music_player.playlists:
            add_to_playlist_menu.add_command(label="No playlists yet...", state=tk.DISABLED)
        else:
            for name in self.music_player.playlists.keys():
                add_to_playlist_menu.add_command(label=name, command=lambda n=name: self.add_selected_to_playlist(n))
        
        context_menu.add_cascade(label="Add to Playlist", menu=add_to_playlist_menu)
        context_menu.post(event.x_root, event.y_root)

    def add_selected_to_playlist(self, playlist_name):
        if not self.song_tree.focus(): return
        
        song_title = self.song_tree.item(self.song_tree.focus())['text']
        song_to_add = next((s for s in self.displayed_songs if s.title == song_title), None)
        
        if song_to_add:
            if not self.music_player.add_song_to_playlist(playlist_name, song_to_add):
                messagebox.showinfo("Already Exists", f"'{song_to_add.title}' is already in that playlist.")

    def load_songs_by_mood(self, mood):
        self.current_view = "Library"
        self.current_view_name = mood
        self.playlist_title_label.config(text=f"{mood} Vibes")
        self.sort_button.config(state=tk.NORMAL)
        self.playlist_listbox.selection_clear(0, tk.END)

        self.displayed_songs = self.music_player.get_songs_by_mood(mood)
        self.update_song_tree(self.displayed_songs, {})

    def visualize_sort(self):
        if self.current_view != "Library":
            messagebox.showinfo("Info", "Sorting is only available in the Library view.")
            return
        if self.sorting_manager.is_sorting: return
        
        self.sort_button.config(state=tk.DISABLED, text="Sorting...")
        self.update_stats_labels(0, 0)
        algorithm = self.sort_algorithm_var.get()
        songs_to_sort = self.music_player.get_songs_by_mood(self.current_view_name)
        self.displayed_songs = songs_to_sort
        self.sorting_manager.sort_in_thread(algorithm, self.displayed_songs)
    
    def play_selected_song(self, event=None):
        if not self.song_tree.focus() or self.sorting_manager.is_sorting: return
        
        song_title = self.song_tree.item(self.song_tree.focus())['text']
        song_index = next((i for i, s in enumerate(self.displayed_songs) if s.title == song_title), -1)
        
        if song_index != -1:
            self.music_player.play_song(self.displayed_songs, song_index)
            self.update_player_info()
            self.play_pause_btn.config(text="⏸")

    def update_song_tree(self, songs: List[Song], highlights: dict):
        self.song_tree.delete(*self.song_tree.get_children())
        for i, song in enumerate(songs):
            duration_str = f"{int(song.duration // 60)}:{int(song.duration % 60):02d}"
            tags=()
            if 'compare' in highlights and i in highlights['compare']: tags = ('compare',)
            if 'swap' in highlights and i in highlights['swap']: tags = ('swap',)
            if 'min' in highlights and i == highlights['min']: tags = ('min',)
            self.song_tree.insert('', tk.END, text=song.title, values=(song.artist, song.mood, duration_str), tags=tags)
    def schedule_tree_update(self, songs, highlights): self.root.after(0, self.update_song_tree, list(songs), highlights)
    def schedule_stats_update(self, c, s): self.root.after(0, self.update_stats_labels, c, s)
    def update_stats_labels(self, c, s): self.comparisons_label.config(text=f"Comparisons: {c}"); self.swaps_label.config(text=f"Swaps: {s}")
    def on_sort_finished(self):
        def re_enable(): self.sort_button.config(state=tk.NORMAL, text="Visualize Sort"); messagebox.showinfo("Sorting Complete", f"Finished: {self.sort_algorithm_var.get()}.")
        self.root.after(0, re_enable)
    def toggle_play_pause(self): self.music_player.toggle_play_pause(); self.play_pause_btn.config(text="⏸" if self.music_player.is_playing else "▶")
    def update_player_info(self):
        song=self.music_player.get_current_song()
        if song: self.current_song_label.config(text=song.title); self.current_artist_label.config(text=song.artist)
        else: self.current_song_label.config(text="No Song Playing"); self.current_artist_label.config(text="Select a song to play")
    def update_playback_progress(self):
        current_time, duration = self.music_player.get_playback_position()
        self.duration_label.config(text=f"{int(duration // 60)}:{int(duration % 60):02d}")
        self.current_time_label.config(text=f"{int(current_time // 60)}:{int(current_time % 60):02d}")
        self.progress_bar.set((current_time / duration) * 100 if duration > 0 else 0)
        
        song = self.music_player.get_current_song()
        if self.music_player.is_playing and song and not song.filepath:
             progress = self.progress_bar.get()
             increment = (100 / duration) if duration > 0 else 100
             if progress + increment >= 100: self.music_player.next_song()
             else: self.progress_bar.set(progress + increment)
        elif self.music_player.is_playing and song and song.filepath and not pygame.mixer.music.get_busy():
            self.music_player.next_song()

        self.update_player_info()
        self.root.after(1000, self.update_playback_progress)