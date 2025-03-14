"""
Custom font definitions for MAX7219 LED matrix display.
Each character is defined as an 8x8 bitmap where 1 represents an ON pixel and 0 represents an OFF pixel.
"""

# Custom large number font (8x8 pixels per digit)
LARGE_NUMBERS = {
    '0': [
        0b00111100,
        0b01100110,
        0b01100110,
        0b01100110,
        0b01100110,
        0b01100110,
        0b01100110,
        0b00111100
    ],
    '1': [
        0b00011000,
        0b00111000,
        0b00011000,
        0b00011000,
        0b00011000,
        0b00011000,
        0b00011000,
        0b01111110
    ],
    '2': [
        0b00111100,
        0b01100110,
        0b00000110,
        0b00001100,
        0b00011000,
        0b00110000,
        0b01100000,
        0b01111110
    ],
    '3': [
        0b00111100,
        0b01100110,
        0b00000110,
        0b00011100,
        0b00000110,
        0b00000110,
        0b01100110,
        0b00111100
    ],
    '4': [
        0b00001100,
        0b00011100,
        0b00111100,
        0b01101100,
        0b01111110,
        0b00001100,
        0b00001100,
        0b00001100
    ],
    '5': [
        0b01111110,
        0b01100000,
        0b01100000,
        0b01111100,
        0b00000110,
        0b00000110,
        0b01100110,
        0b00111100
    ],
    '6': [
        0b00111100,
        0b01100110,
        0b01100000,
        0b01111100,
        0b01100110,
        0b01100110,
        0b01100110,
        0b00111100
    ],
    '7': [
        0b01111110,
        0b00000110,
        0b00001100,
        0b00011000,
        0b00110000,
        0b00110000,
        0b00110000,
        0b00110000
    ],
    '8': [
        0b00111100,
        0b01100110,
        0b01100110,
        0b00111100,
        0b01100110,
        0b01100110,
        0b01100110,
        0b00111100
    ],
    '9': [
        0b00111100,
        0b01100110,
        0b01100110,
        0b01100110,
        0b00111110,
        0b00000110,
        0b01100110,
        0b00111100
    ]
}

# Custom small font (5x8 pixels per character)
SMALL_FONT = {
    'A': [
        0b00100000,
        0b01010000,
        0b10001000,
        0b11111000,
        0b10001000,
        0b10001000,
        0b10001000,
        0b00000000
    ],
    'B': [
        0b11110000,
        0b10001000,
        0b10001000,
        0b11110000,
        0b10001000,
        0b10001000,
        0b11110000,
        0b00000000
    ],
    # Add more characters as needed
}

def get_char(char, font_type='large'):
    """Get the bitmap for a specific character.
    
    Args:
        char (str): The character to get the bitmap for
        font_type (str): 'large' for numbers, 'small' for text
        
    Returns:
        list: List of bytes representing the character bitmap
    """
    if font_type == 'large':
        return LARGE_NUMBERS.get(char, [0] * 8)
    else:
        return SMALL_FONT.get(char, [0] * 8)

def draw_char(display, char, x, y, font_type='large'):
    """Draw a character at the specified position.
    
    Args:
        display: MAX7219 display instance
        char (str): Character to draw
        x (int): X position
        y (int): Y position
        font_type (str): 'large' for numbers, 'small' for text
    """
    bitmap = get_char(char, font_type)
    for row, data in enumerate(bitmap):
        for col in range(8):
            if data & (1 << (7 - col)):
                display.pixel(x + col, y + row, 1)

def draw_text(display, text, x, y, font_type='large'):
    """Draw text string at the specified position.
    
    Args:
        display: MAX7219 display instance
        text (str): Text to draw
        x (int): Starting X position
        y (int): Y position
        font_type (str): 'large' for numbers, 'small' for text
    """
    current_x = x
    for char in text:
        draw_char(display, char, current_x, y, font_type)
        current_x += 8  # Move to next character position 