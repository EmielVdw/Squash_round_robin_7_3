import tkinter as tk
from tkinter import ttk, messagebox
from collections import defaultdict
import json
import os

class RoundRobinTournament:
    def __init__(self, root):
        self.root = root
        self.root.title("Round Robin Tournament - 7 Players")
        self.root.geometry("1000x700")
        
        # Tournament data
        self.players = []
        self.matches = []
        self.scores = defaultdict(lambda: {'wins': 0, 'losses': 0, 'points_for': 0, 'points_against': 0})
        
        # Create main notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create tabs
        self.setup_tab = ttk.Frame(self.notebook)
        self.scores_tab = ttk.Frame(self.notebook)
        self.standings_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.setup_tab, text="Setup Players")
        self.notebook.add(self.scores_tab, text="Enter Scores")
        self.notebook.add(self.standings_tab, text="Standings")
        
        self.setup_players_tab()
        self.setup_scores_tab()
        self.setup_standings_tab()
        
        # Load saved data if exists
        self.load_data()
    
    def setup_players_tab(self):
        # Player names entry
        ttk.Label(self.setup_tab, text="Enter Player Names (7 players required):", 
                 font=('Arial', 12, 'bold')).pack(pady=10)
        
        self.player_entries = []
        for i in range(7):
            frame = ttk.Frame(self.setup_tab)
            frame.pack(fill='x', padx=20, pady=2)
            
            ttk.Label(frame, text=f"Player {i+1}:", width=10).pack(side='left')
            entry = ttk.Entry(frame, width=30)
            entry.pack(side='left', padx=(10, 0))
            self.player_entries.append(entry)
        
        # Save players button
        ttk.Button(self.setup_tab, text="Save Players", 
                  command=self.save_players).pack(pady=20)
        
        # Tournament info
        info_frame = ttk.LabelFrame(self.setup_tab, text="Tournament Information")
        info_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        info_text = """
Round Robin Tournament Rules:
• 7 players will play in a round robin format
• Each round consists of 3 matches
• Total rounds: 7 rounds (each player plays 6 matches)
• Scoring: Win = 1 point, Loss = 0 points
• Points for/against are tracked for tie-breaking
        """
        
        ttk.Label(info_frame, text=info_text, justify='left').pack(padx=10, pady=10)
    
    def setup_scores_tab(self):
        # Round selection
        round_frame = ttk.Frame(self.scores_tab)
        round_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(round_frame, text="Select Round:", font=('Arial', 12, 'bold')).pack(side='left')
        
        self.round_var = tk.StringVar()
        self.round_combo = ttk.Combobox(round_frame, textvariable=self.round_var, 
                                       state='readonly', width=10)
        self.round_combo.pack(side='left', padx=(10, 0))
        self.round_combo.bind('<<ComboboxSelected>>', self.on_round_selected)
        
        # Matches frame
        self.matches_frame = ttk.LabelFrame(self.scores_tab, text="Matches")
        self.matches_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Save scores button
        ttk.Button(self.scores_tab, text="Save Scores", 
                  command=self.save_scores).pack(pady=10)
    
    def setup_standings_tab(self):
        # Standings table
        self.standings_frame = ttk.LabelFrame(self.standings_tab, text="Current Standings")
        self.standings_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create treeview for standings
        columns = ('Rank', 'Player', 'Wins', 'Losses', 'Win%', 'Points For', 'Points Against', 'Point Diff')
        self.standings_tree = ttk.Treeview(self.standings_frame, columns=columns, show='headings')
        
        for col in columns:
            self.standings_tree.heading(col, text=col)
            self.standings_tree.column(col, width=100, anchor='center')
        
        # Scrollbar for standings
        scrollbar = ttk.Scrollbar(self.standings_frame, orient='vertical', command=self.standings_tree.yview)
        self.standings_tree.configure(yscrollcommand=scrollbar.set)
        
        self.standings_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Refresh button
        ttk.Button(self.standings_tab, text="Refresh Standings", 
                  command=self.update_standings).pack(pady=10)
    
    def save_players(self):
        self.players = []
        for entry in self.player_entries:
            name = entry.get().strip()
            if not name:
                messagebox.showerror("Error", "All player names must be filled!")
                return
            self.players.append(name)
        
        # Check for duplicate names
        if len(set(self.players)) != len(self.players):
            messagebox.showerror("Error", "Player names must be unique!")
            return
        
        # Generate matches for all rounds
        self.generate_matches()
        
        # Update round combo box
        self.update_round_combo()
        
        # Switch to scores tab
        self.notebook.select(self.scores_tab)
        
        messagebox.showinfo("Success", "Players saved successfully!")
        self.save_data()
    
    def generate_matches(self):
        """Generate all matches for the round robin tournament"""
        self.matches = []
        n = len(self.players)
        
        # Round robin algorithm
        for round_num in range(n - 1):
            round_matches = []
            # Create 3 matches per round (since we have 7 players)
            for match_num in range(3):
                if match_num == 0:
                    # First match: player 0 vs player (n-1-round_num)
                    p1 = 0
                    p2 = (n - 1 - round_num) % n
                elif match_num == 1:
                    # Second match: player 1 vs player (n-2-round_num)
                    p1 = 1
                    p2 = (n - 2 - round_num) % n
                else:
                    # Third match: player 2 vs player (n-3-round_num)
                    p1 = 2
                    p2 = (n - 3 - round_num) % n
                
                # Skip if same player
                if p1 == p2:
                    continue
                
                round_matches.append({
                    'round': round_num + 1,
                    'match': match_num + 1,
                    'player1': self.players[p1],
                    'player2': self.players[p2],
                    'score1': 0,
                    'score2': 0,
                    'completed': False
                })
            
            self.matches.extend(round_matches)
    
    def update_round_combo(self):
        """Update the round selection combo box"""
        rounds = list(set([match['round'] for match in self.matches]))
        rounds.sort()
        self.round_combo['values'] = rounds
        if rounds:
            self.round_var.set(rounds[0])
            self.on_round_selected()
    
    def on_round_selected(self, event=None):
        """Handle round selection change"""
        if not self.round_var.get():
            return
        
        selected_round = int(self.round_var.get())
        
        # Clear existing match widgets
        for widget in self.matches_frame.winfo_children():
            widget.destroy()
        
        # Get matches for selected round
        round_matches = [match for match in self.matches if match['round'] == selected_round]
        
        # Create match entry widgets
        self.match_widgets = []
        for i, match in enumerate(round_matches):
            match_frame = ttk.Frame(self.matches_frame)
            match_frame.pack(fill='x', padx=10, pady=5)
            
            ttk.Label(match_frame, text=f"Match {match['match']}:", 
                     font=('Arial', 10, 'bold')).pack(side='left')
            
            ttk.Label(match_frame, text=f"{match['player1']} vs {match['player2']}", 
                     width=30).pack(side='left', padx=(10, 0))
            
            ttk.Label(match_frame, text="Score:").pack(side='left', padx=(10, 0))
            
            score1_var = tk.StringVar(value=str(match['score1']))
            score2_var = tk.StringVar(value=str(match['score2']))
            
            score1_entry = ttk.Entry(match_frame, textvariable=score1_var, width=5)
            score1_entry.pack(side='left', padx=(5, 0))
            
            ttk.Label(match_frame, text="-").pack(side='left', padx=(5, 0))
            
            score2_entry = ttk.Entry(match_frame, textvariable=score2_var, width=5)
            score2_entry.pack(side='left', padx=(5, 0))
            
            self.match_widgets.append({
                'match': match,
                'score1_var': score1_var,
                'score2_var': score2_var
            })
    
    def save_scores(self):
        """Save scores for the current round"""
        if not hasattr(self, 'match_widgets'):
            messagebox.showerror("Error", "No matches to save!")
            return
        
        # Validate and save scores
        for widget in self.match_widgets:
            try:
                score1 = int(widget['score1_var'].get())
                score2 = int(widget['score2_var'].get())
                
                if score1 < 0 or score2 < 0:
                    messagebox.showerror("Error", "Scores cannot be negative!")
                    return
                
                # Update match data
                match = widget['match']
                match['score1'] = score1
                match['score2'] = score2
                match['completed'] = True
                
                # Update player scores
                self.update_player_scores(match)
                
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers for all scores!")
                return
        
        messagebox.showinfo("Success", "Scores saved successfully!")
        self.update_standings()
        self.save_data()
    
    def update_player_scores(self, match):
        """Update player statistics based on match result"""
        player1 = match['player1']
        player2 = match['player2']
        score1 = match['score1']
        score2 = match['score2']
        
        # Update points for/against
        self.scores[player1]['points_for'] += score1
        self.scores[player1]['points_against'] += score2
        self.scores[player2]['points_for'] += score2
        self.scores[player2]['points_against'] += score1
        
        # Update wins/losses
        if score1 > score2:
            self.scores[player1]['wins'] += 1
            self.scores[player2]['losses'] += 1
        elif score2 > score1:
            self.scores[player2]['wins'] += 1
            self.scores[player1]['losses'] += 1
        # If tied, no wins/losses added
    
    def update_standings(self):
        """Update the standings display"""
        # Clear existing standings
        for item in self.standings_tree.get_children():
            self.standings_tree.delete(item)
        
        if not self.players:
            return
        
        # Calculate standings
        standings = []
        for player in self.players:
            stats = self.scores[player]
            wins = stats['wins']
            losses = stats['losses']
            total_games = wins + losses
            win_pct = (wins / total_games * 100) if total_games > 0 else 0
            point_diff = stats['points_for'] - stats['points_against']
            
            standings.append({
                'player': player,
                'wins': wins,
                'losses': losses,
                'win_pct': win_pct,
                'points_for': stats['points_for'],
                'points_against': stats['points_against'],
                'point_diff': point_diff
            })
        
        # Sort by wins, then by point difference
        standings.sort(key=lambda x: (-x['wins'], -x['point_diff']))
        
        # Add to treeview
        for i, standing in enumerate(standings, 1):
            self.standings_tree.insert('', 'end', values=(
                i,
                standing['player'],
                standing['wins'],
                standing['losses'],
                f"{standing['win_pct']:.1f}%",
                standing['points_for'],
                standing['points_against'],
                standing['point_diff']
            ))
    
    def save_data(self):
        """Save tournament data to file"""
        data = {
            'players': self.players,
            'matches': self.matches,
            'scores': dict(self.scores)
        }
        
        try:
            with open('tournament_data.json', 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def load_data(self):
        """Load tournament data from file"""
        if os.path.exists('tournament_data.json'):
            try:
                with open('tournament_data.json', 'r') as f:
                    data = json.load(f)
                
                self.players = data.get('players', [])
                self.matches = data.get('matches', [])
                
                # Convert scores back to defaultdict
                scores_data = data.get('scores', {})
                self.scores = defaultdict(lambda: {'wins': 0, 'losses': 0, 'points_for': 0, 'points_against': 0})
                for player, stats in scores_data.items():
                    self.scores[player] = stats
                
                # Update UI
                if self.players:
                    for i, player in enumerate(self.players):
                        if i < len(self.player_entries):
                            self.player_entries[i].insert(0, player)
                    
                    self.update_round_combo()
                    self.update_standings()
                    
            except Exception as e:
                print(f"Error loading data: {e}")

def main():
    root = tk.Tk()
    app = RoundRobinTournament(root)
    root.mainloop()

if __name__ == "__main__":
    main()
