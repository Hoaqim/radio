import sqlite3
import RPi.GPIO as GPIO
import time

class FMRadioFavorites:
    def __init__(self, button_add_pin=4, button_delete_pin=17, database_file="radio_frequencies.db"):
        self.BUTTON_ADD = button_add_pin
        self.BUTTON_DELETE = button_delete_pin
        self.DATABASE_FILE = database_file

        self.setup_gpio()
        self.create_database()

    def setup_gpio(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.BUTTON_ADD, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.BUTTON_DELETE, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def create_database(self):
        conn = sqlite3.connect(self.DATABASE_FILE)
        cursor = conn.cursor()

        cursor.execute('''CREATE TABLE IF NOT EXISTS favorites
                          (id INTEGER PRIMARY KEY AUTOINCREMENT, frequency REAL)''')

        conn.commit()
        conn.close()

    def add_frequency_to_database(self, frequency):
        conn = sqlite3.connect(self.DATABASE_FILE)
        cursor = conn.cursor()

        # Insert the frequency into the favorites table
        cursor.execute("INSERT INTO favorites (frequency) VALUES (?)", (frequency,))

        conn.commit()
        conn.close()

    def delete_frequency_from_database(self, frequency):
        conn = sqlite3.connect(self.DATABASE_FILE)
        cursor = conn.cursor()
        print("Deleted"+str(frequency))

        cursor.execute("DELETE FROM favorites WHERE frequency LIKE ?", (frequency,))
        conn.commit()
        conn.close()

    def get_favorite_frequencies(self):
        conn = sqlite3.connect(self.DATABASE_FILE)
        cursor = conn.cursor()

        cursor.execute("SELECT frequency FROM favorites")
        frequencies = cursor.fetchall()

        conn.close()
        print(type(frequencies))
        return frequencies
