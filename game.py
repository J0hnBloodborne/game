import tkinter as tk
import random
import winsound
from tkinter import messagebox

class Player:
    def __init__(self, name):
        self.name = name
        self.health = 150
        self.attack_power = 35
        self.healing_potions = 3
        self.coins = 0
        self.fireball_charges = 0

    def heal(self):
        if self.healing_potions > 0:
            heal_amount = random.randint(25, 40)
            self.health += heal_amount
            self.healing_potions -= 1
            return heal_amount
        else:
            return "No Potions"

    def buy_healing_potion(self):
        if self.coins >= 10:
            self.coins -= 10
            self.healing_potions += 1
            return True
        return False

    def buy_fireball(self):
        if self.coins >= 20:
            self.coins -= 20
            self.fireball_charges += 1
            return True
        return False

class Enemy:
    def __init__(self, name, art, health, attack_power):
        self.name = name
        self.health = health
        self.attack_power = attack_power
        self.art = art

    def attack(self, player):
        damage = random.randint(5, self.attack_power)
        player.health -= damage
        return damage

    def drop_coins(self):
        if self.name == "Goblin":
            return random.randint(5, 10)
        elif self.name == "Orc":
            return random.randint(10, 15)
        elif self.name == "Troll":
            return random.randint(15, 20)
        else:
            return random.randint(5, 10)

class DungeonGameGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Dungeon Master RPG")
        self.root.geometry("800x550")

        self.player = None
        self.enemy = None
        self.score = 0
        self.swinging = False
        self.swing_direction = 1
        self.swing_position = 10
        self.target_range = 30

        # UI Elements
        self.intro_label = tk.Label(root, text="Welcome to the Dungeon RPG!", font=("Helvetica", 18))
        self.intro_label.pack(pady=10)

        self.name_label = tk.Label(root, text="Enter your name:")
        self.name_label.pack()

        self.name_entry = tk.Entry(root, font=("Helvetica", 14))
        self.name_entry.pack()

        self.start_button = tk.Button(root, text="Start Game", command=self.start_game, bg="lightgreen")
        self.start_button.pack(pady=10)

        self.stats_frame = tk.Frame(root)
        self.player_stats_label = tk.Label(self.stats_frame, text="", font=("Helvetica", 12))
        self.enemy_stats_label = tk.Label(self.stats_frame, text="", font=("Courier", 12))
        self.player_stats_label.grid(row=0, column=0, padx=10)
        self.enemy_stats_label.grid(row=0, column=1, padx=10)

        self.status_label = tk.Label(root, text="", font=("Helvetica", 14), wraplength=600)
        self.status_label.pack(pady=10)

        self.score_label = tk.Label(root, text="Score: 0", font=("Helvetica", 14))
        self.score_label.pack(pady=5)

        self.swing_canvas = tk.Canvas(root, width=300, height=50, bg="white")
        self.swing_bar = self.swing_canvas.create_rectangle(10, 15, 20, 35, fill="#0000FF", width=0)
        self.target_zone = self.swing_canvas.create_rectangle(140, 10, 160, 40, fill="red")
        self.swing_canvas.pack(pady=10)

        self.controls_label = tk.Label(root, text="Controls:\nAttack: Z\nHeal: H\nFireball: X", font=("Helvetica", 12))
        self.controls_label.pack(side=tk.RIGHT, padx=20)

        root.bind("<z>", self.check_timing)
        root.bind("<x>", self.use_fireball)

        self.action_frame = tk.Frame(root)
        self.attack_button = tk.Button(self.action_frame, text="Attack", command=self.start_swing, bg="lightblue")
        self.heal_button = tk.Button(self.action_frame, text="Heal", command=self.heal, bg="lightgoldenrodyellow")
        self.fireball_button = tk.Button(self.action_frame, text="Fireball (20 Coins)", command=self.use_fireball, bg="orange")
        self.attack_button.grid(row=0, column=0, padx=5)
        self.heal_button.grid(row=0, column=1, padx=5)
        self.fireball_button.grid(row=0, column=2, padx=5)

    def start_game(self):
        name = self.name_entry.get()
        if not name:
            messagebox.showwarning("Warning", "Please enter your name!")
            return
        self.player = Player(name)
        self.status_label.config(text=f"Welcome {self.player.name}! Your adventure begins...")

        self.name_label.pack_forget()
        self.name_entry.pack_forget()
        self.start_button.pack_forget()

        self.action_frame.pack()
        self.stats_frame.pack()
        self.trigger_event()

    def trigger_event(self):
        if random.random() < 0.7:
            self.encounter_enemy()
        else:
            self.random_encounter()

    def encounter_enemy(self):
        enemy_data = [
            {"name": "Goblin", "art": "  /\\_/\\  \n ( o.o )\n  > ^ < ", "health": 80, "attack_power": 15},
            {"name": "Orc", "art": "  /\\_/\\  \n ( o.o )\n ( v v ) ", "health": 100, "attack_power": 20},
            {"name": "Troll", "art": " /\\_/\\\n  (._.)\n  /   \\", "health": 120, "attack_power": 25},
            {"name": "Skeleton", "art": " /\\_/\\\n ( x x )\n /   \\", "health": 90, "attack_power": 18},
            {"name": "Zombie", "art": " /\\_/\\\n (._.)\n /   \\", "health": 110, "attack_power": 22}
        ]
        enemy_choice = random.choice(enemy_data)
        self.enemy = Enemy(enemy_choice["name"], enemy_choice["art"], enemy_choice["health"], enemy_choice["attack_power"])
        self.status_label.config(text=f"An enemy {self.enemy.name} appears with {self.enemy.health} health!\n{self.enemy.art}")
        self.update_stats()

    def random_encounter(self):
        encounter_type = random.choice(["treasure", "nothing"])
        if encounter_type == "treasure":
            found_coins = random.randint(10, 20)
            self.player.coins += found_coins
            self.status_label.config(text=f"You found a treasure chest! You collected {found_coins} coins.")
        else:
            self.status_label.config(text="You encountered nothing of note...")

        self.update_stats()
        self.show_shop()

    def start_swing(self):
        if self.enemy:
            self.swinging = True
            self.swing_position = 10
            self.swing_direction = 1
            self.update_swing_bar()

    def update_swing_bar(self):
        if self.swinging:
            if self.swing_position <= 10:
                self.swing_direction = 1
            elif self.swing_position >= 290:
                self.swing_direction = -1

            self.swing_position += self.swing_direction * 6
            self.swing_canvas.coords(self.swing_bar, self.swing_position, 15, self.swing_position + 10, 35)

            self.root.after(16, self.update_swing_bar)

    def check_timing(self, event):
        if self.swinging:
            self.swinging = False
            swing_x1, _, swing_x2, _ = self.swing_canvas.coords(self.swing_bar)
            target_x1, _, target_x2, _ = self.swing_canvas.coords(self.target_zone)
            if target_x1 <= swing_x1 <= target_x2 or target_x1 <= swing_x2 <= target_x2:
                damage = self.player.attack_power
                self.status_label.config(text=f"Perfect hit! You dealt {damage} damage!")
            else:
                damage = int(self.player.attack_power * 0.5)
                self.status_label.config(text=f"Missed timing! You dealt only {damage} damage.")
            winsound.PlaySound("attack.wav", winsound.SND_ASYNC)
            self.enemy.health -= damage
            self.update_stats()
            if self.enemy.health <= 0:
                winsound.PlaySound("enemy_defeated.wav", winsound.SND_ASYNC)
                coins_dropped = self.enemy.drop_coins()
                self.player.coins += coins_dropped
                self.status_label.config(text=f"{self.enemy.name} has been defeated! You collected {coins_dropped} coins.")
                self.score += 10
                self.score_label.config(text=f"Score: {self.score}")
                self.enemy = None
                self.update_stats()
                self.show_shop()
            else:
                self.enemy_turn()

    def use_fireball(self, event):
        if self.player.fireball_charges > 0 and self.enemy:
            winsound.PlaySound("fireball.wav", winsound.SND_ASYNC)
            self.enemy.health = 0
            coins_dropped = self.enemy.drop_coins() * 2
            self.player.coins += coins_dropped
            self.status_label.config(text=f"You incinerated the {self.enemy.name} with a fireball! You collected {coins_dropped} coins.")
            self.player.fireball_charges -= 1
            self.score += 20
            self.score_label.config(text=f"Score: {self.score}")
            self.enemy = None
            self.update_stats()
            self.show_shop()
        else:
            self.status_label.config(text="You don't have any fireball charges left!")

    def heal(self):
        heal_amount = self.player.heal()
        if heal_amount == "No Potions":
            self.status_label.config(text="You're out of healing potions!")
        else:
            winsound.PlaySound("heal.wav", winsound.SND_ASYNC)
            self.status_label.config(text=f"You healed {heal_amount} health!")
        self.update_stats()

    def enemy_turn(self):
        damage = self.enemy.attack(self.player)
        self.status_label.config(text=f"The {self.enemy.name} attacks and deals {damage} damage!")
        self.update_stats()

    def update_stats(self):
        self.player_stats_label.config(text=f"{self.player.name} - Health: {self.player.health} | Potions: {self.player.healing_potions} | Coins: {self.player.coins} | Fireballs: {self.player.fireball_charges}")
        if self.enemy:
            self.enemy_stats_label.config(text=f"{self.enemy.name} - Health: {self.enemy.health}")
        else:
            self.enemy_stats_label.config(text="")

    def show_shop(self):
        shop_window = tk.Toplevel(self.root)
        shop_window.title("Dungeon Shop")

        tk.Label(shop_window, text="Welcome to the Dungeon Shop!").pack(pady=10)

        buy_potion_button = tk.Button(shop_window, text="Buy Healing Potion (10 Coins)", command=self.buy_healing_potion)
        buy_fireball_button = tk.Button(shop_window, text="Buy Fireball (20 Coins)", command=self.buy_fireball)
        buy_nothing_button = tk.Button(shop_window, text="Buy Nothing", command=self.on_shop_close(shop_window))
        buy_potion_button.pack(pady=5)
        buy_fireball_button.pack(pady=5)
        buy_nothing_button.pack(pady=5)

        shop_window.protocol("WM_DELETE_WINDOW", self.on_shop_close(shop_window))

    def buy_healing_potion(self):
        if self.player.buy_healing_potion():
            self.status_label.config(text="You bought a healing potion!")
        else:
            self.status_label.config(text="Not enough coins!")
        self.update_stats()

    def buy_fireball(self):
        if self.player.buy_fireball():
            self.status_label.config(text="You bought a fireball!")
        else:
            self.status_label.config(text="Not enough coins!")
        self.update_stats()

    def on_shop_close(self, shop_window):
        def close_shop():
            shop_window.destroy()
            self.trigger_event()
        return close_shop

if __name__ == "__main__":
    root = tk.Tk()
    game_gui = DungeonGameGUI(root)
    root.mainloop()
