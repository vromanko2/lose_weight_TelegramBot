import logging
import json
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)
from hand_estimation import hand_estimation_function, calculate_wrist, calculate_best_weight, calculate_cal_man, calculate_cal_woman

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

GENDER, PHOTO_OF_ARM, AGE, HEIGHT, LOCATION, BIO, CALORIES = range(7)

current_user = {
    "username": "",
    "gender": "",
    "photo_of_arm": "",
    "age": "",
    "height": "",
    "bio": ""
}


def start(update, context):
    reply_keyboard = [['Хлопець', 'Дівчина', 'Щось інше']]

    update.message.reply_text(
        'Привіт! Я найкращий дівчачий бот! Чому? Тому, що я вмію вираховувати сантиметри, які тебе покинули.'
        'Надішли /cancel щоб зупинити наше спілкування.\n\n'
        'Ти дівчинка чи хлопчик:)?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return GENDER


def gender(update, context):
    user = update.message.from_user
    response = update.message.text
    logger.info("Стать %s: %s", user.first_name, response)
    current_user["username"] = user.first_name
    current_user["gender"] = response
    update.message.reply_text('Супер! Будь ласка, надішли мені фото своєї руки, так, щоб було видно кисть, '
                              'щоб я зміг визначити '
                              'твою "ідеальну вагу"',
                              reply_markup=ReplyKeyboardRemove())

    return PHOTO_OF_ARM


def photo_of_arm(update, context):
    user = update.message.from_user
    photo_file = update.message.photo[-1].get_file()
    photo_file.download('user_photo_of_arm.jpg')
    logger.info("Фото кисті руки %s: %s", user.first_name, 'user_photo_of_arm.jpg')
    update.message.reply_text('Дякую! Мені ще потрібно знати твій вік. Скільки тобі років? '
                              'Я нікому не скажу, обіцяю!:)')
    current_user["photo_of_arm"] = 'user_photo_of_arm.jpg'

    return AGE


def skip_photo_of_arm(update, context):
    user = update.message.from_user
    logger.info("Користувач %s не надіслав photo_of_arm.", user.first_name)
    update.message.reply_text('Сумно, бо тепер я не зможу порахувати твою оптимальну вагу:((')

    return AGE


def age(update, context):
    user = update.message.from_user
    response = update.message.text
    logger.info("Вік %s: %s", user.first_name, response)
    update.message.reply_text('В тебе ще все життя попереду! Мені також потрібен твій ріст (в сантиметрах)')
    current_user["age"] = response

    return HEIGHT


def skip_age(update, context):
    user = update.message.from_user
    logger.info("Користувач %s не надіслав вік.", user.first_name)
    update.message.reply_text('Сумно, бо тепер я не зможу побачити твої зміни:((')

    return HEIGHT


def height(update, context):
    user = update.message.from_user
    response = update.message.text
    logger.info("Ріст %s: %s", user.first_name, response)
    update.message.reply_text('Супер, дякую! Зараз я розрахую твою "ідеальну вагу", але, спершу, '
                              'надішли свою локацію, будь ласка, '
                              'або надішли /skip , якщо хочеш пропустити.')
    current_user["height"] = response

    return LOCATION


def skip_height(update, context):
    user = update.message.from_user
    logger.info("Користувач %s не надіслав висоту.", user.first_name)
    update.message.reply_text('Сумно, бо тепер я не зможу побачити твої зміни:(( Надішли тепер свою локацію, будь'
                              ' ласка, або надішли /skip , якщо хочеш пропустити.')

    return LOCATION


def location(update, context):
    user = update.message.from_user
    user_location = update.message.location
    logger.info("Локація %s: %f / %f", user.first_name, user_location.latitude,
                user_location.longitude)
    update.message.reply_text('Може якось разом сходимо на пробіжку:)! '
                              'Розкажи мені ще щось про себе:)')
    current_user["location"] = user_location.latitude

    return BIO


def skip_location(update, context):
    user = update.message.from_user
    logger.info("Користувач %s не надіслав локацію.", user.first_name)
    update.message.reply_text('Щось ти трохи параноїк:)! '
                              'Розкажи мені ще щось про себе:)')

    return BIO


def bio(update, context):
    reply_keyboard = [['Так', 'Ні']]
    user = update.message.from_user
    response = update.message.text
    logger.info("Інфо про %s: %s", user.first_name, response)
    points = hand_estimation_function('user_photo_of_arm.jpg')
    wrist = calculate_wrist(points[0], points[1])
    best_weight = str(calculate_best_weight(wrist, int(current_user["age"]), int(current_user["height"])))
    message = 'Як я і обіцяв, ocm твоя оптимальна вага : ' + best_weight + '. Хочеш я порахую денну норму калорій, ' \
                                                         'якої слід дотримуватись, щоб мати цю вагу?:)'
    update.message.reply_text(message, reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    current_user["bio"] = response
    current_user["best_weight"] = best_weight
    with open('file.txt', 'w') as file:
        file.write(json.dumps(current_user))

    return CALORIES


def skip_bio(update, context):
    user = update.message.from_user
    logger.info("Користувач %s не біо.", user.first_name)
    update.message.reply_text('Ну і не треба!')
    return CALORIES


def calories(update, context):
    user = update.message.from_user
    response = update.message.text
    if response == 'Так':
        if current_user["gender"] == "Дівчина":
            calories = calculate_cal_woman(float(current_user["best_weight"]), int(current_user["age"]),
                                           int(current_user["height"]))
        else:
            calories = calculate_cal_man(float(current_user["best_weight"]), int(current_user["age"]),
                                           int(current_user["height"]))
        message = 'Тобі слід харчуватися на ' + str(calories) + ' кКал'
    else:
        message = 'Ну і не треба! Бувай, гарного тобі дня!'
    update.message.reply_text(message)
    return ConversationHandler.END


def cancel(update, context):
    user = update.message.from_user
    logger.info("Користувач %s завершив розмову.", user.first_name)
    update.message.reply_text('Бувай! Сподіваюсь поговорити якось ще:).',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    updater = Updater("1008400356:AAHNOVO7TZ8ik9r5HWLNzd6xdEqsaKSN7LY", use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO_BEFORE, PHOTO_AFTER, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            GENDER: [MessageHandler(Filters.regex('^(Хлопець|Дівчина|Щось інше)$'), gender)],

            PHOTO_OF_ARM: [MessageHandler(Filters.photo, photo_of_arm),
                           CommandHandler('skip', skip_photo_of_arm)],

            AGE: [MessageHandler(Filters.text, age), CommandHandler('skip', skip_age)],

            HEIGHT: [MessageHandler(Filters.text, height), CommandHandler('skip', skip_height)],

            LOCATION: [MessageHandler(Filters.location, location),
                       CommandHandler('skip', skip_location)],

            BIO: [MessageHandler(Filters.text, bio), CommandHandler('skip', skip_bio)],

            CALORIES: [MessageHandler(Filters.regex('^(Так|Ні)$'), calories)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)

    dp.add_error_handler(error)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()