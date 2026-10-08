import telebot
from telebot import types
import os
from flask import Flask
import threading

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

# روابطك الرسمية المحمية
PRIVACY_URL = "https://telegra.ph/sudan-jobs-bot-%D8%B3%D9%8A%D8%A7%D8%B3%D8%A9-%D8%A7%D9%84%D8%AE%D8%B5%D9%88%D8%B5%D9%8A%D8%A9-10-08"
FORM_EMPLOYER = "https://forms.gle/HHnGdygrcQj7c1Qv5"
FORM_SEEKER = "https://forms.gle/UrFeBcVXvZCYxdUH6"
REPORT_FORM = "https://forms.gle/Yhj1D3RregwxU3or5"

CHANNELS = {
    "🇸🇦 الرياض": "https://t.me/SudanJobs2riyadh",
    "🇪🇬 القاهرة": "https://t.me/SudanJobs1cairo",
    "🇸🇩 الخرطوم": "https://t.me/SudanJobs3khartoum",
    "🇦🇪 دبي": "https://t.me/SudanJobsNow",
    "🇶🇦 قطر": "https://t.me/SudanJobsqatar"
}

def main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("🔍 أبحث عن وظيفة", "📢 عندي وظيفة")
    markup.add("📄 سجل كـ باحث عن عمل", "🚨 بلاغ عن وظيفة وهمية")
    markup.add("⚖️ سياسة الخصوصية")
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ موافق وادخل البوت", callback_data="agree"))
    markup.add(types.InlineKeyboardButton("📄 سياسة الخصوصية", url=PRIVACY_URL))
    bot.send_message(message.chat.id,
        "🇸🇩 مرحبا بيك في SudanJobs\n\n"
        "⚠️ نحن منصة عرض فقط، لسنا شركة توظيف.\n"
        "كل الوظائف مجانية 100% - ممنوع دفع رسوم.\n\n"
        "بضغطك موافق، أنت توافق على سياسة الخصوصية والشروط.",
        reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "agree")
def agree(call):
    bot.send_message(call.message.chat.id, "تم ✅ القائمة الرئيسية:", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "🔍 أبحث عن وظيفة")
def jobs_menu(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    for city in CHANNELS.keys():
        markup.add(types.KeyboardButton(city))
    markup.add("⬅️ رجوع")
    bot.send_message(message.chat.id, "اختار مدينتك 👇", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text in CHANNELS)
def send_channel(message):
    link = CHANNELS[message.text]
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(f"ادخل قناة {message.text} ✅", url=link))
    bot.send_message(message.chat.id, f"وظائف {message.text} 👇\n{link}\n\n⚠️ مجانا - لا تدفع أي رسوم", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "📢 عندي وظيفة")
def employer_form(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📝 افتح فورم النشر", url=FORM_EMPLOYER))
    bot.send_message(message.chat.id, "انشر وظيفتك مجانا - المراجعة خلال 6 ساعات 👇\n⚠️ ممنوع طلب رسوم من المتقدمين", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "📄 سجل كـ باحث عن عمل")
def seeker_form(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📄 سجل بياناتك", url=FORM_SEEKER))
    bot.send_message(message.chat.id, "سجل كـ باحث عن عمل - بياناتك تحذف بعد 30 يوم 🔒", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🚨 بلاغ عن وظيفة وهمية")
def report_form(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🚨 قدم بلاغ سري", url=REPORT_FORM))
    bot.send_message(message.chat.id, "بلاغك سري وسيتم الحظر خلال 24 ساعة - ساعدنا نحارب النصب 👇", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "⚖️ سياسة الخصوصية")
def privacy(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📄 افتح سياسة الخصوصية", url=PRIVACY_URL))
    bot.send_message(message.chat.id, "سياسة الخصوصية والشروط القانونية 👇", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "⬅️ رجوع")
def back(message):
    bot.send_message(message.chat.id, "القائمة الرئيسية:", reply_markup=main_menu())

# حماية من النوم في Render
app = Flask('')
@app.route('/')
def home(): return "SudanJobs Bot - Protected & Live"
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
threading.Thread(target=run_flask).start()

print("البوت المحمي النهائي شغال...")
bot.infinity_polling()
