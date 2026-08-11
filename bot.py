import os
from io import BytesIO

import telebot
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN environment variable is not set")

bot = telebot.TeleBot(TOKEN)


BRAILLE_MAP = {
    "а": "⠁", "б": "⠃", "в": "⠺", "г": "⠛", "д": "⠙",
    "е": "⠑", "ё": "⠡", "ж": "⠚", "з": "⠵", "и": "⠊",
    "й": "⠯", "к": "⠅", "л": "⠇", "м": "⠍", "н": "⠝",
    "о": "⠕", "п": "⠏", "р": "⠗", "с": "⠎", "т": "⠞",
    "у": "⠥", "ф": "⠋", "х": "⠓", "ц": "⠉", "ч": "⠟",
    "ш": "⠱", "щ": "⠭", "ъ": "⠷", "ы": "⠮", "ь": "⠾",
    "э": "⠪", "ю": "⠳", "я": "⠫", " ": " ",
    ",": "⠂", ".": "⠲", "!": "⠖", "?": "⠦", "-": "⠤",
    ":": "⠒", ";": "⠆", "(": "⠶", ")": "⠶",
}

MAX_LINE_LENGTH = 35


def char_to_braille(char: str) -> str:
    """Convert one Russian character to a six-dot Braille character."""
    return BRAILLE_MAP.get(char.lower(), "?")


def mirror_braille_horizontal(braille_char: str) -> str:
    """Mirror a six-dot Braille cell horizontally for punching from the back."""
    if braille_char == " ":
        return " "

    codepoint = ord(braille_char)
    if not 0x2800 <= codepoint <= 0x28FF:
        return braille_char

    binary = codepoint - 0x2800
    mirrored_binary = (
        ((binary & 0b000001) << 3)
        | ((binary & 0b000010) << 3)
        | ((binary & 0b000100) << 3)
        | ((binary & 0b001000) >> 3)
        | ((binary & 0b010000) >> 3)
        | ((binary & 0b100000) >> 3)
    )
    return chr(0x2800 + mirrored_binary)


def text_to_braille_right_to_left(text: str) -> str:
    """Build the mirrored right-to-left template used for manual punching."""
    braille_text = "".join(char_to_braille(char) for char in text)
    mirrored_text = "".join(
        mirror_braille_horizontal(char) for char in braille_text
    )
    return mirrored_text[::-1]


def split_into_lines(text: str, max_length: int = MAX_LINE_LENGTH) -> list[str]:
    """Wrap text by words without exceeding the target line length when possible."""
    words = text.split()
    lines = []
    current_line = []
    current_length = 0

    for word in words:
        separator = 1 if current_line else 0
        if current_line and current_length + separator + len(word) > max_length:
            lines.append(" ".join(current_line))
            current_line = []
            current_length = 0
            separator = 0

        current_line.append(word)
        current_length += separator + len(word)

    if current_line:
        lines.append(" ".join(current_line))

    return lines


def build_docx(lines: list[str]) -> BytesIO:
    """Create a printable DOCX in memory."""
    document = Document()

    for line in lines:
        paragraph = document.add_paragraph(line)
        paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        paragraph.runs[0].font.size = Pt(22)

    buffer = BytesIO()
    document.save(buffer)
    buffer.seek(0)
    buffer.name = "braille_for_poking.docx"
    return buffer


@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.reply_to(
        message,
        "Привет! Отправь мне текст на русском языке, и я верну DOCX-шаблон "
        "в Брайле для прокалывания. Текст разобьётся по словам.",
    )


@bot.message_handler(content_types=["text"])
def handle_text(message):
    braille_for_poking = text_to_braille_right_to_left(message.text)
    reversed_lines = split_into_lines(braille_for_poking)[::-1]

    document = build_docx(reversed_lines)
    bot.send_document(message.chat.id, document)


if __name__ == "__main__":
    bot.infinity_polling()
