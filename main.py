import nltk
import telebot
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from langdetect import detect

# Загрузка токена бота (замените на свой токен)
TOKEN = '7148535083:AAFWygiIjejg6n_iPfxjJFEZ6jt4ug-_svg'
bot = telebot.TeleBot(TOKEN)

# Загрузка ресурсов для токенизации (выполнять единожды)
nltk.download('punkt')

# Инициализация сглаживающей функции BLEU
smoothing_function = SmoothingFunction().method1

# Множество для хранения идентификаторов обработанных сообщений
processed_messages = set()

# Словарь с описанием поддерживаемых языков
language_descriptions = {
    "en": "английский",
    "ru": "русский",
    "es": "испанский",
    "fr": "французский",
    "de": "немецкий"
}

def tokenize_text(text):
    return nltk.word_tokenize(text.lower())

def calculate_bleu(candidate, references):
    # Токенизация текста
    candidate_tokens = tokenize_text(candidate)
    reference_tokens = [tokenize_text(ref) for ref in references]

    # Расчет BLEU с использованием сглаживания
    bleu_score = sentence_bleu(reference_tokens, candidate_tokens, smoothing_function=smoothing_function)

    return bleu_score

@bot.message_handler(commands=['start'])
def handle_start(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Привет! Я бот для вычисления BLEU-оценки.\nОтправьте мне сначала текст-эталон.")
    bot.register_next_step_handler(message, get_reference_text)

def get_reference_text(message):
    chat_id = message.chat.id
    reference_text = message.text
    bot.send_message(chat_id, "Теперь отправьте мне текст-перевод.")
    bot.register_next_step_handler(message, lambda msg: calculate_and_send_bleu(msg, reference_text))

def calculate_and_send_bleu(message, reference_text):
    chat_id = message.chat.id
    translated_text = message.text

    # Определение языка текста
    lang = detect(translated_text)
    if lang not in language_descriptions:
        bot.send_message(chat_id, f"Язык '{lang}' не поддерживается. Пожалуйста, отправьте текст на одном из поддерживаемых языков.")
        return

    # Расчет BLEU-оценки
    bleu_score = calculate_bleu(translated_text, [reference_text])

    # Объяснение расчета BLEU Score
    explanation = ("BLEU Score рассчитывается на основе статистики биграмм и их совпадений между "
                   "текстом-переводом и текстом-эталоном. Он оценивает сходство между двумя текстами "
                   "путем сравнения биграмм (пар соседних слов) в переводе с эталонным текстом.")

    # Формирование сообщения с результатом и объяснением
    language_description = language_descriptions[lang]
    result_message = f"BLEU Score для перевода на {language_description}: {bleu_score}\n\n"
    result_message += explanation

    # Отправляем результат пользователю
    bot.send_message(chat_id, result_message)

    # Предлагаем пользователю использовать бота снова
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    item = telebot.types.KeyboardButton("Вычислить BLEU снова")
    markup.add(item)

    bot.send_message(chat_id, "Хотите вычислить BLEU снова?", reply_markup=markup)

    # Добавляем идентификатор обработанного сообщения в множество
    processed_messages.add(message.message_id)

    bot.register_next_step_handler(message, restart_bot)

def restart_bot(message):
    chat_id = message.chat.id
    if message.text.lower() == "вычислить bleu снова":
        bot.send_message(chat_id, "Отлично! Тогда отправьте Ваш текст-эталон.")
        bot.register_next_step_handler(message, get_reference_text)
    else:
        bot.send_message(chat_id, "Спасибо за использование бота!")

if __name__ == "__main__":
    bot.infinity_polling()
