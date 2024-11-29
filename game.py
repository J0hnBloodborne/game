import tkinter as tk
import random
import winsound
import string

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

    def gain_xp(self, amount):
        self.xp += amount
        if self.xp >= self.level * 100:  # Level-up threshold
            self.xp -= self.level * 100
            self.level += 1
            self.health += 20  # Increase health on level-up
            self.attack_power += 5  # Increase attack power on level-up
            return True
        return False

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
        if self.coins >= 30:
            self.coins -= 30
            self.fireball_charges += 1
            return True
        return False


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
            return random.randint(20,30)
        elif self.name == "Demon":
            return random.randint(20,30)
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
        self.swing_canvas.pack(pady=10)

        self.controls_label = tk.Label(
            root,
            text="Controls:\nAttack: Z\nHeal: H\nFireball: X",
            font=("Helvetica", 12),
        )
        self.controls_label.pack(side=tk.RIGHT, padx=20)

        self.action_frame = tk.Frame(root)
        self.attack_button = tk.Button(
            self.action_frame, text="Attack", command=self.start_swing, bg="lightblue"
        )
        self.heal_button = tk.Button(
            self.action_frame, text="Heal", command=self.heal, bg="lightgoldenrodyellow"
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
        self.heal_button.grid(row=0, column=1, padx=5)
        self.shop_button.grid(row=0, column=2, padx=5)
        self.skip_button.grid(row=0, column=3, padx=5)
        self.enemy_data = [
            {
                "name": "Goblin",
                "art": " .--.  \n/    \\\n| () |\n \\__/ ",
                "health": 80,
                "attack_power": 15,
            },
            {
                "name": "Orc",
                "art": " .--. \n/    \\\n| () |\n `--' ",
                "health": 100,
                "attack_power": 20,
            },
            {
                "name": "Troll",
                "art": " .--. \n/    \\\n| uu |\n `--' ",
                "health": 120,
                "attack_power": 25,
            },
            {
                "name": "Skeleton",
                "art": " .--. \n/    \\\n| xx |\n `--' ",
                "health": 90,
                "attack_power": 18,
            },
            {
                "name": "Zombie",
                "art": " .--. \n/    \\\n| oo |\n `--' ",
                "health": 110,
                "attack_power": 22,
            },
            {
                "name": "Dragon",
                "art": "  /^\\/^\\\n _|__|  O|\n\\/     /~ \\\n \\____|_____\n       \\_/\\_/",
                "health": 200,
                "attack_power": 40
            },
            {
                "name": "Demon",
                "art": "     ,--.\n  ,--'  '-.\n /     O   \\_\n \\         -,\n  '-._   _,'",
                "health": 180,
                "attack_power": 35
            },
        ]
        self.root.bind("<z>", self.check_timing)
        self.root.bind("<x>", self.use_fireball)

    def scale_enemies(self):
        for enemy_data in self.enemy_data:
            enemy_data["health"] = int(enemy_data["health"]*1.2)
            enemy_data["attack_power"] = int(enemy_data["attack_power"]*1.5)

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

    def encounter_enemy(self):
        enemy_choice = random.choice(self.enemy_data)
        self.enemy = Enemy(
            enemy_choice["name"],
            enemy_choice["art"],
            enemy_choice["health"],
            enemy_choice["attack_power"],
        )
        xp_gained = random.randint(15, 25)
        if self.enemy.name in ["Dragon", "Demon"]:
            xp_gained = self.player.level * 100  # Full level-up for Dragon and Demon
        self.player.gain_xp(xp_gained)
        coins_gained = self.enemy.drop_coins()
        self.player.coins += coins_gained
        level_up_message = "You leveled up!" if self.player.gain_xp(xp_gained) else ""
        self.display_message(
            f"A {self.enemy.name} has appeared!\n{self.enemy.art}\n"
            f"You gained {coins_gained} coins and {xp_gained} XP! {level_up_message}"
        )
        self.update_stats()
        self.display_message(f"A {self.enemy.name} has appeared!\n{self.enemy.art}")
        self.shop_button.config(state="disabled")
        self.skip_button.config(state="disabled")`

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
        self.heal_button.config(state="disabled")
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
        self.heal_button.config(state="disabled")
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
        self.heal_button.config(state="normal")
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
                damage = int(self.player.attack_power * 0.5)
                self.display_message(f"Missed timing! You dealt only {damage} damage!")
            self.enemy.health -= damage
            self.update_stats()
            if self.enemy.health <= 0:
                winsound.PlaySound("enemy_defeated.wav", winsound.SND_ASYNC)
                coins_dropped = self.enemy.drop_coins()
                self.player.coins += coins_dropped
                self.display_message(
                    f"{self.enemy.name} has been defeated! You collected {coins_dropped} coins."
                )
                self.score += 10
                self.score_label.config(text=f"Score: {self.score}")
                self.enemy = None
                self.update_stats()
                self.shop_button.config(state="normal")
                self.skip_button.config(state="normal")
            else:
                self.enemy_turn()

    def use_fireball(self, event):
        if self.player.fireball_charges > 0 and self.enemy:
            winsound.PlaySound("fireball.wav", winsound.SND_ASYNC)
            self.enemy.health = 0
            coins_dropped = self.enemy.drop_coins() * 2
            self.player.coins += coins_dropped
            self.display_message(
                f"You incinerated the {self.enemy.name} with a fireball! You collected {coins_dropped} coins."
            )
            self.player.fireball_charges -= 1
            self.score += 20
            self.score_label.config(text=f"Score: {self.score}")
            winsound.PlaySound("enemy_defeated.wav", winsound.SND_ASYNC)
            self.enemy = None
            self.update_stats()
        else:
            self.display_message("You don't have any fireball charges left!")

    def heal(self):
        heal_amount = self.player.heal()
        if heal_amount == "No Potions":
            self.display_message("You're out of healing potions!")
        else:
            winsound.PlaySound("heal.wav", winsound.SND_ASYNC)
            self.display_message(f"You healed {heal_amount} health!")
        self.update_stats()

    def enemy_turn(self):
        damage = self.enemy.attack(self.player)
        self.display_message(
            f"The {self.enemy.name} attacks and deals {damage} damage!"
        )
        self.update_stats()
        self.shop_button.config(state="disabled")
        self.skip_button.config(state="disabled")

    def update_stats(self):
        self.player_stats_label.config(
            text=f"{self.player.name} - Health: {self.player.health} | Potions: {self.player.healing_potions} | Coins: {self.player.coins} | Fireballs: {self.player.fireball_charges}"
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
            shop_window.geometry(
                "400x150+{}+{}".format(
                    int(self.root.winfo_width() / 2 - 200),
                    int(self.root.winfo_height() / 2 - 75),
                )
            )

            shop_label = tk.Label(shop_window, text="Welcome to the Dungeon Shop!")
            shop_label.pack(pady=10)

            buy_potion_button = tk.Button(
                shop_window,
                text="Buy Healing Potion (10 Coins)",
                command=self.buy_healing_potion,
            )
            buy_fireball_button = tk.Button(
                shop_window, text="Buy Fireball (30 Coins)", command=self.buy_fireball
            )
            buy_nothing_button = tk.Button(
                shop_window,
                text="Buy Nothing",
                command=lambda: self.on_shop_close(shop_window),
            )
            buy_potion_button.pack(pady=5)
            buy_fireball_button.pack(pady=5)
            buy_nothing_button.pack(pady=5)

            shop_window.protocol(
                "WM_DELETE_WINDOW", lambda: self.on_shop_close(shop_window)
            )
        else:
            self.display_message("You can't shop while fighting an enemy!")

    def buy_healing_potion(self):
        if self.player.buy_healing_potion():
            self.display_message("You bought a healing potion!")
        else:
            self.display_message("Not enough coins!")
        self.update_stats()

    def buy_fireball(self):
        if self.player.buy_fireball():
            self.display_message("You bought a fireball!")
        else:
            self.display_message("Not enough coins!")
        self.update_stats()

    def on_shop_close(self, shop_window):
        shop_window.destroy()

    def display_message(self, message):
        message_window = tk.Toplevel(self.root)
        message_window.title("Message")
        message_window.geometry(
            "400x150+{}+{}".format(
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
