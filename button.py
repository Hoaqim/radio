import sqlite3
import RPi.GPIO as GPIO
import time

# GPIO pins for buttons
BUTTON_ADD = 4
BUTTON_DELETE = 17

# Database file
DATABASE_FILE = "radio_frequencies.db"

def setup_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON_ADD, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(BUTTON_DELETE, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def create_database():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    # Create a table to store favorite frequencies
    cursor.execute('''CREATE TABLE IF NOT EXISTS favorites
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, frequency REAL)''')

    conn.commit()
    conn.close()

def add_frequency_to_database(frequency):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    # Insert the frequency into the favorites table
    cursor.execute("INSERT INTO favorites (frequency) VALUES (?)", (frequency,))

    conn.commit()
    conn.close()

def delete_frequency_from_database(frequency):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    # Delete the frequency from the favorites table
    cursor.execute("DELETE FROM favorites WHERE frequency = ?", (frequency,))

    conn.commit()
    conn.close()

def get_favorite_frequencies():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    # Retrieve all frequencies from the favorites table
    cursor.execute("SELECT frequency FROM favorites")
    frequencies = cursor.fetchall()

    conn.close()

    return frequencies

def main():
    setup_gpio()
    create_database()

    try:
        while True:
            if not GPIO.input(BUTTON_ADD):
                # Button to add frequency pressed
                print("Adding current frequency to favorites")
                add_frequency_to_database(101.1)  # Replace with the actual current frequency
                time.sleep(0.2)  # Button debounce delay

            if not GPIO.input(BUTTON_DELETE):
                # Button to delete frequency pressed
                print("Deleting current frequency from favorites")
                delete_frequency_from_database(101.1)  # Replace with the actual current frequency
                time.sleep(0.2)  # Button debounce delay

            # Retrieve and print favorite frequencies
#            favorites = get_favorite_frequencies()
 #           print("Favorite Frequencies:", favorites)

            time.sleep(0.1)  # Main loop delay

    except KeyboardInterrupt:
        GPIO.cleanup()

if __name__ == "__main__":
    main()
