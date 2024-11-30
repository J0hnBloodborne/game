import tkinter as tk
import random
import winsound

class Player:
    def __init__(self, name):
        self.name = name
        self.health = 150
        self.attack_power = 35
        self.healing_potions = 3
        self.coins = 0
        self.fireball_charges = 0
        self.level = 1
        self.xp = 0
        self.shield_active = False  # Tracks Shield of Denial effect
        self.strength_potions = 0
        self.strength_potion_effect = 0  # Tracks Strength Potion duration

    def gain_xp(self, amount):
        self.xp += amount
        if self.xp >= self.level * 100:  # Level-up threshold
            self.xp -= self.level * 100
            self.level += 1
            self.health *= 1.2  # Increase health on level-up
            self.attack_power *= 1.2  # Increase attack power on level-up
            return True
        return False

    def heal(self):  # Retain original functionality for internal calls
        if self.healing_potions > 0:
            heal_amount = random.randint(25, 40)
            self.health += heal_amount
            self.healing_potions -= 1
            return heal_amount
        else:
            return "No Potions"

class Enemy:
    def __init__(self, name, art, health, attack_power):
        self.name = name
        self.art = art
        self.health = health
        self.attack_power = attack_power

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
        elif self.name == "Skeleton":
            return random.randint(8, 12)
        elif self.name == "Zombie":
            return random.randint(12, 18)
        elif self.name == "Dragon":
            return random.randint(20, 30)
        elif self.name == "Demon":
            return random.randint(20, 30)
        else:
            return random.randint(5, 10)


class DungeonGameGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Dungeon Master RPG")
        self.root.geometry("1000x1000")
        self.encounter_count = 0
        self.player = None
        self.enemy = None
        self.score = 0
        self.swinging = False
        self.swing_direction = 1
        self.swing_position = 10
        self.target_range = 45
        self.encounter_ongoing = False
        self.dodge_count = 0
        self.countdown_value = 0

        self.intro_label = tk.Label(
            root, text="Welcome to the Dungeon RPG!", font=("Helvetica", 18)
        )
        self.intro_label.pack(pady=10)

        self.name_label = tk.Label(root, text="Enter your name:")
        self.name_label.pack()

        self.name_entry = tk.Entry(root, font=("Helvetica", 14))
        self.name_entry.pack()

        self.start_button = tk.Button(
            root, text="Start Game", command=self.start_game, bg="lightgreen"
        )
        self.start_button.pack(pady=10)

        self.stats_frame = tk.Frame(root)
        self.player_stats_label = tk.Label(
            self.stats_frame, text="", font=("Helvetica", 12)
        )
        self.enemy_stats_label = tk.Label(
            self.stats_frame, text="", font=("Courier", 12)
        )
        self.player_stats_label.grid(row=0, column=0, padx=10)
        self.enemy_stats_label.grid(row=0, column=1, padx=10)

        self.status_label = tk.Label(
            root, text="", font=("Helvetica", 14), wraplength=800
        )
        self.status_label.pack(pady=10)

        self.score_label = tk.Label(root, text="Score: 0", font=("Helvetica", 14))
        self.score_label.pack(pady=5)

        self.swing_canvas = tk.Canvas(root, width=400, height=100, bg="white")
        self.target_zone = self.swing_canvas.create_rectangle(
            140, 15, 210, 85, fill="red", state="hidden"
        )
        self.perfect_zone = self.swing_canvas.create_rectangle(
            170, 25, 180, 75, fill="#52D305", outline="", state="hidden"
        )
        self.swing_bar = self.swing_canvas.create_rectangle(
            13, 30, 17, 70, fill="#0000FF", width=0, outline="", state="hidden"
        )
        self.dodge_zone = self.swing_canvas.create_rectangle(
            0, 15, 50, 30, fill="red", state="hidden"
        )
        self.swing_canvas.pack(pady=10)

        self.controls_label = tk.Label(
            root,
            text="Controls:\nAttack: Z\nDodge: D\nFireball: X",
            font=("Helvetica", 12),
        )
        self.controls_label.pack(side=tk.RIGHT, padx=20)

        self.action_frame = tk.Frame(root)
        self.attack_button = tk.Button(
            self.action_frame, text="Attack", command=self.start_swing, bg="lightblue"
        )
        self.use_item_button = tk.Button(
            self.action_frame, text="Use Item", command=self.use_item, bg="lightgoldenrodyellow"
        )
        self.shop_button = tk.Button(
            self.action_frame,
            text="Shop",
            command=self.show_shop,
            state="disabled",
            bg="grey",
        )
        self.skip_button = tk.Button(
            self.action_frame,
            text="Continue",
            command=self.continue_encounter,
            state="disabled",
            bg="grey",
        )
        self.attack_button.grid(row=0, column=0, padx=5)
        self.use_item_button.grid(row=0, column=1, padx=5)
        self.shop_button.grid(row=0, column=2, padx=5)
        self.skip_button.grid(row=0, column=3, padx=5)
        self.enemy_data = [
            {"name": "Goblin", "art": " .--.  \n/    \\\n| () |\n \\__/ ", "health": 80, "attack_power": 15},
            {"name": "Orc", "art": " .--. \n/    \\\n| () |\n `--' ", "health": 100, "attack_power": 20},
            {"name": "Troll", "art": " .--. \n/    \\\n| uu |\n `--' ", "health": 120, "attack_power": 25},
            {"name": "Skeleton", "art": " .--. \n/    \\\n| xx |\n `--' ", "health": 90, "attack_power": 18},
            {"name": "Zombie", "art": " .--. \n/    \\\n| oo |\n `--' ", "health": 110, "attack_power": 22},
            {"name": "Dragon", "art": "  /^\\/^\\\n _|__|  O|\n\\/     /~ \\\n \\____|_____\n       \\_/\\_/", "health": 200, "attack_power": 40},
            {"name": "Demon", "art": "     ,--.\n  ,--'  '-.\n /     O   \\_\n \\         -,\n  '-._   _,'", "health": 180, "attack_power": 35},
        ]
        self.root.bind("<z>", self.check_timing)
        self.root.bind("<d>", lambda event: self.check_dodge(event))
        #self.root.bind("<x>", self.use_fireball)

    def start_game(self):
        name = self.name_entry.get()
        if not name:
            self.display_message("Please enter your name!")
            return
        self.player = Player(name)
        self.display_message(f"Welcome {self.player.name}! Your adventure begins...")

        self.name_label.pack_forget()
        self.name_entry.pack_forget()
        self.start_button.pack_forget()

        self.action_frame.pack()
        self.stats_frame.pack()
        self.trigger_event()

    def trigger_event(self):
        if self.player.health <= 0:
            if self.player.shield_active:
                self.player.shield_active = False
                self.display_message(
                    f"The Shield of Denial saved you from certain death!"
                )
                self.update_stats()
            else:
                self.display_message(
                    f"GAME OVER \n Score : {self.score}"
                )
                return
        if not self.encounter_ongoing:
            self.encounter_ongoing = True
            self.encounter_count += 1
            if self.encounter_count % 3 == 0:
                self.scale_enemies()
            encounter_type = random.choices(
                ["enemy", "treasure", "funny", "riddle"], weights=[8, 2, 1, 2]
            )[0]
            if encounter_type == "enemy":
                self.encounter_enemy()
            elif encounter_type == "treasure":
                self.find_treasure()
            elif encounter_type == "riddle":
                self.riddle_encounter()
            else:
                self.funny_encounter()
            self.encounter_ongoing = False

    def scale_enemies(self):
        for enemy in self.enemy_data:
            enemy["health"] = enemy["health"] * 1.2
            enemy["attack_power"] = enemy["attack_power"] * 1.4


    def encounter_enemy(self):
        enemy_choice = random.choices(self.enemy_data, weights = [5,5,5,5,5,1,1])[0]
        self.enemy = Enemy(
            enemy_choice["name"],
            enemy_choice["art"],
            enemy_choice["health"],
            enemy_choice["attack_power"],
        )
        self.display_message(
            f"A {self.enemy.name} has appeared!\n{self.enemy.art}\n"
        )
        self.update_stats()

    def find_treasure(self):
        found_coins = random.randint(10, 20)
        self.player.coins += found_coins
        winsound.PlaySound("pickupCoin.wav", winsound.SND_ASYNC)
        self.display_message(
            f"You found a treasure chest! You collected {found_coins} coins."
        )
        self.update_stats()

    def funny_encounter(self):
        funny_encounters = [
            "You trip over a rock and fall on your face. How embarrassing...",
            "A small dragon hiccups, accidentally setting your hair on fire. Luckily, it goes out quickly.",
            "You accidentally step in a puddle, splashing mud all over your clothes. Nice look!",
            "A curious squirrel steals your snack while you're not looking. Rude!",
        ]
        self.display_message(random.choice(funny_encounters))
        self.update_stats()

    def riddle_encounter(self):
        # Disable buttons during the encounter
        self.attack_button.config(state="disabled")
        self.use_item_button.config(state="disabled")
        self.shop_button.config(state="disabled")
        self.skip_button.config(state="disabled")

        # Show mysterious man dialogue in a popup window
        popup = tk.Toplevel(self.root)
        popup.title("Mysterious Encounter")
        popup.geometry("400x200")
        popup.resizable(False, False)

        tk.Label(
            popup,
            text="A mysterious man appears and challenges you with a riddle...\n"
            "Solve it correctly to earn a reward, or lose all your coins!",
            font=("Helvetica", 12),
            wraplength=350,
            justify="center",
        ).pack(pady=20)

        def on_continue():
            # Close the popup and immediately show the riddle
            popup.destroy()
            self.show_riddle()

        tk.Button(
            popup, text="Continue", font=("Helvetica", 12), command=on_continue
        ).pack(pady=10)

        popup.grab_set()
        popup.focus_set()

    def show_riddle(self):
        # Load riddles if not already loaded
        if not hasattr(self, "riddles"):
            self.riddles = []
            with open("riddles_new.txt", "r", encoding="utf-8", errors="replace") as file:
                current_riddle = {}
                for line in file:
                    line = line.strip()
                    if line.startswith("Question:"):
                        current_riddle["question"] = line[len("Question:"):].strip()
                    elif line.startswith("Answer:"):
                        current_riddle["answer"] = line[len("Answer:"):].strip()
                    elif line.startswith("Wrong options:"):
                        current_riddle["wrong"] = [opt.strip() for opt in line[len("Wrong options:"):].split(",")]
                        self.riddles.append(current_riddle)
                        current_riddle = {}  # Reset for the next riddle

        # Select a random riddle
        riddle = random.choice(self.riddles)
        question = riddle["question"]
        correct_answer = riddle["answer"]
        options = riddle["wrong"] + [correct_answer]
        random.shuffle(options)

        # Clear the canvas and set up the riddle display
        if not hasattr(self, "riddle_canvas"):
            self.riddle_canvas = tk.Canvas(self.root, width=600, height=400, bg="lightgray")
            self.riddle_canvas.pack(pady=10)
        self.riddle_canvas.delete("all")
        self.riddle_canvas.create_text(
            300,
            50,
            text=question,
            font=("Helvetica", 14),
            fill="black",
            width=580,
            anchor="center",
        )

        # Place answer buttons inside the canvas
        if hasattr(self, "answer_buttons"):
            for btn in self.answer_buttons:
                btn.destroy()
        self.answer_buttons = []

        for i, option in enumerate(options):
            btn = tk.Button(
                self.root,
                text=option,
                font=("Helvetica", 12),
                command=lambda opt=option: self.check_answer(opt, correct_answer),
            )
            self.answer_buttons.append(btn)
            self.riddle_canvas.create_window(
                300, 120 + i * 40, window=btn, anchor="center"
            )

        # Disable main game buttons during the riddle encounter
        self.attack_button.config(state="disabled")
        self.use_item_button.config(state="disabled")
        self.shop_button.config(state="disabled")
        self.skip_button.config(state="disabled")

    def check_answer(self, selected_option, correct_answer):
        # Check if the selected answer is correct
        if selected_option == correct_answer:
            winsound.PlaySound("riddle_answered correctly.wav", winsound.SND_ASYNC)
            self.player.healing_potions += 1
            self.show_result_popup("Correct!", "You earned a free healing potion.")
        else:
            winsound.PlaySound("riddle_answered incorrectly.wav", winsound.SND_ASYNC)
            self.player.coins = 0
            self.show_result_popup("Wrong!", "The mysterious man took all your coins.")
        # Clear the canvas and answer buttons
        if hasattr(self, "riddle_canvas"):
            self.riddle_canvas.delete("all")
        if hasattr(self, "answer_buttons"):
            for btn in self.answer_buttons:
                btn.destroy()

        # Re-enable main game buttons
        self.attack_button.config(state="normal")
        self.use_item_button.config(state="normal")
        self.shop_button.config(state="normal")
        self.skip_button.config(state="normal")

        self.trigger_event()

    def show_result_popup(self, title, message):
        # Create a popup window to show the result
        popup = tk.Toplevel(self.root)
        popup.title(title)
        popup.geometry("400x200")
        popup.resizable(False, False)

        tk.Label(
            popup,
            text=message,
            font=("Helvetica", 14),
            wraplength=350,
            justify="center",
        ).pack(pady=20)

        tk.Button(popup, text="OK", font=("Helvetica", 12), command=popup.destroy).pack(
            pady=10
        )

        popup.grab_set()
        popup.focus_set()

        popup.wait_window()

    def start_swing(self):
        if self.enemy:
            self.swinging = True
            self.swing_position = 10
            self.swing_direction = 1
            self.swing_canvas.itemconfig(self.target_zone, state="normal")
            self.swing_canvas.itemconfig(self.perfect_zone, state="normal")
            self.swing_canvas.itemconfig(self.swing_bar, state="normal")
            self.update_swing_bar()
            self.shop_button.config(state="disabled")
            self.skip_button.config(state="disabled")

    def update_swing_bar(self):
        if self.swinging:
            if self.swing_position <= 10:
                self.swing_direction = 1
            elif self.swing_position >= 390:
                self.swing_direction = -1

            self.swing_position += self.swing_direction * 5
            bar_width = 4
            bar_top = 30
            bar_bottom = 70
            self.swing_canvas.coords(
                self.swing_bar,
                self.swing_position,
                bar_top,
                self.swing_position + bar_width,
                bar_bottom,
            )

            self.root.after(16, self.update_swing_bar)

    def check_timing(self, event):
        if self.swinging:
            self.swinging = False
            swing_x1, _, swing_x2, _ = self.swing_canvas.coords(self.swing_bar)
            target_x1, _, target_x2, _ = self.swing_canvas.coords(self.target_zone)
            perfect_x1, _, perfect_x2, _ = self.swing_canvas.coords(self.perfect_zone)
            winsound.PlaySound("attack.wav", winsound.SND_ASYNC)
            swing_center = (swing_x1 + swing_x2) / 2
            self.swing_canvas.itemconfig(self.target_zone, state="hidden")
            self.swing_canvas.itemconfig(self.perfect_zone, state="hidden")
            self.swing_canvas.itemconfig(self.swing_bar, state="hidden")
            if perfect_x1 <= swing_center <= perfect_x2:
                damage = int(self.player.attack_power * 1.5)
                self.display_message(f"Perfect hit! You dealt {damage} damage!")
            elif (
                target_x1 <= swing_x1 <= target_x2 or target_x1 <= swing_x2 <= target_x2
            ):
                damage = self.player.attack_power
                self.display_message(f"Good hit! You dealt {damage} damage!")
            else:
                damage = int(self.player.attack_power * 0)
                self.display_message(f"Missed timing! You dealt only no damage!")
            self.enemy.health -= damage
            self.update_stats()

            if self.enemy.health <= 0:
                # Only reward the player after defeating the enemy
                winsound.PlaySound("enemy_defeated.wav", winsound.SND_ASYNC)
                coins_dropped = self.enemy.drop_coins()
                self.player.coins += coins_dropped
                xp_gained = random.randint(15, 25)
                if self.enemy.name in ["Dragon", "Demon"]:
                    xp_gained = self.player.level * 100  # Full level-up for Dragon and Demon
                level_up_message = "You leveled up!" if self.player.gain_xp(xp_gained) else ""
                self.display_message(
                    f"{self.enemy.name} has been defeated! You collected {coins_dropped} coins and {xp_gained} XP! {level_up_message}"
                )
                self.score += 10
                self.score_label.config(text=f"Score: {self.score}")
                self.enemy = None
                self.update_stats()
                self.shop_button.config(state="normal")
                self.skip_button.config(state="normal")
            else:
                self.start_dodge()

    #def use_fireball(self, event):
     #   if self.player.fireball_charges > 0 and self.enemy:
      #      winsound.PlaySound("fireball.wav", winsound.SND_ASYNC)
       #     self.enemy.health = 0
        #    coins_dropped = self.enemy.drop_coins() * 2
         #   self.player.coins += coins_dropped
          #  self.display_message(
           #     f"You incinerated the {self.enemy.name} with a fireball! You collected {coins_dropped} coins."
            #)
            #self.player.fireball_charges -= 1
            #self.score += 20
            #self.score_label.config(text=f"Score: {self.score}")
            #winsound.PlaySound("enemy_defeated.wav", winsound.SND_ASYNC)
            #self.enemy = None
            #self.update_stats()
        #else:
         #   self.display_message("You don't have any fireball charges left!")

    def heal(self):
        heal_amount = self.player.heal()
        if heal_amount == "No Potions":
            self.display_message("You're out of healing potions!")
        else:
            winsound.PlaySound("heal.wav", winsound.SND_ASYNC)
            self.display_message(f"You healed {heal_amount} health!")
        self.update_stats()

    def start_dodge(self):
        """Starts the dodge timer before the dodge sequence."""
        self.dodge_success = False  # Reset dodge success
        self.start_dodge_timer()

    def start_dodge_timer(self):
        """Displays a countdown timer before starting the dodge sequence."""
        self.dodge_timer_label = tk.Label(
            self.root, text="3", font=("Helvetica", 18), bg="white"
        )
        self.dodge_timer_label.place(x=200, y=50)  # Position above the swing canvas
        self.countdown_value = 3
        self.update_dodge_timer()

    def update_dodge_timer(self):
        if self.countdown_value > 0:
            self.dodge_timer_label.config(text=str(self.countdown_value))
            self.countdown_value -= 1
            self.root.after(1000, self.update_dodge_timer)
        else:
            self.dodge_timer_label.destroy()  # Remove the timer label
            self.start_dodge_bar()  # Start the dodge sequence

    def start_dodge_bar(self):
        """Initializes the dodge bar and randomizes the dodge zone position."""
        random_x = random.randint(50, 300)  # Avoid extreme edges
        self.swing_canvas.coords(
            self.dodge_zone, random_x, 15, random_x + 50, 85  # Randomize position
        )
        self.swing_canvas.itemconfig(self.dodge_zone, state="normal")  # Show dodge zone
        self.swinging = True
        self.swing_canvas.itemconfig(self.swing_bar, state="normal") # Show timing bar
        self.swing_direction = 1  # Start moving right
        self.swing_position = 10
        self.dodge_success = False
        self.update_dodge_bar()

    def update_dodge_bar(self):
        """Moves the dodge bar to create a timing challenge."""
        if self.swinging:
            if self.swing_position >= 390:  # Stop at the right edge
                self.swinging = False
                self.check_dodge(None)  # Automatically evaluate timing
                return

            self.swing_position += 5
            self.swing_canvas.coords(
                self.swing_bar,
                self.swing_position,
                30,
                self.swing_position + 4,
                70,
            )
            self.root.after(16, self.update_dodge_bar)

    def check_dodge(self, event=None):
        """Checks if the player's timing for dodge was successful."""
        if self.swinging:
            self.swinging = False
            self.swing_canvas.itemconfig(self.dodge_zone, state="hidden")  # Hide dodge zone
            self.swing_canvas.itemconfig(self.swing_bar, state="hidden")  # Hide the timing bar

            swing_x1, _, swing_x2, _ = self.swing_canvas.coords(self.swing_bar)
            dodge_x1, _, dodge_x2, _ = self.swing_canvas.coords(self.dodge_zone)

            if dodge_x1 <= (swing_x1 + swing_x2) / 2 <= dodge_x2:
                self.dodge_success = True
            else:
                self.dodge_success = False

            self.resolve_enemy_turn()

    #def enemy_turn(self):
    #    """Handles enemy attacks."""
    #    self.start_dodge()  # Initiates the dodge functionality during the enemy turn
    #    self.root.after(4000, self.resolve_enemy_turn)

    def resolve_enemy_turn(self):
        """Resolves the enemy's attack after the dodge attempt."""
        if self.dodge_success:
            self.display_message(f"You dodged the {self.enemy.name}'s attack!")
        else:
            damage = self.enemy.attack(self.player)
            self.display_message(f"The {self.enemy.name} attacks and deals {damage} damage!")
        self.dodge_success = False  # Reset dodge success for the next turn
        self.update_stats()

    def update_stats(self):
        self.player_stats_label.config(
            text=f"{self.player.name} - Health: {self.player.health} | Potions: {self.player.healing_potions} | Coins: {self.player.coins} | Fireballs: {self.player.fireball_charges} | Level: {self.player.level} | XP: {self.player.xp}"
        )
        if self.enemy:
            self.enemy_stats_label.config(
                text=f"{self.enemy.name} - Health: {self.enemy.health}\n{self.enemy.art}"
            )
            self.shop_button.config(state="disabled")
            self.skip_button.config(state="disabled")
        else:
            self.enemy_stats_label.config(text="")
            self.shop_button.config(state="normal")
            self.skip_button.config(state="normal")

    def show_shop(self):
        if self.enemy is None:
            shop_window = tk.Toplevel(self.root)
            shop_window.title("Dungeon Shop")
            shop_window.geometry("400x200")

            shop_label = tk.Label(shop_window, text="Welcome to the Dungeon Shop!")
            shop_label.pack(pady=10)

            tk.Button(
                shop_window, text="Buy Healing Potion (10 Coins)",
                command=lambda: self.buy_item("Healing Potion", 10, shop_window)
            ).pack(pady=5)

            tk.Button(
                shop_window, text="Buy Fireball (30 Coins)",
                command=lambda: self.buy_item("Fireball", 30, shop_window)
            ).pack(pady=5)

            tk.Button(
                shop_window, text="Buy Strength Potion (15 Coins)",
                command=lambda: self.buy_item("Strength Potion", 15, shop_window)
            ).pack(pady=5)

            tk.Button(
                shop_window, text="Buy Shield of Denial (50 Coins)",
                command=lambda: self.buy_item("Shield of Denial", 50, shop_window)
            ).pack(pady=5)

            tk.Button(
                shop_window, text="Leave Shop", command=shop_window.destroy
            ).pack(pady=5)

    def buy_item(self, item, cost, window):
        if self.player.coins >= cost:
            self.player.coins -= cost
            if item == "Healing Potion":
                self.player.healing_potions += 1
            elif item == "Fireball":
                self.player.fireball_charges += 1
            elif item == "Strength Potion":
                self.player.strength_potions += 1
            elif item == "Shield of Denial":
                self.player.shield_active = True
            self.display_message(f"You bought a {item}!")
            self.update_stats()
            window.destroy()
        else:
            self.display_message("Not enough coins!")
            window.destroy()

    def use_item(self):
        item_window = tk.Toplevel(self.root)
        item_window.title("Use Item")
        item_window.geometry("200x200")

        def apply_item(item):
            if item == "Healing Potion" and self.player.healing_potions > 0:
                self.player.healing_potions -= 1
                self.player.health += random.randint(25, 40)
                winsound.PlaySound("heal.wav", winsound.SND_ASYNC)
                self.display_message("You used a Healing Potion!")
            elif item == "Fireball" and self.player.fireball_charges > 0:
                coins_dropped = self.enemy.drop_coins() * 2
                self.player.coins += coins_dropped
                winsound.PlaySound("fireball.wav", winsound.SND_ASYNC)
                self.display_message(f"You incinerated the {self.enemy.name} with a fireball! You collected {coins_dropped} coins.")
                self.player.fireball_charges -= 1
                self.score += 20
                self.score_label.config(text=f"Score: {self.score}")
                winsound.PlaySound("enemy_defeated.wav", winsound.SND_ASYNC)
            elif item == "Strength Potion" and self.player.strength_potions > 0:
                self.player.strength_potion_effect += 3
                self.display_message("You used a Strength Potion!")
            else:
                self.display_message("You can't use that item right now!")
            self.update_stats()
            item_window.destroy()

        for item in ["Healing Potion", "Fireball", "Strength Potion"]:
            tk.Button(
                item_window, text=f"Use {item}",
                command=lambda i=item: apply_item(i)
            ).pack(pady=5)

    def display_message(self, message):
        message_window = tk.Toplevel(self.root)
        message_window.title("Message")
        message_window.geometry(
            "400x250+{}+{}".format(
                int(self.root.winfo_width() / 2 - 200),
                int(self.root.winfo_height() / 2 - 75),
            )
        )

        message_label = tk.Label(
            message_window, text=message, font=("Helvetica", 14), wraplength=350
        )
        message_label.pack(pady=20)

        ok_button = tk.Button(
            message_window, text="OK", command=lambda: message_window.destroy()
        )
        ok_button.pack(pady=10)

        message_window.protocol("WM_DELETE_WINDOW", lambda: message_window.destroy())
        message_window.wait_window()

    def continue_encounter(self):
        if not self.enemy:
            self.trigger_event()
        else:
            self.display_message("You can't continue while fighting an enemy!")

if __name__ == "__main__":
    root = tk.Tk()
    game_gui = DungeonGameGUI(root)
    root.mainloop()
