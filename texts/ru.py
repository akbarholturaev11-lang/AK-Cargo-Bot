CHOOSE_LANGUAGE = (
    "🚚 <b>Добро пожаловать в Akcorgo!</b>\n\n"
    "Отслеживайте свои грузы из Китая в Таджикистан.\n\n"
    "<blockquote>Пожалуйста, выберите язык:</blockquote>"
)

REGISTER = "📝 Регистрация"
LOGIN = "🔐 Войти"

ASK_FULL_NAME = (
    "🧑 <b>Имя и фамилия</b>\n\n"
    "Введите полное имя и фамилию."
)

ASK_PHONE = (
    "📞 <b>Номер телефона</b>\n\n"
    "Введите ваш номер телефона.\n\n"
    "<blockquote>Номер должен состоять только из 9 цифр.\n"
    "Пример: <code>929999999</code></blockquote>"
)

ASK_CITY = (
    "🏬 <b>Выберите филиал</b>\n\n"
    "Ваш основной филиал будет определён по этому выбору."
)

REGISTRATION_COMPLETED = (
    "✅ <b>Регистрация завершена!</b>\n\n"
    "🎉 Вы стали клиентом Akcorgo.\n"
    "🔐 Ваш клиентский код: <code>{client_code}</code>\n\n"
    "<blockquote>Этот код используется для отслеживания груза и идентификации клиента.</blockquote>"
)

LOGIN_SUCCESS = (
    "✅ <b>Вы вошли в аккаунт!</b>\n\n"
    "🔐 Ваш клиентский код: <code>{client_code}</code>"
)

PHONE_NOT_FOUND = (
    "❌ <b>Этот номер не найден в базе.</b>\n\n"
    "<blockquote>Введите номер правильно или сначала зарегистрируйтесь.</blockquote>"
)

NAME_MISMATCH = (
    "❌ <b>Имя и фамилия не совпали.</b>\n\n"
    "<blockquote>Пожалуйста, введите заново.</blockquote>"
)

INVALID_PHONE = (
    "❌ <b>Неверный номер телефона.</b>\n\n"
    "Введите номер только из 9 цифр.\n"
    "Пример: <code>929999999</code>"
)

BACK = "⬅️ Назад"

MENU_SEARCH_PARCEL = "🔍 Найти груз"
MENU_MY_PARCELS = "📦 Мои грузы"
MENU_CALCULATOR = "🧮 Примерный расчёт"
MENU_PROFILE = "👤 Мой профиль"
MENU_WAREHOUSES = "🏬 Адреса складов"
MENU_PRICES = "💰 Цены"
MENU_OPERATOR = "☎️ Оператор"

PARCEL_FOUND = (
    "📦 <b>Ваш груз найден</b>\n\n"
    "<blockquote>"
    "🔢 Трек-код: <code>{track_code}</code>\n"
    "📍 Статус: <b>{dynamic_status}</b>\n"
    "🏬 Склад: <b>{destination_city}</b>\n"
    "🗓 Дата приёма в Китае: <b>{received_china_at}</b>\n"
    "🚚 Примерный срок: <b>{delivery_days}</b>"
    "</blockquote>\n\n"
    "<blockquote>⚠️ Вес и сумма будут известны после прибытия.</blockquote>"
)

ASK_TRACK_CODE = (
    "🔍 <b>Поиск груза</b>\n\n"
    "Отправьте трек-код груза.\n\n"
    "<blockquote>Пример: <code>SF123456789CN</code></blockquote>"
)

PARCEL_NOT_FOUND = (
    "❌ <b>Этот трек-код пока не найден в базе.</b>\n\n"
    "<blockquote>Возможно:\n"
    "— груз ещё не прибыл на склад в Китае;\n"
    "— трек-код введён неправильно;\n"
    "— сотрудник карго ещё не добавил его в базу.</blockquote>"
)

MY_PARCELS_EMPTY = (
    "📭 <b>Для вас пока нет зарегистрированных грузов.</b>\n\n"
    "<blockquote>Когда ваш груз будет принят на складе в Китае, бот отправит уведомление.</blockquote>"
)

MY_PARCELS_TITLE = "📦 <b>Мои грузы</b>"

MY_PARCELS_ITEM = (
    "📦 <b>{index}. Груз</b>\n"
    "🔢 Трек-код: <code>{track_code}</code>\n"
    "📍 Статус: <b>{dynamic_status}</b>\n"
    "🏬 Склад: <b>{destination_city}</b>\n"
    "🗓 Дата приёма: <b>{received_china_at}</b>"
)

PROFILE = (
    "👤 <b>👤 Мой профиль</b>\n\n"
    "<blockquote>"
    "🧑 Имя: <b>{full_name}</b>\n"
    "📞 Телефон: <code>{phone}</code>\n"
    "🏙 Город: <b>{city}</b>\n"
    "🔐 Код клиента: <code>{client_code}</code>\n"
    "🌐 Язык: <b>{language}</b>"
    "</blockquote>\n\n"
    "<blockquote>⚙️ Здесь вы можете изменить свои данные.</blockquote>"
)

PROFILE_BACK = "🏠 Главное меню"
PROFILE_UPDATED = "✅ <b>Данные обновлены.</b>"
PHONE_ALREADY_USED = "❌ <b>Этот номер телефона уже используется.</b>"

CALCULATOR = (
    "🧮 <b>🧮 Примерный расчёт</b>\n\n"
    "Каким способом хотите рассчитать?"
)

CALCULATOR_BY_KG = "⚖️ По килограммам"
CALCULATOR_BY_CUBE = "📐 По кубам"
CALCULATOR_RESULT = "💰 Примерная стоимость: <b>{amount} сомонӣ</b>"

CALCULATOR_CHOOSE = (
    "🧮 <b>🧮 Примерный расчёт</b>\n\n"
    "Каким способом хотите рассчитать?"
)

CALCULATOR_ASK_KG = (
    "⚖️ <b>Расчёт по кг</b>\n\n"
    "Введите примерный вес груза в кг.\n\n"
    "<blockquote>Пример: <code>2.5</code></blockquote>"
)

CALCULATOR_ASK_CUBE = (
    "📐 <b>Расчёт по кубам</b>\n\n"
    "Введите примерный объём груза в кубах.\n\n"
    "<blockquote>Пример: <code>0.35</code></blockquote>"
)

CALCULATOR_INVALID_NUMBER = (
    "❌ <b>Неверное число.</b>\n\n"
    "Пожалуйста, введите положительное число."
)

CALCULATOR_KG_RESULT = (
    "🧮 <b>🧮 Примерный расчёт</b>\n\n"
    "<blockquote>"
    "⚖️ Вес: <b>{amount} кг</b>\n"
    "💰 Цена за 1 кг: <b>{price} сомонӣ</b>\n"
    "📦 Итого: <b>{total} сомонӣ</b>"
    "</blockquote>\n\n"
    "<blockquote>⚠️ Это примерный расчёт. Точный вес и сумма будут известны после прибытия груза.</blockquote>"
)

CALCULATOR_CUBE_RESULT = (
    "🧮 <b>🧮 Примерный расчёт</b>\n\n"
    "<blockquote>"
    "📐 Объём: <b>{amount} куб</b>\n"
    "💰 Цена за 1 куб: <b>{price} сомонӣ</b>\n"
    "📦 Итого: <b>{total} сомонӣ</b>"
    "</blockquote>\n\n"
    "<blockquote>⚠️ Это примерный расчёт. Точный объём и сумма будут известны после прибытия груза.</blockquote>"
)

WAREHOUSE_ACTIVE = (
    "🏬 <b>Адрес склада — {city}</b>\n\n"
    "{caption}"
)

WAREHOUSE_INACTIVE = (
    "❌ <b>Сейчас для этого региона филиал недоступен.</b>\n\n"
    "<blockquote>Пожалуйста, выберите доступный филиал или напишите оператору.</blockquote>"
)

WAREHOUSE_ADDRESS_MISSING = (
    "❌ <b>Адрес этого склада пока не добавлен.</b>\n\n"
    "<blockquote>Пожалуйста, напишите оператору.</blockquote>"
)

DELIVERY_UNAVAILABLE = (
    "❌ <b>Сейчас доставка недоступна.</b>\n\n"
    "<blockquote>Пожалуйста, заберите груз со склада.</blockquote>"
)

DELIVERY_REQUEST = (
    "📍 <b>Адрес доставки</b>\n\n"
    "Пожалуйста, отправьте ваш адрес."
)

DELIVERY_REQUEST_ACCEPTED = (
    "✅ <b>Заявка на доставку принята.</b>\n\n"
    "<blockquote>Оператор свяжется с вами после проверки.</blockquote>"
)

DELIVERY_NOT_FOUND = (
    "❌ <b>Прибывший груз для доставки не найден.</b>"
)

DELIVERY_CONFIRM = (
    "🚚 <b>Заявка на доставку</b>\n\n"
    "🔢 Трек-код: <code>{track_code}</code>\n"
    "👤 Клиент: <b>{full_name}</b>\n"
    "📞 Телефон: <code>{phone}</code>\n"
    "🏬 Склад: <b>{destination_city}</b>\n"
    "📍 Адрес: <b>{delivery_address}</b>\n\n"
    "<blockquote>Данные верны?</blockquote>"
)

DELIVERY_TERMS = (
    "🚚 <b>Услуга доставки</b>\n\n"
    "🏙 {inside_city}\n\n"
    "🚕 {outside_city}\n\n"
    "📍 <b>Пожалуйста, отправьте ваш адрес:</b>"
)

DELIVERY_SEND_ADDRESS = "📍 <b>Пожалуйста, отправьте ваш адрес:</b>"
DELIVERY_CANCELLED = "❌ <b>Заявка на доставку отменена.</b>"

NOTIFICATION_CHINA_RECEIVED = (
    "📦 <b>Ваш груз принят</b>\n\n"
    "🔢 Трек-код: <code>{track_code}</code>\n"
    "📍 Статус: <b>{status}</b>\n"
    "🏬 Склад: <b>{destination_city}</b>\n"
    "🗓 Дата приёма в Китае: <b>{received_china_at}</b>\n"
    "🚚 Примерный срок: <b>{delivery_days}</b>\n\n"
    "<blockquote>⚠️ Вес и сумма будут известны после прибытия.</blockquote>"
)

NOTIFICATION_ARRIVED = (
    "🎉 <b>Ваш груз прибыл на склад {city}!</b>\n\n"
    "🔢 Трек-код: <code>{track_code}</code>\n"
    "📍 Статус: <b>Готов к получению</b>\n\n"
    "<blockquote>Вы можете забрать груз со склада или выбрать услугу доставки.</blockquote>"
)

OPERATOR = (
    "☎️ <b>Оператор</b>\n\n"
    "{contacts}\n\n"
    "<blockquote>Вы можете написать свой вопрос здесь. Сообщение будет отправлено администратору.</blockquote>"
)

OPERATOR_NOT_SET = (
    "❌ <b>Контакты оператора пока не указаны.</b>"
)

PRICES = (
    "💰 <b>💰 Цены</b>\n\n"
    "<blockquote>"
    "🇨🇳 Китай → Таджикистан\n\n"
    "📦 1 кг: <b>{price_per_kg_tjs} сомонӣ</b>\n"
    "📐 1 куб: <b>{price_per_cube_tjs} сомонӣ</b>\n"
    "🚚 Примерный срок: <b>{delivery_days}</b>"
    "</blockquote>\n\n"
    "<blockquote>⚠️ Точный вес и сумма будут известны после прибытия.</blockquote>"
)

MENU_PROHIBITED = "🚫 Запрещённые товары"

PROHIBITED_GOODS = (
    "🚫 <b>Запрещённые товары</b>\n\n"
    "<blockquote>"
    "Эти товары не принимаются:\n\n"
    "— лекарства и медицинские товары без разрешения\n"
    "— жидкости, масла, химия\n"
    "— батареи, powerbank, аккумуляторы\n"
    "— оружие, ножи, опасные предметы\n"
    "— скоропортящиеся товары\n"
    "— деньги, карты, личные документы\n"
    "— бренд/копии, если есть таможенный риск\n\n"
    "Если сомневаетесь, напишите оператору до заказа."
    "</blockquote>"
)
