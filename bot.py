import telebot
import setting
from docx import Document
from docx.shared import Pt
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

bot = telebot.TeleBot(setting.bot)


# Словарь русского алфавита Брайля
def char_to_braille(char):
    braille_map = {
        'а': '⠁', 'б': '⠃', 'в': '⠺', 'г': '⠛', 'д': '⠙',
        'е': '⠑', 'ё': '⠡', 'ж': '⠚', 'з': '⠵', 'и': '⠊',
        'й': '⠯', 'к': '⠅', 'л': '⠇', 'м': '⠍', 'н': '⠝',
        'о': '⠕', 'п': '⠏', 'р': '⠗', 'с': '⠎', 'т': '⠞',
        'у': '⠥', 'ф': '⠋', 'х': '⠓', 'ц': '⠉', 'ч': '⠟',
        'ш': '⠱', 'щ': '⠭', 'ъ': '⠷', 'ы': '⠮', 'ь': '⠾',
        'э': '⠪', 'ю': '⠳', 'я': '⠫', ' ': ' ',  # Пробел
        ',': '⠂', '.': '⠲', '!': '⠖', '?': '⠦', '-': '⠤',
        ':': '⠒', ';': '⠆', '(': '⠶', ')': '⠶',
    }
    return braille_map.get(char.lower(), '?')


# Зеркальное отображение символа Брайля (горизонтально)
def mirror_braille_horizontal(braille_char):
    if braille_char == ' ':
        return ' '  # Пробел не изменяется

    binary = ord(braille_char) - 0x2800  # Убираем базовый код для Брайля

    mirrored_binary = (
            ((binary & 0b000001) << 3) |
            ((binary & 0b000010) << 3) |
            ((binary & 0b000100) << 3) |
            ((binary & 0b001000) >> 3) |
            ((binary & 0b010000) >> 3) |
            ((binary & 0b100000) >> 3)
    )
    return chr(0x2800 + mirrored_binary)  # Преобразуем обратно в символ Брайля


# Преобразование текста в Брайль с зеркалированием и записью справа налево
def text_to_braille_right_to_left(text):
    braille_text = ''.join(char_to_braille(char) for char in text)
    mirrored_text = ''.join(mirror_braille_horizontal(char) for char in braille_text)
    return mirrored_text[::-1]  # Записываем результат справа налево


# Обработка сообщений
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message,
                 "Привет! Отправь мне текст на русском языке, и я верну его в Брайле для прокалывания. Тест разобьется по словам.")


@bot.message_handler(func=lambda message: True)
def handle_text(message):
    original_text = message.text
    braille_for_poking = text_to_braille_right_to_left(original_text)

    # Разбиваем текст на слова
    words = braille_for_poking.split()
    lines = []  # Список строк
    current_line = []  # Текущая строка
    current_length = 0  # Текущая длина строки

    # Формируем строки, не превышающие 35 символов
    for word in words:
        if current_length + len(word) + 1 > 35:  # Если длина строки превышает 35
            lines.append(' '.join(current_line))  # Добавляем текущую строку в список строк
            current_line = []  # Очищаем текущую строку
            current_length = 0  # Сбрасываем длину строки

        current_line.append(word)  # Добавляем слово в текущую строку
        current_length += len(word) + 1  # Учитываем длину слова и пробел

    if current_line:  # Добавляем последнюю строку, если она есть
        lines.append(' '.join(current_line))

    # Инвертируем порядок строк
    reversed_lines = lines[::-1]

    # Создаем новый документ .docx
    doc = Document()

    # Настроим форматирование текста
    for line in reversed_lines:
        paragraph = doc.add_paragraph(line)
        run = paragraph.runs[0]
        run.font.size = Pt(22)  # Устанавливаем размер шрифта 22
        paragraph.alignment = 2  # Выравнивание по правому краю

    # Сохраняем документ
    doc_filename = "braille_for_poking.docx"
    doc.save(doc_filename)

    # Создаем PDF с шрифтом Times-Roman
    pdf_filename = "braille_for_poking.pdf"
    c = canvas.Canvas(pdf_filename, pagesize=letter)
    c.setFont("Times-Roman", 12)  # Используем Times-Roman для кириллицы

    # Устанавливаем размер шрифта 22 в PDF
    c.setFont("Times-Roman", 22)

    y_position = 750  # Начальная вертикальная позиция
    for line in reversed_lines:
        c.drawString(500, y_position, line)  # Отрисовываем текст с отступом от правого края
        y_position -= 30  # Смещаемся вниз для следующей строки
        if y_position < 50:
            c.showPage()  # Переходим на новую страницу, если текст не помещается
            c.setFont("Times-Roman", 22)  # Устанавливаем шрифт на новой странице

    c.save()

    # Отправляем оба файла
    with open(doc_filename, "rb") as doc_file, open(pdf_filename, "rb") as pdf_file:
        bot.send_document(message.chat.id, doc_file)
        bot.send_document(message.chat.id, pdf_file)


# Запуск бота
bot.polling()
