# Puncture Braille Bot

Experimental Telegram bot that converts Russian text into a mirrored Braille template for manual punching.

The idea is simple: send text to the bot, receive a printable DOCX document, print it, and use the mirrored dots as a guide when punching from the back side of the sheet. After the sheet is turned over, the raised dots are oriented for reading.

> Work in progress. This is a hobby project and has not been validated as assistive technology. For real-world use, verify the resulting Braille with an experienced reader.

## How it works

1. The bot accepts Russian text.
2. Characters are converted to six-dot Russian Braille.
3. Each Braille cell is mirrored horizontally and the text is reversed for punching from the back side.
4. The result is wrapped into printable lines.
5. The bot generates a DOCX file and sends it back to the user.

Unsupported characters currently remain as `?`.

## Stack

- Python
- pyTelegramBotAPI
- python-docx

## Run locally

```bash
git clone https://github.com/TerentievKirill/Puncture_Braile_bot.git
cd Puncture_Braile_bot
python -m venv .venv
```

Activate the virtual environment and install dependencies:

```bash
pip install -r requirements.txt
```

Set the Telegram bot token:

Linux / macOS:

```bash
export TELEGRAM_BOT_TOKEN="your-token"
python bot.py
```

PowerShell:

```powershell
$env:TELEGRAM_BOT_TOKEN="your-token"
python bot.py
```

---

## Русский

Небольшой экспериментальный Telegram-бот для подготовки текста к ручному созданию письма по системе Брайля.

Пользователь отправляет боту текст на русском языке. Бот переводит его в шеститочечный Брайль, зеркально отражает ячейки и разворачивает текст так, чтобы получился шаблон для прокалывания бумаги с обратной стороны. После переворота листа рельефные точки оказываются ориентированы для чтения.

Бот формирует DOCX, который можно распечатать и использовать как шаблон.

### Запуск

Установить зависимости:

```bash
pip install -r requirements.txt
```

Перед запуском задать токен бота в переменной окружения `TELEGRAM_BOT_TOKEN`, затем выполнить:

```bash
python bot.py
```

### Статус

Проект находится в состоянии work in progress. Это экспериментальный инструмент, а не сертифицированное средство доступности; для реального использования результат стоит проверять с человеком, который уверенно читает Брайль.
