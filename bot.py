import telebot
from telebot import types
import os

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

CHANNELS = {
    "🇸🇦 الرياض": "https://t.me/SudanJobs2riyadh",
    "🇪🇬 القاهرة": "https://t.me/SudanJobs1cairo",
    "🇸🇩 الخرطوم": "https://t.me/SudanJobs3khartoum",
    "🇦🇪 دبي": "https://t.me/SudanJobsNow",
    "🇶🇦 قطر": "https://t.me/SudanJobsqatar"
}

FORM_EMPLOYER = "https://forms.gle/XXXX"
FORM_SEEKER = "https://forms.gle/YYYY"

WARNING_TEXT = """
⚠️ تنبيه مهم:
- كل الوظائف مجانية 100%
- لا تدفع أي رسوم توظيف
- نحن منصة عرض فقط
- لو طلبو منك قروش بلغنا فورا
"""

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("🔍 أبحث عن وظيفة", "📢 عندي وظيفة - انشر مجانا")
    markup.add("📄 سجل كـ باحث عن عمل", "⚠️ تنبيه هام")
    bot.send_message(message.chat.id, "🇸🇩 مرحبا بيك في بوت وظائف السودانيين\n\nأكبر تجمع لوظائف السودانيين في الخليج ومصر والسودان\nاختار من القائمة تحت:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🔍 أبحث عن وظيفة")
def jobs_menu(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    for city in CHANNELS.keys():
        markup.add(types.KeyboardButton(city))
    markup.add("⬅️ رجوع")
    bot.send_message(message.chat.id, "اختار مدينتك:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text in CHANNELS)
def send_channel(message):
    city = message.text
    link = CHANNELS[city]
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(f"ادخل قناة {city}", url=link))
    bot.send_message(message.chat.id, f"✅ وظائف {city} 👇\n{link}", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "📢 عندي وظيفة - انشر مجانا")
def employer_form(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📋 افتح فورم نشر الوظيفة", url=FORM_EMPLOYER))
    bot.send_message(message.chat.id, "انشر وظيفتك مجانا ويشوفها آلاف السودانيين 👇", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "📄 سجل كـ باحث عن عمل")
def seeker_form(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📝 سجل بياناتك", url=FORM_SEEKER))
    bot.send_message(message.chat.id, "سجل بياناتك ونوصلها للشركات مجانا 👇", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "⚠️ تنبيه هام")
def warning(message):
    bot.send_message(message.chat.id, WARNING_TEXT)

@bot.message_handler(func=lambda m: m.text == "⬅️ رجوع")
def back(message):
    start(message)

print("البوت شغال...")
bot.infinity_polling()
