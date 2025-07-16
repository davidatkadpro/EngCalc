# config.py
# Hardware pin mappings and display configuration

# Example pin mappings (to be customized)
PINS = {
    'KEYPAD_ROWS': [0, 1, 2, 3, 4, 5],
    'KEYPAD_COLS': [6, 7, 8, 9, 10, 11],
    'ENCODER_A': 12,
    'ENCODER_B': 13,
    'ENCODER_SW': 14,
    'OLED_DC': 15,
    'OLED_CS': 16,
    'OLED_RST': 17,
    'OLED_SCK': 18,
    'OLED_MOSI': 19,
}

DISPLAY = {
    'WIDTH': 128,
    'HEIGHT': 64,
    'DRIVER': 'SSD1309',
    'SPI': True,
} 