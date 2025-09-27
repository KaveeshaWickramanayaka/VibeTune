import tkinter as tk
from tkinter import ttk, messagebox
from core import MusicPlayer, SortingManager, Song

class MoodMusicPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Mood Music Player - Sorting Algorithm Demo")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1a1a1a')
        
        self.music_player = MusicPlayer()
        self.sorting_manager = SortingManager(
            update_callback=self.update_music_display,
            stats_callback=self.update_sort_stats
        )
        
        self.is_sorting = False
        self.sort_comparisons = 0
        self.sort_swaps = 0
        
        self.setup_ui()
        self.update_music_display()
    
    def setup_ui(self):
        header_frame = tk.Frame(self.root, bg='#2d2d2d', height=100)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text="🎵 Mood Music Player", 
                              font=('Arial', 24, 'bold'), fg='#ffffff', bg='#2d2d2d')
        title_label.pack(expand=True)
        
        subtitle_label = tk.Label(header_frame, text="Smart Music Sorting Based on Your Mood", 
                                 font=('Arial', 12), fg='#cccccc', bg='#2d2d2d')
        subtitle_label.pack()
        
        main_container = tk.Frame(self.root, bg='#1a1a1a')
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        left_panel = tk.Frame(main_container, bg='#2d2d2d', width=300)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)
        
        mood_frame = tk.LabelFrame(left_panel, text="🎭 Select Your Mood", 
                                  font=('Arial', 12, 'bold'), fg='#ffffff', bg='#2d2d2d')
        mood_frame.pack(fill=tk.X, padx=10, pady=10)
        
        moods = ["All", "Happy", "Energetic", "Sad", "Melancholic", "Romantic", "Chill"]
        mood_colors = {"Happy": "#f1c40f", "Energetic": "#e74c3c", "Sad": "#3498db", 
                      "Melancholic": "#9b59b6", "Romantic": "#e91e63", "Chill": "#2ecc71", "All": "#95a5a6"}
        
        for mood in moods:
            color = mood_colors.get(mood, "#95a5a6")
            btn = tk.Button(mood_frame, text=f"{mood} {'❤️' if mood == 'Romantic' else ''}", 
                           command=lambda m=mood: self.select_mood(m),
                           bg=color, fg='white', font=('Arial', 10, 'bold'),
                           relief=tk.FLAT, padx=20, pady=5)
            btn.pack(fill=tk.X, pady=2)
        
        sorting_frame = tk.LabelFrame(left_panel, text="🔧 Sorting Options", 
                                     font=('Arial', 12, 'bold'), fg='#ffffff', bg='#2d2d2d')
        sorting_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.sort_var = tk.StringVar(value="Bubble Sort")
        sort_algorithms = ["Bubble Sort", "Selection Sort", "Insertion Sort"]
        for algo in sort_algorithms:
            rb = tk.Radiobutton(sorting_frame, text=algo, variable=self.sort_var, value=algo,
                               fg='#ffffff', bg='#2d2d2d', selectcolor='#404040', 
                               font=('Arial', 10))
            rb.pack(anchor=tk.W, padx=10)
        
        self.sort_criteria = tk.StringVar(value="Energy")
        criteria_frame = tk.Frame(sorting_frame, bg='#2d2d2d')
        criteria_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(criteria_frame, text="Sort by:", fg='#ffffff', bg='#2d2d2d').pack(side=tk.LEFT)
        criteria_combo = ttk.Combobox(criteria_frame, textvariable=self.sort_criteria, 
                                     values=["Energy", "Valence", "Artist", "Title"], width=10)
        criteria_combo.pack(side=tk.RIGHT)
        
        tk.Button(sorting_frame, text="🔄 Sort Music", command=self.start_sorting,
                 bg='#3498db', fg='white', font=('Arial', 10, 'bold'), pady=5).pack(fill=tk.X, padx=10, pady=5)
        
        stats_frame = tk.LabelFrame(left_panel, text="📊 Sorting Stats", 
                                   font=('Arial', 12, 'bold'), fg='#ffffff', bg='#2d2d2d')
        stats_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.comparisons_label = tk.Label(stats_frame, text="Comparisons: 0", 
                                         fg='#ffffff', bg='#2d2d2d', font=('Arial', 10))
        self.comparisons_label.pack(anchor=tk.W, padx=10)
        
        self.swaps_label = tk.Label(stats_frame, text="Swaps: 0", 
                                   fg='#ffffff', bg='#2d2d2d', font=('Arial', 10))
        self.swaps_label.pack(anchor=tk.W, padx=10)
        
        self.sort_status = tk.Label(stats_frame, text="Ready to sort", 
                                   fg='#2ecc71', bg='#2d2d2d', font=('Arial', 10))
        self.sort_status.pack(anchor=tk.W, padx=10)
        
        playlist_frame = tk.LabelFrame(left_panel, text="📝 Playlists", 
                                      font=('Arial', 12, 'bold'), fg='#ffffff', bg='#2d2d2d')
        playlist_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        playlist_controls = tk.Frame(playlist_frame, bg='#2d2d2d')
        playlist_controls.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Button(playlist_controls, text="➕ New", command=self.create_playlist,
                 bg='#27ae60', fg='white', font=('Arial', 9)).pack(side=tk.LEFT, padx=2)
        tk.Button(playlist_controls, text="💾 Save", command=self.save_playlists,
                 bg='#f39c12', fg='white', font=('Arial', 9)).pack(side=tk.LEFT, padx=2)
        
        self.playlist_listbox = tk.Listbox(playlist_frame, bg='#404040', fg='#ffffff', 
                                          font=('Arial', 10), selectbackground='#3498db')
        self.playlist_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.playlist_listbox.bind('<<ListboxSelect>>', self.on_playlist_select)
        
        self.update_playlist_display()
        
        center_panel = tk.Frame(main_container, bg='#2d2d2d')
        center_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        music_header = tk.Frame(center_panel, bg='#404040', height=50)
        music_header.pack(fill=tk.X)
        music_header.pack_propagate(False)
        
        tk.Label(music_header, text="🎶 Music Library", font=('Arial', 16, 'bold'), 
                fg='#ffffff', bg='#404040').pack(expand=True)
        
        tree_frame = tk.Frame(center_panel, bg='#2d2d2d')
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar_y = ttk.Scrollbar(tree_frame)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        scrollbar_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Custom.Treeview', background='#404040', foreground='#ffffff', 
                       fieldbackground='#404040', borderwidth=0)
        style.configure('Custom.Treeview.Heading', background='#2d2d2d', 
                       foreground='#ffffff', font=('Arial', 10, 'bold'))
        
        self.music_tree = ttk.Treeview(tree_frame, yscrollcommand=scrollbar_y.set, 
                                      xscrollcommand=scrollbar_x.set, style='Custom.Treeview')
        self.music_tree.pack(fill=tk.BOTH, expand=True)
        
        scrollbar_y.config(command=self.music_tree.yview)
        scrollbar_x.config(command=self.music_tree.xview)
        
        self.music_tree['columns'] = ('artist', 'mood', 'energy', 'valence', 'duration')
        self.music_tree.column('#0', width=200, minwidth=150)
        self.music_tree.column('artist', width=150, minwidth=100)
        self.music_tree.column('mood', width=100, minwidth=80)
        self.music_tree.column('energy', width=80, minwidth=60)
        self.music_tree.column('valence', width=80, minwidth=60)
        self.music_tree.column('duration', width=80, minwidth=60)
        
        self.music_tree.heading('#0', text='Song Title', anchor=tk.W)
        self.music_tree.heading('artist', text='Artist', anchor=tk.W)
        self.music_tree.heading('mood', text='Mood', anchor=tk.CENTER)
        self.music_tree.heading('energy', text='Energy', anchor=tk.CENTER)
        self.music_tree.heading('valence', text='Valence', anchor=tk.CENTER)
        self.music_tree.heading('duration', text='Duration', anchor=tk.CENTER)
        
        self.music_tree.tag_configure('Happy', background='#f1c40f', foreground='#000000')
        self.music_tree.tag_configure('Energetic', background='#e74c3c', foreground='#ffffff')
        self.music_tree.tag_configure('Sad', background='#3498db', foreground='#ffffff')
        self.music_tree.tag_configure('Melancholic', background='#9b59b6', foreground='#ffffff')
        self.music_tree.tag_configure('comparing', background='#f39c12', foreground='#000000')
        self.music_tree.tag_configure('swapping', background='#e67e22', foreground='#ffffff')
        
        self.music_tree.bind('<Double-1>', self.play_selected_song)
        self.music_tree.bind('<Button-3>', self.show_context_menu)
        
        right_panel = tk.Frame(main_container, bg='#2d2d2d', width=250)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y)
        right_panel.pack_propagate(False)
        
        player_frame = tk.LabelFrame(right_panel, text="🎵 Now Playing", 
                                    font=('Arial', 12, 'bold'), fg='#ffffff', bg='#2d2d2d')
        player_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.current_song_label = tk.Label(player_frame, text="No song selected", 
                                          font=('Arial', 11, 'bold'), fg='#ffffff', bg='#2d2d2d',
                                          wraplength=200)
        self.current_song_label.pack(pady=5)
        
        self.current_artist_label = tk.Label(player_frame, text="", 
                                            font=('Arial', 10), fg='#cccccc', bg='#2d2d2d',
                                            wraplength=200)
        self.current_artist_label.pack()
        
        controls_frame = tk.Frame(player_frame, bg='#2d2d2d')
        controls_frame.pack(pady=10)
        
        tk.Button(controls_frame, text="⏮️", command=self.previous_song,
                 bg='#3498db', fg='white', font=('Arial', 12), width=3).pack(side=tk.LEFT, padx=2)
        
        self.play_button = tk.Button(controls_frame, text="▶️", command=self.toggle_play,
                                    bg='#27ae60', fg='white', font=('Arial', 12), width=3)
        self.play_button.pack(side=tk.LEFT, padx=2)
        
        tk.Button(controls_frame, text="⏭️", command=self.next_song,
                 bg='#3498db', fg='white', font=('Arial', 12), width=3).pack(side=tk.LEFT, padx=2)
        
        queue_frame = tk.LabelFrame(right_panel, text="📋 Play Queue", 
                                   font=('Arial', 12, 'bold'), fg='#ffffff', bg='#2d2d2d')
        queue_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.queue_listbox = tk.Listbox(queue_frame, bg='#404040', fg='#ffffff', 
                                       font=('Arial', 9), selectbackground='#3498db')
        self.queue_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.queue_listbox.bind('<Double-1>', self.play_from_queue)
        
        self.context_menu = tk.Menu(self.root, tearoff=0, bg='#2d2d2d', fg='#ffffff')
        self.context_menu.add_command(label="Add to Playlist", command=self.add_to_playlist_dialog)
        self.context_menu.add_command(label="Play Now", command=self.play_selected_song)
        self.context_menu.add_command(label="Add to Queue", command=self.add_to_queue)
    
    def select_mood(self, mood):
        self.music_player.current_mood = mood
        self.update_music_display()
        mood_emoji = {"Happy": "😊", "Energetic": "⚡", "Sad": "😢", 
                     "Melancholic": "😔", "Romantic": "❤️", "Chill": "😌", "All": "🎵"}
        self.sort_status.config(text=f"Mood: {mood_emoji.get(mood, '🎵')} {mood}")
    
    def update_music_display(self, highlight_indices=None):
        for item in self.music_tree.get_children():
            self.music_tree.delete(item)
        
        filtered_music = self.music_player.get_filtered_music()
        
        for i, song in enumerate(filtered_music):
            mood_tag = song.mood
            if highlight_indices and i in highlight_indices:
                if highlight_indices[i] == 'comparing':
                    mood_tag = 'comparing'
                elif highlight_indices[i] == 'swapping':
                    mood_tag = 'swapping'
            
            self.music_tree.insert('', 'end', text=song.title,
                                  values=(song.artist, song.mood, 
                                         f"{song.energy}%", f"{song.valence}%", 
                                         song.duration),
                                  tags=(mood_tag,))
    
    def start_sorting(self):
        if self.sorting_manager.is_sorting:
            return
        
        algorithm = self.sort_var.get()
        criteria = self.sort_criteria.get()
        
        filtered_music_dicts = [song.to_dict() for song in self.music_player.get_filtered_music()]
        self.sorting_manager.sort_music(algorithm, criteria, filtered_music_dicts)
        
        def update_library():
            filtered_music = [Song.from_dict(song_dict) for song_dict in filtered_music_dicts]
            if self.music_player.current_mood == "All":
                self.music_player.music_library = filtered_music
            else:
                for i, song in enumerate(self.music_player.music_library):
                    if song.mood == self.music_player.current_mood:
                        for sorted_song in filtered_music:
                            if sorted_song.title == song.title:
                                self.music_player.music_library[i] = sorted_song
                                break
        
        self.root.after(100, update_library)
    
    def update_sort_stats(self, comparisons, swaps):
        self.comparisons_label.config(text=f"Comparisons: {comparisons}")
        self.swaps_label.config(text=f"Swaps: {swaps}")
    
    def play_selected_song(self, event=None):
        selection = self.music_tree.selection()
        if selection:
            item = self.music_tree.item(selection[0])
            song_title = item['text']
            
            filtered_music = self.music_player.get_filtered_music()
            for i, song in enumerate(filtered_music):
                if song.title == song_title:
                    self.music_player.current_playlist = filtered_music
                    self.music_player.current_song_index = i
                    self.music_player.is_playing = True
                    self.play_current_song()
                    break
    
    def play_current_song(self):
        song = self.music_player.get_current_song()
        if song:
            self.current_song_label.config(text=song.title)
            self.current_artist_label.config(text=song.artist)
            self.music_player.is_playing = True
            self.play_button.config(text="⏸️")
            self.update_queue_display()
    
    def toggle_play(self):
        if self.music_player.is_playing:
            self.music_player.is_playing = False
            self.play_button.config(text="▶️")
        else:
            if self.music_player.current_playlist:
                self.music_player.is_playing = True
                self.play_button.config(text="⏸️")
    
    def next_song(self):
        song = self.music_player.next_song()
        if song:
            self.play_current_song()
    
    def previous_song(self):
        song = self.music_player.previous_song()
        if song:
            self.play_current_song()
    
    def show_context_menu(self, event):
        self.context_menu.post(event.x_root, event.y_root)
    
    def add_to_playlist_dialog(self):
        selection = self.music_tree.selection()
        if not selection:
            return
        
        playlist_window = tk.Toplevel(self.root)
        playlist_window.title("Add to Playlist")
        playlist_window.geometry("300x200")
        playlist_window.configure(bg='#2d2d2d')
        
        tk.Label(playlist_window, text="Select Playlist:", 
                fg='#ffffff', bg='#2d2d2d', font=('Arial', 12)).pack(pady=10)
        
        playlist_var = tk.StringVar()
        playlist_combo = ttk.Combobox(playlist_window, textvariable=playlist_var, 
                                     values=list(self.music_player.playlists.keys()))
        playlist_combo.pack(pady=10)
        
        def add_song():
            playlist_name = playlist_var.get()
            if playlist_name in self.music_player.playlists:
                item = self.music_tree.item(selection[0])
                song_title = item['text']
                
                for song in self.music_player.music_library:
                    if song.title == song_title:
                        if self.music_player.add_to_playlist(playlist_name, song):
                            messagebox.showinfo("Success", f"Added '{song_title}' to '{playlist_name}'")
                        else:
                            messagebox.showwarning("Warning", "Song already in playlist")
                        break
                
                playlist_window.destroy()
        
        tk.Button(playlist_window, text="Add Song", command=add_song,
                 bg='#27ae60', fg='white', font=('Arial', 10)).pack(pady=20)
    
    def add_to_queue(self):
        selection = self.music_tree.selection()
        if selection:
            item = self.music_tree.item(selection[0])
            song_title = item['text']
            
            for song in self.music_player.music_library:
                if song.title == song_title:
                    if not self.music_player.current_playlist:
                        self.music_player.current_playlist = []
                    self.music_player.current_playlist.append(song)
                    self.update_queue_display()
                    break
    
    def play_from_queue(self, event):
        selection = self.queue_listbox.curselection()
        if selection:
            self.music_player.current_song_index = selection[0]
            self.play_current_song()
    
    def update_queue_display(self):
        self.queue_listbox.delete(0, tk.END)
        for i, song in enumerate(self.music_player.current_playlist):
            prefix = "▶️ " if i == self.music_player.current_song_index and self.music_player.is_playing else ""
            self.queue_listbox.insert(tk.END, f"{prefix}{song.title} - {song.artist}")
    
    def create_playlist(self):
        playlist_window = tk.Toplevel(self.root)
        playlist_window.title("Create New Playlist")
        playlist_window.geometry("300x150")
        playlist_window.configure(bg='#2d2d2d')
        
        tk.Label(playlist_window, text="Playlist Name:", 
                fg='#ffffff', bg='#2d2d2d', font=('Arial', 12)).pack(pady=10)
        
        name_entry = tk.Entry(playlist_window, font=('Arial', 12), width=25)
        name_entry.pack(pady=10)
        name_entry.focus()
        
        def create():
            name = name_entry.get().strip()
            if name and self.music_player.create_playlist(name):
                self.update_playlist_display()
                messagebox.showinfo("Success", f"Created playlist '{name}'")
                playlist_window.destroy()
            elif name in self.music_player.playlists:
                messagebox.showerror("Error", "Playlist already exists")
            else:
                messagebox.showerror("Error", "Please enter a valid name")
        
        tk.Button(playlist_window, text="Create", command=create,
                 bg='#27ae60', fg='white', font=('Arial', 10)).pack(pady=10)
        
        name_entry.bind('<Return>', lambda e: create())
    
    def update_playlist_display(self):
        self.playlist_listbox.delete(0, tk.END)
        for name, playlist in self.music_player.playlists.items():
            self.playlist_listbox.insert(tk.END, f"{name} ({len(playlist.songs)} songs)")
    
    def on_playlist_select(self, event):
        selection = self.playlist_listbox.curselection()
        if selection:
            playlist_text = self.playlist_listbox.get(selection[0])
            playlist_name = playlist_text.split(" (")[0]
            
            if playlist_name in self.music_player.playlists:
                self.music_player.current_playlist = self.music_player.playlists[playlist_name].songs.copy()
                self.music_player.current_song_index = 0
                self.update_queue_display()
                
                if self.music_player.current_playlist:
                    response = messagebox.askyesno("Play Playlist", 
                                                 f"Play '{playlist_name}' playlist now?")
                    if response:
                        self.play_current_song()
    
    def save_playlists(self):
        if self.music_player.save_playlists():
            messagebox.showinfo("Success", "Playlists saved successfully!")
        else:
            messagebox.showerror("Error", "Failed to save playlists")