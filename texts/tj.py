CHOOSE_LANGUAGE = (
    "🚚 <b>Хуш омадед ба Akcorgo!</b>\n\n"
    "Борҳои худро аз Чин то Тоҷикистон осон ва ором пайгирӣ кунед.\n\n"
    "<blockquote>Лутфан забонро интихоб кунед:</blockquote>"
)

REGISTER = "📝 Сабти ном"
LOGIN = "🔐 Ворид шудан"

ASK_FULL_NAME = (
    "🧑 <b>Ном ва насаб</b>\n\n"
    "Лутфан ному насаби худро пурра ворид кунед."
)

ASK_PHONE = (
    "📞 <b>Рақами телефон</b>\n\n"
    "Лутфан рақами телефони худро ворид кунед.\n\n"
    "<blockquote>Рақам бояд танҳо аз 9 рақам иборат бошад.\n"
    "Мисол: <code>929999999</code></blockquote>"
)

ASK_CITY = (
    "🏬 <b>Филиалро интихоб кунед</b>\n\n"
    "Филиали асосии шумо аз рӯи ҳамин интихоб муайян мешавад."
)

REGISTRATION_COMPLETED = (
    "✅ <b>Сабти ном анҷом шуд!</b>\n\n"
    "🎉 Шумо ба Akcorgo пайваст шудед.\n"
    "🔐 Коди мизоҷии шумо: <code>{client_code}</code>\n\n"
    "<blockquote>Ин код барои пайгирии бор ва шинохтани мизоҷ истифода мешавад.</blockquote>"
)

LOGIN_SUCCESS = (
    "✅ <b>Шумо ворид шудед!</b>\n\n"
    "🔐 Коди мизоҷии шумо: <code>{client_code}</code>"
)

PHONE_NOT_FOUND = (
    "❌ <b>Ин рақам дар база ёфт нашуд.</b>\n\n"
    "<blockquote>Лутфан рақамро дуруст ворид кунед ё аввал сабти ном кунед.</blockquote>"
)

NAME_MISMATCH = (
    "❌ <b>Ному насаб мувофиқат накард.</b>\n\n"
    "<blockquote>Лутфан аз нав нависед.</blockquote>"
)

INVALID_PHONE = (
    "❌ <b>Рақами телефон нодуруст аст.</b>\n\n"
    "Лутфан рақамро танҳо аз 9 рақам ворид кунед.\n"
    "Мисол: <code>929999999</code>"
)

BACK = "⬅️ Бозгашт"

MENU_SEARCH_PARCEL = "🔍 Ҷустуҷӯи бор"
MENU_MY_PARCELS = "📦 Борҳои ман"
MENU_CALCULATOR = "🧮 Ҳисоби тахминӣ"
MENU_PROFILE = "👤 Профили ман"
MENU_WAREHOUSES = "🏬 Суроғаҳои склад"
MENU_PRICES = "💰 Нархҳо"
MENU_OPERATOR = "☎️ Оператор"

PARCEL_FOUND = (
    "📦 <b>Бори шумо ёфт шуд</b>\n\n"
    "<blockquote>"
    "🔢 Трек-код: <code>{track_code}</code>\n"
    "📍 Статус: <b>{dynamic_status}</b>\n"
    "🏬 Склад: <b>{destination_city}</b>\n"
    "🗓 Санаи қабул дар Чин: <b>{received_china_at}</b>\n"
    "🚚 Муддати тахминӣ: <b>{delivery_days}</b>"
    "</blockquote>\n\n"
    "<blockquote>⚠️ Вазн ва маблағ баъди расидан маълум мешавад.</blockquote>"
)

ASK_TRACK_CODE = (
    "🔍 <b>🔍 Ҷустуҷӯи бор</b>\n\n"
    "Трек-коди борро фиристед.\n\n"
    "<blockquote>Мисол: <code>SF123456789CN</code></blockquote>"
)

PARCEL_NOT_FOUND = (
    "❌ <b>Ин трек-код ҳоло дар база ёфт нашуд.</b>\n\n"
    "<blockquote>Эҳтимол:\n"
    "— бор ҳоло ба склади Чин нарасидааст;\n"
    "— трек-код хато ворид шудааст;\n"
    "— корманди карго ҳоло онро ба база илова накардааст.</blockquote>"
)

MY_PARCELS_EMPTY = (
    "📭 <b>Ҳоло барои шумо бор сабт нашудааст.</b>\n\n"
    "<blockquote>Вақте бори шумо ба склади Чин қабул мешавад, бот ба шумо хабар медиҳад.</blockquote>"
)

MY_PARCELS_TITLE = "📦 <b>Борҳои ман</b>"

MY_PARCELS_ITEM = (
    "📦 <b>{index}. Бор</b>\n"
    "🔢 Трек-код: <code>{track_code}</code>\n"
    "📍 Статус: <b>{dynamic_status}</b>\n"
    "🏬 Склад: <b>{destination_city}</b>\n"
    "🗓 Санаи қабул: <b>{received_china_at}</b>"
)

PROFILE = (
    "👤 <b>👤 Профили ман</b>\n\n"
    "<blockquote>"
    "🧑 Ном: <b>{full_name}</b>\n"
    "📞 Телефон: <code>{phone}</code>\n"
    "🏙 Шаҳр: <b>{city}</b>\n"
    "🔐 Коди мизоҷӣ: <code>{client_code}</code>\n"
    "🌐 Забон: <b>{language}</b>"
    "</blockquote>\n\n"
    "<blockquote>⚙️ Аз ин ҷо шумо метавонед маълумоти худро тағйир диҳед.</blockquote>"
)

PROFILE_BACK = "🏠 Менюи асосӣ"
PROFILE_UPDATED = "✅ <b>Маълумот нав шуд.</b>"
PHONE_ALREADY_USED = "❌ <b>Ин рақами телефон аллакай истифода мешавад.</b>"

CALCULATOR = (
    "🧮 <b>🧮 Ҳисоби тахминӣ</b>\n\n"
    "Бо кадом усул ҳисоб мекунед?"
)

CALCULATOR_BY_KG = "⚖️ Бо кг ҳисоб кардан"
CALCULATOR_BY_CUBE = "📐 Бо куб ҳисоб кардан"
CALCULATOR_RESULT = "💰 Нархи тахминӣ: <b>{amount} сомонӣ</b>"

CALCULATOR_CHOOSE = (
    "🧮 <b>🧮 Ҳисоби тахминӣ</b>\n\n"
    "Бо кадом усул ҳисоб мекунед?"
)

CALCULATOR_ASK_KG = (
    "⚖️ <b>Ҳисоб бо кг</b>\n\n"
    "Вазни тахминии борро бо кг ворид кунед.\n\n"
    "<blockquote>Мисол: <code>2.5</code></blockquote>"
)

CALCULATOR_ASK_CUBE = (
    "📐 <b>Ҳисоб бо куб</b>\n\n"
    "Ҳаҷми тахминии борро бо куб ворид кунед.\n\n"
    "<blockquote>Мисол: <code>0.35</code></blockquote>"
)

CALCULATOR_INVALID_NUMBER = (
    "❌ <b>Рақам нодуруст аст.</b>\n\n"
    "Лутфан рақами мусбат ворид кунед."
)

CALCULATOR_KG_RESULT = (
    "🧮 <b>🧮 Ҳисоби тахминӣ</b>\n\n"
    "<blockquote>"
    "⚖️ Вазн: <b>{amount} кг</b>\n"
    "💰 Нарх барои 1 кг: <b>{price} сомонӣ</b>\n"
    "📦 Ҳамагӣ: <b>{total} сомонӣ</b>"
    "</blockquote>\n\n"
    "<blockquote>⚠️ Ин ҳисоб тахминӣ аст. Вазн ва маблағи аниқ баъди расидани бор маълум мешавад.</blockquote>"
)

CALCULATOR_CUBE_RESULT = (
    "🧮 <b>🧮 Ҳисоби тахминӣ</b>\n\n"
    "<blockquote>"
    "📐 Ҳаҷм: <b>{amount} куб</b>\n"
    "💰 Нарх барои 1 куб: <b>{price} сомонӣ</b>\n"
    "📦 Ҳамагӣ: <b>{total} сомонӣ</b>"
    "</blockquote>\n\n"
    "<blockquote>⚠️ Ин ҳисоб тахминӣ аст. Ҳаҷм ва маблағи аниқ баъди расидани бор маълум мешавад.</blockquote>"
)

WAREHOUSE_ACTIVE = (
    "🏬 <b>Суроғаи склад — {city}</b>\n\n"
    "{caption}"
)

WAREHOUSE_INACTIVE = (
    "❌ <b>Ҳозирча барои ин минтақа филиал фаъол нест.</b>\n\n"
    "<blockquote>Лутфан филиали дастрасро интихоб кунед ё ба оператор нависед.</blockquote>"
)

WAREHOUSE_ADDRESS_MISSING = (
    "❌ <b>Адреси ин склад ҳоло дар база илова нашудааст.</b>\n\n"
    "<blockquote>Лутфан ба оператор нависед.</blockquote>"
)

DELIVERY_UNAVAILABLE = (
    "❌ <b>Ҳозирча хизматрасонии доставка фаъол нест.</b>\n\n"
    "<blockquote>Лутфан борро аз склад гирифта баред.</blockquote>"
)

DELIVERY_REQUEST = (
    "📍 <b>Адреси доставка</b>\n\n"
    "Лутфан адреси худро равон кунед."
)

DELIVERY_REQUEST_ACCEPTED = (
    "✅ <b>Дархости доставка қабул шуд.</b>\n\n"
    "<blockquote>Оператор баъд аз санҷиш бо шумо тамос мегирад.</blockquote>"
)

DELIVERY_NOT_FOUND = (
    "❌ <b>Бори расида барои доставка ёфт нашуд.</b>"
)

DELIVERY_CONFIRM = (
    "🚚 <b>Дархости доставка</b>\n\n"
    "🔢 Трек-код: <code>{track_code}</code>\n"
    "👤 Мизоҷ: <b>{full_name}</b>\n"
    "📞 Телефон: <code>{phone}</code>\n"
    "🏬 Склад: <b>{destination_city}</b>\n"
    "📍 Адрес: <b>{delivery_address}</b>\n\n"
    "<blockquote>Маълумот дуруст аст?</blockquote>"
)

DELIVERY_TERMS = (
    "🚚 <b>Хизматрасонии доставка</b>\n\n"
    "🏙 {inside_city}\n\n"
    "🚕 {outside_city}\n\n"
    "📍 <b>Лутфан адреси худро равон кунед:</b>"
)

DELIVERY_SEND_ADDRESS = "📍 <b>Лутфан адреси худро равон кунед:</b>"
DELIVERY_CANCELLED = "❌ <b>Дархости доставка бекор карда шуд.</b>"

NOTIFICATION_CHINA_RECEIVED = (
    "📦 <b>Бори шумо қабул шуд</b>\n\n"
    "🔢 Трек-код: <code>{track_code}</code>\n"
    "📍 Статус: <b>{status}</b>\n"
    "🏬 Склад: <b>{destination_city}</b>\n"
    "🗓 Санаи қабул дар Чин: <b>{received_china_at}</b>\n"
    "🚚 Муддати тахминӣ: <b>{delivery_days}</b>\n\n"
    "<blockquote>⚠️ Вазн ва маблағ баъди расидан маълум мешавад.</blockquote>"
)

NOTIFICATION_ARRIVED = (
    "🎉 <b>Бори шумо ба склади {city} расид!</b>\n\n"
    "🔢 Трек-код: <code>{track_code}</code>\n"
    "📍 Статус: <b>Омода барои гирифтан</b>\n\n"
    "<blockquote>Шумо метавонед борро аз склад гирифта баред ё хизматрасонии доставка интихоб кунед.</blockquote>"
)

OPERATOR = (
    "☎️ <b>Оператор</b>\n\n"
    "{contacts}\n\n"
    "<blockquote>Шумо метавонед саволи худро ҳамин ҷо нависед. Паёми шумо ба админ фиристода мешавад.</blockquote>"
)

OPERATOR_NOT_SET = (
    "❌ <b>Тамоси оператор ҳоло сабт нашудааст.</b>"
)

PRICES = (
    "💰 <b>💰 Нархҳо</b>\n\n"
    "<blockquote>"
    "🇨🇳 Чин → Тоҷикистон\n\n"
    "📦 1 кг: <b>{price_per_kg_tjs} сомонӣ</b>\n"
    "📐 1 куб: <b>{price_per_cube_tjs} сомонӣ</b>\n"
    "🚚 Муддати тахминӣ: <b>{delivery_days}</b>"
    "</blockquote>\n\n"
    "<blockquote>⚠️ Вазн ва маблағи аниқ баъди расидани бор маълум мешавад.</blockquote>"
)

MENU_PROHIBITED = "🚫 Манъшудаҳо"

PROHIBITED_GOODS = (
    "🚫 <b>Товарҳои манъшуда</b>\n\n"
    "<blockquote>"
    "Ин намуди товарҳо қабул карда намешаванд:\n\n"
    "— дору ва маводи тиббӣ бе иҷозат\n"
    "— моеъҳо, равғанҳо, химия\n"
    "— батарея, powerbank, аккумулятор\n"
    "— силоҳ, корд, ашёи хатарнок\n"
    "— маҳсулоти зудвайроншаванда\n"
    "— пул, карта, ҳуҷҷатҳои шахсӣ\n"
    "— бренд/копия, агар хавфи гумрукӣ дошта бошад\n\n"
    "Агар шубҳа дошта бошед, пеш аз фармоиш ба оператор нависед."
    "</blockquote>"
)
