import telebot
import setting

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

    # Получаем бинарное представление точек символа Брайля
    binary = ord(braille_char) - 0x2800  # Убираем базовый код для Брайля

    # Зеркальное отображение точек по горизонтали
    mirrored_binary = (
            ((binary & 0b000001) << 3) |  # Перемещаем точку 1 на место 4
            ((binary & 0b000010) << 3) |  # Перемещаем точку 2 на место 5
            ((binary & 0b000100) << 3) |  # Перемещаем точку 3 на место 6
            ((binary & 0b001000) >> 3) |  # Перемещаем точку 4 на место 1
            ((binary & 0b010000) >> 3) |  # Перемещаем точку 5 на место 2
            ((binary & 0b100000) >> 3)  # Перемещаем точку 6 на место 3
    )
    return chr(0x2800 + mirrored_binary)  # Преобразуем обратно в символ Брайля


# Преобразование текста в Брайль с зеркалированием и записью справа налево
def text_to_braille_right_to_left(text):
    braille_text = ''.join(char_to_braille(char) for char in text)  # Преобразуем текст в Брайль
    mirrored_text = ''.join(mirror_braille_horizontal(char) for char in braille_text)  # Зеркалим каждый символ
    #return mirrored_text
    return mirrored_text[::-1]  # Записываем результат справа налево


# Обработка сообщений
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message,
                 "Привет! Отправь мне текст на русском языке, и я верну его в Брайле для прокалывания. Тест разобьетя по словам. Если в строке больше 30 симболов - происходит перенос на следующию строчку. Выравнивание пока в процессе. Рекомендую печатать из Блокнота, 24 шрифтом. Просто прокалываем черные точки и с другой стороны - текст по Брайлю")

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    original_text = message.text
    braille_for_poking = text_to_braille_right_to_left(original_text)

    # Разбиваем текст на слова
    words = braille_for_poking.split()
    lines = []  # Список строк
    current_line = []  # Текущая строка
    current_length = 0  # Текущая длина строки

    # Формируем строки, не превышающие 30 символов
    for word in words:
        if current_length + len(word) + 1 > 35:  # Если длина строки превышает 30
            lines.append(' '.join(current_line))  # Добавляем текущую строку в список строк
            current_line = []  # Очищаем текущую строку
            current_length = 0  # Сбрасываем длину строки

        current_line.append(word)  # Добавляем слово в текущую строку
        current_length += len(word) + 1  # Учитываем длину слова и пробел

    if current_line:  # Добавляем последнюю строку, если она есть
        lines.append(' '.join(current_line))

    # Инвертируем порядок строк
    reversed_lines = lines[::-1]

    # Определяем максимальную длину строки
    max_length = max(len(line) for line in reversed_lines)

    # Добавляем пробелы в начало каждой строки
    formatted_lines = [line.rjust(max_length) for line in reversed_lines]

    # Объединяем строки с переходами на новую строку
    formatted_braille = '\n'.join(formatted_lines)

    # Сохраняем текст в файл
    filename = "braille_for_poking.txt"
    with open(filename, "w", encoding="utf-8") as file:
        file.write(formatted_braille)

    # Отправляем файл
    with open(filename, "rb") as file:
        bot.send_document(message.chat.id, file)
# Запуск бота
bot.polling()