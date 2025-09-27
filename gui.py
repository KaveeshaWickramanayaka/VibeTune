import tkinter as tk
from tkinter import ttk, messagebox
from core import MusicPlayer, SortingManager, Song

class MoodMusicPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Mood Music Player - Sorting Algorithm Demo")
        self.root.geometry("1200x900")  # Increased height from 800 to 900
        self.root.configure(bg='#1a1a1a')
        
        self.music_player = MusicPlayer()
        self.sorting_manager = SortingManager(
            update_callback=self.update_music_display,
            stats_callback=self.update_sort_stats
        )
        
        self.is_sorting = False
        self.sort_comparisons = 0
        self.sort_swaps = 0
        self.selected_playlist = None
        
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
                                  font=('Arial', 10, 'bold'), fg='#ffffff', bg='#2d2d2d')
        mood_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Create mood dropdown instead of buttons
        mood_container = tk.Frame(mood_frame, bg='#2d2d2d')
        mood_container.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(mood_container, text="Current Mood:", fg='#ffffff', bg='#2d2d2d', 
                font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
        
        self.mood_var = tk.StringVar(value="All")
        moods = ["All", "Happy", "Energetic", "Sad", "Melancholic", "Romantic", "Chill"]
        
        mood_dropdown = ttk.Combobox(mood_container, textvariable=self.mood_var, 
                                   values=moods, state="readonly", width=15)
        mood_dropdown.pack(side=tk.RIGHT, padx=5)
        mood_dropdown.bind('<<ComboboxSelected>>', lambda e: self.select_mood(self.mood_var.get()))
        
        sorting_frame = tk.LabelFrame(left_panel, text="🔧 Sorting Options", 
                                     font=('Arial', 10, 'bold'), fg='#ffffff', bg='#2d2d2d')
        sorting_frame.pack(fill=tk.X, padx=10, pady=3)  # Reduced padding from 5 to 3
        
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
                                   font=('Arial', 10, 'bold'), fg='#ffffff', bg='#2d2d2d')
        stats_frame.pack(fill=tk.X, padx=10, pady=3)  # Reduced padding from 5 to 3
        
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
                                      font=('Arial', 10, 'bold'), fg='#ffffff', bg='#2d2d2d')
        playlist_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=3)  # Reduced padding from 5 to 3
        
        playlist_controls = tk.Frame(playlist_frame, bg='#2d2d2d')
        playlist_controls.pack(fill=tk.X, padx=5, pady=5)
        
        # First row of buttons
        controls_row1 = tk.Frame(playlist_controls, bg='#2d2d2d')
        controls_row1.pack(fill=tk.X, pady=2)
        
        tk.Button(controls_row1, text="➕ New", command=self.create_playlist,
                 bg='#27ae60', fg='white', font=('Arial', 8)).pack(side=tk.LEFT, padx=1)
        tk.Button(controls_row1, text="🗑️ Del", command=self.delete_playlist,
                 bg='#e74c3c', fg='white', font=('Arial', 8)).pack(side=tk.LEFT, padx=1)
        tk.Button(controls_row1, text="✏️ Rename", command=self.rename_playlist,
                 bg='#f39c12', fg='white', font=('Arial', 8)).pack(side=tk.LEFT, padx=1)
        
        # Second row of buttons
        controls_row2 = tk.Frame(playlist_controls, bg='#2d2d2d')
        controls_row2.pack(fill=tk.X, pady=2)
        
        tk.Button(controls_row2, text="👁️ View Songs", command=self.view_selected_playlist,
                 bg='#9b59b6', fg='white', font=('Arial', 8)).pack(side=tk.LEFT, padx=1)
        tk.Button(controls_row2, text="💾 Save", command=self.save_playlists,
                 bg='#3498db', fg='white', font=('Arial', 8)).pack(side=tk.LEFT, padx=1)
        
        self.playlist_listbox = tk.Listbox(playlist_frame, bg='#404040', fg='#ffffff', 
                                          font=('Arial', 9), selectbackground='#3498db', 
                                          height=8)  # Increased from 5 to 8 due to saved space
        
        # Add scrollbar for playlist listbox
        playlist_scrollbar = ttk.Scrollbar(playlist_frame)
        playlist_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.playlist_listbox.config(yscrollcommand=playlist_scrollbar.set)
        playlist_scrollbar.config(command=self.playlist_listbox.yview)
        
        self.playlist_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.playlist_listbox.bind('<<ListboxSelect>>', self.on_playlist_select)
        
        playlist_stats_frame = tk.Frame(playlist_frame, bg='#2d2d2d')
        playlist_stats_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.playlist_stats_label = tk.Label(playlist_stats_frame, text="Select a playlist", 
                                           fg='#cccccc', bg='#2d2d2d', font=('Arial', 9))
        self.playlist_stats_label.pack()
        
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
        
        self.music_tree['columns'] = ('artist', 'mood', 'energy', 'valence', 'duration', 'liked')
        self.music_tree.column('#0', width=200, minwidth=150)
        self.music_tree.column('artist', width=150, minwidth=100)
        self.music_tree.column('mood', width=100, minwidth=80)
        self.music_tree.column('energy', width=80, minwidth=60)
        self.music_tree.column('valence', width=80, minwidth=60)
        self.music_tree.column('duration', width=80, minwidth=60)
        self.music_tree.column('liked', width=60, minwidth=40)
        
        self.music_tree.heading('#0', text='Song Title', anchor=tk.W)
        self.music_tree.heading('artist', text='Artist', anchor=tk.W)
        self.music_tree.heading('mood', text='Mood', anchor=tk.CENTER)
        self.music_tree.heading('energy', text='Energy', anchor=tk.CENTER)
        self.music_tree.heading('valence', text='Valence', anchor=tk.CENTER)
        self.music_tree.heading('duration', text='Duration', anchor=tk.CENTER)
        self.music_tree.heading('liked', text='❤️', anchor=tk.CENTER)
        
        self.music_tree.tag_configure('Happy', background='#f1c40f', foreground='#000000')
        self.music_tree.tag_configure('Energetic', background='#e74c3c', foreground='#ffffff')
        self.music_tree.tag_configure('Sad', background='#3498db', foreground='#ffffff')
        self.music_tree.tag_configure('Melancholic', background='#9b59b6', foreground='#ffffff')
        self.music_tree.tag_configure('comparing', background='#f39c12', foreground='#000000')
        self.music_tree.tag_configure('swapping', background='#e67e22', foreground='#ffffff')
        self.music_tree.tag_configure('liked', background='#e74c3c', foreground='#ffffff')
        
        self.music_tree.bind('<Double-1>', self.play_selected_song)
        self.music_tree.bind('<Button-3>', self.show_context_menu)
        # Alternative binding for Windows
        self.music_tree.bind('<Button-2>', self.show_context_menu)  # Middle click as backup
        # Add keyboard shortcut for liking songs
        self.root.bind('<Control-l>', lambda e: self.toggle_like_song())
        self.root.bind('<Control-p>', lambda e: self.add_to_playlist_dialog())
        
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
        self.context_menu.add_command(label="❤️ Like/Unlike", command=self.toggle_like_song)
        self.context_menu.add_command(label="Add to Playlist", command=self.add_to_playlist_dialog)
        self.context_menu.add_command(label="Play Now", command=self.play_selected_song)
        self.context_menu.add_command(label="Add to Queue", command=self.add_to_queue)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="View Song Info", command=self.show_song_info)
        
        # Add keyboard shortcuts info to context menu
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Keyboard Shortcuts: Ctrl+L (Like), Ctrl+P (Add to Playlist)", state='disabled')
    
    def select_mood(self, mood):
        self.music_player.current_mood = mood
        self.mood_var.set(mood)  # Update dropdown selection
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
            
            liked_status = "❤️" if self.music_player.is_song_liked(song) else ""
            
            self.music_tree.insert('', 'end', text=song.title,
                                  values=(song.artist, song.mood, 
                                         f"{song.energy}%", f"{song.valence}%", 
                                         song.duration, liked_status),
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
            self.update_music_display()
        
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
        print(f"DEBUG: Right-click detected at ({event.x_root}, {event.y_root})")
        selection = self.music_tree.selection()
        print(f"DEBUG: Selection: {selection}")
        if selection:
            print("DEBUG: Showing context menu")
            self.context_menu.post(event.x_root, event.y_root)
        else:
            print("DEBUG: No selection, context menu not shown")
    
    def toggle_like_song(self):
        print("DEBUG: toggle_like_song called")
        selection = self.music_tree.selection()
        print(f"DEBUG: Current selection: {selection}")
        if selection:
            item = self.music_tree.item(selection[0])
            song_title = item['text']
            song_artist = item['values'][0] if item['values'] else "Unknown"
            print(f"DEBUG: Song title: '{song_title}', Artist: '{song_artist}'")
            
            # Find the song in the music library
            found_song = None
            for song in self.music_player.music_library:
                if song.title == song_title and song.artist == song_artist:
                    found_song = song
                    print(f"DEBUG: Found matching song: {song.title} by {song.artist}")
                    break
            
            if found_song:
                was_liked = self.music_player.is_song_liked(found_song)
                print(f"DEBUG: Song was liked: {was_liked}")
                result = self.music_player.toggle_like_song(found_song)
                print(f"DEBUG: Toggle result: {result}")
                is_liked = self.music_player.is_song_liked(found_song)
                print(f"DEBUG: Song is now liked: {is_liked}")
                self.update_music_display()
                self.update_playlist_display()  # Update playlist display too
                messagebox.showinfo("Success", f"{'Liked' if is_liked else 'Unliked'} '{song_title}'")
            else:
                print(f"DEBUG: Song not found in library: {song_title} by {song_artist}")
                messagebox.showerror("Error", "Song not found in library")
        else:
            print("DEBUG: No selection found for toggle_like_song")
    
    def add_to_playlist_dialog(self):
        print("DEBUG: add_to_playlist_dialog called")
        selection = self.music_tree.selection()
        print(f"DEBUG: Current selection: {selection}")
        if not selection:
            print("DEBUG: No selection, returning early")
            return
        
        playlist_window = tk.Toplevel(self.root)
        playlist_window.title("Add to Playlist")
        playlist_window.geometry("300x200")
        playlist_window.configure(bg='#2d2d2d')
        
        tk.Label(playlist_window, text="Select Playlist:", 
                fg='#ffffff', bg='#2d2d2d', font=('Arial', 12)).pack(pady=10)
        
        playlist_var = tk.StringVar()
        available_playlists = list(self.music_player.playlists.keys())
        print(f"DEBUG: Available playlists: {available_playlists}")
        playlist_combo = ttk.Combobox(playlist_window, textvariable=playlist_var, 
                                     values=available_playlists)
        playlist_combo.pack(pady=10)
        
        def add_song():
            playlist_name = playlist_var.get()
            print(f"DEBUG: Selected playlist: {playlist_name}")
            if playlist_name in self.music_player.playlists:
                item = self.music_tree.item(selection[0])
                song_title = item['text']
                print(f"DEBUG: Song to add: {song_title}")
                
                for song in self.music_player.music_library:
                    if song.title == song_title:
                        print(f"DEBUG: Found matching song: {song.title}")
                        result = self.music_player.add_to_playlist(playlist_name, song)
                        print(f"DEBUG: Add result: {result}")
                        if result:
                            self.update_playlist_display()  # Update the playlist count display
                            messagebox.showinfo("Success", f"Added '{song_title}' to '{playlist_name}'")
                        else:
                            messagebox.showwarning("Warning", "Song already in playlist")
                        break
                
                playlist_window.destroy()
            else:
                print(f"DEBUG: Playlist '{playlist_name}' not found")
        
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
                    messagebox.showinfo("Success", f"Added '{song_title}' to queue")
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
        print("DEBUG: create_playlist called")
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
            print(f"DEBUG: Creating playlist with name: '{name}'")
            if name and self.music_player.create_playlist(name):
                print("DEBUG: Playlist created successfully")
                self.update_playlist_display()
                messagebox.showinfo("Success", f"Created playlist '{name}'")
                playlist_window.destroy()
            elif name in self.music_player.playlists:
                print("DEBUG: Playlist already exists")
                messagebox.showerror("Error", "Playlist already exists")
            else:
                print("DEBUG: Invalid name provided")
                messagebox.showerror("Error", "Please enter a valid name")
        
        tk.Button(playlist_window, text="Create", command=create,
                 bg='#27ae60', fg='white', font=('Arial', 10)).pack(pady=10)
        
        name_entry.bind('<Return>', lambda e: create())
    
    def delete_playlist(self):
        print("DEBUG: delete_playlist called")
        selection = self.playlist_listbox.curselection()
        print(f"DEBUG: Selection from listbox: {selection}")
        if selection:
            playlist_text = self.playlist_listbox.get(selection[0])
            print(f"DEBUG: Selected playlist text: '{playlist_text}'")
            # Extract playlist name properly - remove both emoji and song count
            if playlist_text.startswith("Liked Songs"):
                playlist_name = "Liked Songs"
            else:
                # For other playlists, extract name before the first space and opening parenthesis
                playlist_name = playlist_text.split(" (")[0]
            print(f"DEBUG: Extracted playlist name: '{playlist_name}'")
            
            if playlist_name == "Liked Songs":
                print("DEBUG: Cannot delete 'Liked Songs' playlist")
                messagebox.showerror("Error", "Cannot delete 'Liked Songs' playlist")
                return
                
            if messagebox.askyesno("Confirm Delete", f"Delete playlist '{playlist_name}'?"):
                print(f"DEBUG: User confirmed deletion of '{playlist_name}'")
                result = self.music_player.delete_playlist(playlist_name)
                print(f"DEBUG: Delete result: {result}")
                if result:
                    self.update_playlist_display()
                    messagebox.showinfo("Success", f"Deleted playlist '{playlist_name}'")
                else:
                    messagebox.showerror("Error", "Failed to delete playlist")
            else:
                print("DEBUG: User cancelled deletion")
        else:
            print("DEBUG: No playlist selected for deletion")
            messagebox.showwarning("Warning", "Please select a playlist to delete")
    
    def rename_playlist(self):
        selection = self.playlist_listbox.curselection()
        if selection:
            playlist_text = self.playlist_listbox.get(selection[0])
            # Extract playlist name properly - remove both emoji and song count
            if playlist_text.startswith("Liked Songs"):
                old_name = "Liked Songs"
            else:
                # For other playlists, extract name before the first space and opening parenthesis
                old_name = playlist_text.split(" (")[0]
            
            if old_name == "Liked Songs":
                messagebox.showerror("Error", "Cannot rename 'Liked Songs' playlist")
                return
            
            rename_window = tk.Toplevel(self.root)
            rename_window.title("Rename Playlist")
            rename_window.geometry("300x150")
            rename_window.configure(bg='#2d2d2d')
            
            tk.Label(rename_window, text="New Playlist Name:", 
                    fg='#ffffff', bg='#2d2d2d', font=('Arial', 12)).pack(pady=10)
            
            name_entry = tk.Entry(rename_window, font=('Arial', 12), width=25)
            name_entry.insert(0, old_name)
            name_entry.pack(pady=10)
            name_entry.select_range(0, tk.END)
            name_entry.focus()
            
            def rename():
                new_name = name_entry.get().strip()
                if new_name and new_name != old_name:
                    if self.music_player.rename_playlist(old_name, new_name):
                        self.update_playlist_display()
                        messagebox.showinfo("Success", f"Renamed playlist to '{new_name}'")
                        rename_window.destroy()
                    else:
                        messagebox.showerror("Error", "Playlist name already exists")
                else:
                    messagebox.showerror("Error", "Please enter a valid name")
            
            tk.Button(rename_window, text="Rename", command=rename,
                     bg='#f39c12', fg='white', font=('Arial', 10)).pack(pady=10)
            
            name_entry.bind('<Return>', lambda e: rename())
        else:
            messagebox.showwarning("Warning", "Please select a playlist to rename")
    
    def update_playlist_display(self):
        self.playlist_listbox.delete(0, tk.END)
        for name, playlist in self.music_player.playlists.items():
            song_count = len(playlist.songs)
            like_emoji = " ❤️" if name == "Liked Songs" else ""
            playlist_text = f"{name}{like_emoji} ({song_count} songs)"
            self.playlist_listbox.insert(tk.END, playlist_text)
        self.playlist_stats_label.config(text="Select a playlist to view stats")
    
    def on_playlist_select(self, event):
        selection = self.playlist_listbox.curselection()
        if selection:
            playlist_text = self.playlist_listbox.get(selection[0])
            # Extract playlist name properly - remove both emoji and song count
            if playlist_text.startswith("Liked Songs"):
                playlist_name = "Liked Songs"
            else:
                # For other playlists, extract name before the first space and opening parenthesis
                playlist_name = playlist_text.split(" (")[0]
            
            self.selected_playlist = playlist_name
            
            # Update stats
            stats = self.music_player.get_playlist_stats(playlist_name)
            if stats.get("total_songs", 0) > 0:
                stats_text = f"Songs: {stats['total_songs']} | Duration: {stats['total_duration']} | Avg Energy: {stats['average_energy']}%"
                self.playlist_stats_label.config(text=stats_text)
            else:
                self.playlist_stats_label.config(text="Empty playlist")
            
            # Show playlist contents in a new window
            self.show_playlist_contents(playlist_name)
    
    def show_song_info(self):
        selection = self.music_tree.selection()
        if selection:
            item = self.music_tree.item(selection[0])
            song_title = item['text']
            
            for song in self.music_player.music_library:
                if song.title == song_title:
                    info_window = tk.Toplevel(self.root)
                    info_window.title("Song Information")
                    info_window.geometry("300x250")
                    info_window.configure(bg='#2d2d2d')
                    
                    info_text = f"""
Title: {song.title}
Artist: {song.artist}
Mood: {song.mood}
Energy: {song.energy}%
Valence: {song.valence}%
Duration: {song.duration}
Liked: {'Yes ❤️' if self.music_player.is_song_liked(song) else 'No'}
"""
                    tk.Label(info_window, text=info_text, 
                            fg='#ffffff', bg='#2d2d2d', font=('Arial', 11),
                            justify=tk.LEFT).pack(pady=20, padx=20)
                    break
    
    def save_playlists(self):
        if self.music_player.save_playlists():
            messagebox.showinfo("Success", "Playlists saved successfully!")
        else:
            messagebox.showerror("Error", "Failed to save playlists")
    
    def show_playlist_contents(self, playlist_name):
        """Show playlist contents in a popup window"""
        
        # Get playlist songs
        playlist_songs = self.music_player.get_playlist_songs(playlist_name)
        
        # Create popup window
        playlist_window = tk.Toplevel(self.root)
        playlist_window.title(f"Playlist: {playlist_name}")
        playlist_window.geometry("600x400")
        playlist_window.configure(bg='#2d2d2d')
        
        # Header
        header_frame = tk.Frame(playlist_window, bg='#404040', height=50)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text=f"🎵 {playlist_name}", 
                font=('Arial', 14, 'bold'), fg='#ffffff', bg='#404040').pack(expand=True)
        
        # Create treeview for songs
        tree_frame = tk.Frame(playlist_window, bg='#2d2d2d')
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Scrollbars
        scrollbar_y = ttk.Scrollbar(tree_frame)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview
        playlist_tree = ttk.Treeview(tree_frame, yscrollcommand=scrollbar_y.set, style='Custom.Treeview')
        playlist_tree.pack(fill=tk.BOTH, expand=True)
        scrollbar_y.config(command=playlist_tree.yview)
        
        # Configure columns
        playlist_tree['columns'] = ('artist', 'mood', 'energy', 'valence', 'duration')
        playlist_tree.column('#0', width=180, minwidth=150)
        playlist_tree.column('artist', width=120, minwidth=100)
        playlist_tree.column('mood', width=80, minwidth=70)
        playlist_tree.column('energy', width=60, minwidth=50)
        playlist_tree.column('valence', width=60, minwidth=50)
        playlist_tree.column('duration', width=60, minwidth=50)
        
        # Configure headers
        playlist_tree.heading('#0', text='Song Title', anchor=tk.W)
        playlist_tree.heading('artist', text='Artist', anchor=tk.W)
        playlist_tree.heading('mood', text='Mood', anchor=tk.CENTER)
        playlist_tree.heading('energy', text='Energy', anchor=tk.CENTER)
        playlist_tree.heading('valence', text='Valence', anchor=tk.CENTER)
        playlist_tree.heading('duration', text='Duration', anchor=tk.CENTER)
        
        # Add songs to treeview
        if playlist_songs:
            for song in playlist_songs:
                playlist_tree.insert('', 'end', text=song.title,
                                   values=(song.artist, song.mood, 
                                          f"{song.energy}%", f"{song.valence}%", 
                                          song.duration),
                                   tags=(song.mood,))
        else:
            # Show empty message
            playlist_tree.insert('', 'end', text="No songs in this playlist",
                               values=("", "", "", "", ""))
        
        # Buttons frame
        button_frame = tk.Frame(playlist_window, bg='#2d2d2d')
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Close button
        tk.Button(button_frame, text="Close", command=playlist_window.destroy,
                 bg='#95a5a6', fg='white', font=('Arial', 10)).pack(side=tk.RIGHT, padx=5)
        
        # Remove song button (if songs exist)
        if playlist_songs:
            def remove_selected_song():
                selection = playlist_tree.selection()
                if selection:
                    item = playlist_tree.item(selection[0])
                    song_title = item['text']
                    song_artist = item['values'][0] if item['values'] else ""
                    
                    # Find and remove the song
                    for song in playlist_songs:
                        if song.title == song_title and song.artist == song_artist:
                            if self.music_player.remove_from_playlist(playlist_name, song):
                                playlist_window.destroy()
                                self.update_playlist_display()
                                messagebox.showinfo("Success", f"Removed '{song_title}' from '{playlist_name}'")
                            else:
                                messagebox.showerror("Error", "Failed to remove song")
                            break
                else:
                    messagebox.showwarning("Warning", "Please select a song to remove")
            
            tk.Button(button_frame, text="Remove Selected", command=remove_selected_song,
                     bg='#e74c3c', fg='white', font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
    
    def view_selected_playlist(self):
        """View songs in the selected playlist"""
        selection = self.playlist_listbox.curselection()
        if selection:
            playlist_text = self.playlist_listbox.get(selection[0])
            # Extract playlist name properly - remove both emoji and song count
            if playlist_text.startswith("Liked Songs"):
                playlist_name = "Liked Songs"
            else:
                # For other playlists, extract name before the first space and opening parenthesis
                playlist_name = playlist_text.split(" (")[0]
            self.show_playlist_contents(playlist_name)
        else:
            messagebox.showwarning("Warning", "Please select a playlist to view")