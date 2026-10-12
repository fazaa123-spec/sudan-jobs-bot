import os
import re
import sqlite3
import logging
import random
from datetime import datetime, date
import telebot
from telebot import types

logging.basicConfig(level=logging.INFO)

def get_env_config():
    token = os.getenv("BOT_TOKEN")
    admin_id = os.getenv("ADMIN_ID")
    if not token or not admin_id:
        print("❌ ضيف BOT_TOKEN و ADMIN_ID في Render > Environment Variables")
        exit(1)
    return token, int(admin_id)

TOKEN, ADMIN_ID = get_env_config()
bot = telebot.TeleBot(TOKEN, parse_mode="HTML", threaded=False)

PRIVACY_URL = "https://telegra.ph/sudan-jobs-bot-%D8%B3%D9%8A%D8%A7%D8%B3%D8%A9-%D8%A7%D9%84%D8%AE%D8%B5%D9%88%D8%B5%D9%8A%D8%A9-10-08"
FORM_SEEKER = "https://forms.gle/UrFeBcVXvZCYxdUH6"
REPORT_FORM = "https://forms.gle/Yhj1D3RregwxU3or5"

CHANNELS = {
    "🇸🇦 الرياض": "@SudanJobs2riyadh",
    "🇪🇬 القاهرة": "@SudanJobs1cairo",
    "🇸🇩 الخرطوم": "@SudanJobs3khartoum",
    "🇦🇪 دبي": "@SudanJobsNow",
    "🇶🇦 قطر": "@SudanJobsqatar"
}

BANNED_WORDS = ["رسوم", "عمولة", "ادفع", "تحويل", "خاص", "بنات", "جنس", "سلف", "مقابل", "اشتراك"]

TATWEER_TIPS = [
    "💡 <b>نصيحة اليوم:</b>\nاتعلم مهارة واحدة كل 3 شهور من اليوتيوب مجانا (اكسل، تصميم، مونتاج) بتزيد راتبك 200%",
    "📚 <b>كورس مجاني مع شهادة:</b>\nموقع Alison.com فيهو شهادات معتمدة مجانية",
    "🔥 <b>طور سيرتك:</b>\nاعمل CV احترافي في Canva",
    "🎯 <b>قاعدة ذهبية:</b>\nما تقدم بنفس الـ CV لكل الوظائف. عدل الهدف حسب الوظيفة",
    "💪 <b>تحدي 7 ايام:</b>\nكل يوم اتعلم 20 كلمة انجليزية خاصة بمجالك",
    "🧠 <b>كسر ملل:</b>\nاتعلم تكتب ايميل رسمي احترافي",
    "💼 <b>سر المقابلات:</b>\nقبل المقابلة اكتب في يوتيوب 'اسئلة مقابلة + اسم وظيفتك'",
    "🚀 <b>حركة سمحة:</b>\nصور فيديو 30 ثانية تعرف فيهو عن نفسك عربي/انجليزي"
]

# === قاعدة البيانات مع اصلاح تلقائي ===
conn = sqlite3.connect("jobs.db", check_same_thread=False)
conn.execute("""CREATE TABLE IF NOT EXISTS jobs
(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, job TEXT, city TEXT, details TEXT, status TEXT, created TIMESTAMP, created_date TEXT)""")
conn.commit()

# اصلاح للملف القديم اللي عامل الخطأ في صورتك
try:
    conn.execute("ALTER TABLE jobs ADD COLUMN created_date TEXT")
    conn.commit()
    print("تم تحديث قاعدة البيانات ✅")
except Exception as e:
    print(f"قاعدة البيانات جاهزة: {e}")

conn.commit()

user_temp = {}

def main_menu():
    m = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    m.add(types.KeyboardButton("🔍 أبحث عن وظيفة"), types.KeyboardButton("📢 عندي وظيفة"))
    m.add(types.KeyboardButton("📄 سجل كـ باحث عن عمل"), types.KeyboardButton("✨ طور نفسك"))
    m.add(types.KeyboardButton("🚨 بلاغ عن وظيفة وهمية"), types.KeyboardButton("⚖️ سياسة الخصوصية"))
    return m

def cancel_menu():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True)
    m.add("⬅️ إلغاء ورجوع")
    return m

def check_rate_limit(user_id):
    today = str(date.today())
    try:
        count = conn.execute("SELECT COUNT(*) FROM jobs WHERE user_id=? AND created_date=?", (user_id, today)).fetchone()[0]
        return count < 3
    except:
        return True

@bot.message_handler(commands=['start'])
def start_handler(message):
    user_temp.pop(message.chat.id, None)
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("✅ موافق وادخل البوت", callback_data="agree"))
    kb.add(types.InlineKeyboardButton("📄 سياسة الخصوصية", url=PRIVACY_URL))
    welcome = "🇸🇩 <b>حبابك عشرة!</b>\n\n💼 منصة مجانية 100%\n⚠️ لو زول طلب رسوم بلغ طوالي\n\nدوس موافق 👇"
    bot.send_message(message.chat.id, welcome, reply_markup=kb)

@bot.callback_query_handler(func=lambda c: c.data == "agree")
def on_agree(call):
    bot.answer_callback_query(call.id, "حبابك 🇸🇩")
    bot.send_message(call.message.chat.id, "تم ✅ اختار:", reply_markup=main_menu())

@bot.message_handler(commands=['فحص', 'check'])
def check_status(message):
    if message.from_user.id!= ADMIN_ID:
        bot.send_message(message.chat.id, "البوت شغال ✅ /start"); return
    try:
        pending = conn.execute("SELECT COUNT(*) FROM jobs WHERE status='pending'").fetchone()[0]
        total = conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
        today = conn.execute("SELECT COUNT(*) FROM jobs WHERE created_date=?", (str(date.today()),)).fetchone()[0]
        bot.send_message(message.chat.id, f"📊 معلق: {pending}\nالكلي: {total}\nاليوم: {today}")
    except Exception as e:
        bot.send_message(message.chat.id, f"البوت شغال ✅\nخطأ بسيط في العد: {e}")

@bot.message_handler(func=lambda m: m.text and "أبحث عن وظيفة" in m.text)
def jobs_menu(message):
    kb = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    for city in CHANNELS.keys():
        kb.add(types.KeyboardButton(city))
    kb.add(types.KeyboardButton("⬅️ رجوع"))
    bot.send_message(message.chat.id, "اختار مدينتك 👇", reply_markup=kb)

@bot.message_handler(func=lambda m: m.text in CHANNELS)
def send_channel_link(message):
    city = message.text
    chan = CHANNELS[city]
    link = f"https://t.me/{chan.replace('@','')}"
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(f"ادخل قناة {city} 🚀", url=link))
    bot.send_message(message.chat.id, f"وظائف {city}:\n{link}", reply_markup=kb)

@bot.message_handler(func=lambda m: m.text and "سجل كـ باحث" in m.text)
def seeker_register(message):
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("📝 فتح الاستمارة", url=FORM_SEEKER))
    bot.send_message(message.chat.id, f"سجل:\n{FORM_SEEKER}", reply_markup=kb)

@bot.message_handler(func=lambda m: m.text and "بلاغ عن وظيفة" in m.text)
def report_scam(message):
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("🚨 بلاغ فوري", url=REPORT_FORM))
    bot.send_message(message.chat.id, f"بلغ هنا:\n{REPORT_FORM}", reply_markup=kb)

@bot.message_handler(func=lambda m: m.text and "سياسة الخصوصية" in m.text)
def send_privacy(message):
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("📄 السياسة", url=PRIVACY_URL))
    bot.send_message(message.chat.id, "خصوصيتك محفوظة 👇", reply_markup=kb)

@bot.message_handler(func=lambda m: m.text and "طور نفسك" in m.text)
def tatweer(message):
    tip = random.choice(TATWEER_TIPS)
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton("📚 كورسات مجانية", url="https://alison.com"))
    kb.add(types.InlineKeyboardButton("🎨 اعمل CV", url="https://www.canva.com/resumes/"))
    kb.add(types.InlineKeyboardButton("✨ نصيحة تانية", callback_data="more_tip"))
    bot.send_message(message.chat.id, tip, reply_markup=kb)

@bot.callback_query_handler(func=lambda c: c.data == "more_tip")
def more_tip(call):
    tip = random.choice(TATWEER_TIPS)
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton("📚 كورسات", url="https://alison.com"))
    kb.add(types.InlineKeyboardButton("✨ تانية", callback_data="more_tip"))
    bot.edit_message_text(tip, call.message.chat.id, call.message.message_id, reply_markup=kb)
    bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda m: m.text and ("رجوع" in m.text or "إلغاء" in m.text))
def go_back(message):
    user_temp.pop(message.chat.id, None)
    bot.send_message(message.chat.id, "رجعت 👌", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text and "عندي وظيفة" in m.text)
def employer_start(message):
    if not check_rate_limit(message.chat.id):
        bot.send_message(message.chat.id, "⚠️ وصلت الحد اليومي (3 وظائف). تعال بكرة", reply_markup=main_menu())
        return
    user_temp[message.chat.id] = {}
    bot.send_message(message.chat.id, "الوظيفة شنو؟", reply_markup=cancel_menu())
    bot.register_next_step_handler(message, step_country)

def step_country(m):
    if "رجوع" in m.text or "إلغاء" in m.text:
        go_back(m); return
    user_temp[m.chat.id]['job'] = m.text.strip()[:100]
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    for city in CHANNELS.keys():
        kb.add(types.KeyboardButton(city))
    kb.add(types.KeyboardButton("⬅️ إلغاء ورجوع"))
    bot.send_message(m.chat.id, "في ياتو مدينة؟", reply_markup=kb)
    bot.register_next_step_handler(m, step_details)

def step_details(m):
    if "رجوع" in m.text or "إلغاء" in m.text:
        go_back(m); return
    if m.text not in CHANNELS:
        bot.send_message(m.chat.id, "اختار من الازرار"); bot.register_next_step_handler(m, step_details); return
    user_temp[m.chat.id]['city'] = m.text
    bot.send_message(m.chat.id, "التفاصيل + رقم واتساب واحد", reply_markup=cancel_menu())
    bot.register_next_step_handler(m, step_preview)

def step_preview(m):
    if "رجوع" in m.text or "إلغاء" in m.text:
        go_back(m); return
    text = m.text or ""
    low = text.lower()
    for w in BANNED_WORDS:
        if w in low:
            bot.send_message(m.chat.id, f"⚠️ كلمة '{w}' ممنوعة"); bot.register_next_step_handler(m, step_preview); return
    if "http" in low or "t.me" in low or "www." in low:
        bot.send_message(m.chat.id, "⚠️ ممنوع الروابط"); bot.register_next_step_handler(m, step_preview); return
    if len(re.findall(r'\d{9,}', text)) > 2:
        bot.send_message(m.chat.id, "⚠️ رقم واحد بس"); bot.register_next_step_handler(m, step_preview); return
    if len(text) < 20:
        bot.send_message(m.chat.id, "⚠️ اكتب تفاصيل اكتر"); bot.register_next_step_handler(m, step_preview); return

    d = user_temp[m.chat.id]
    conn.execute("INSERT INTO jobs (user_id, job, city, details, status, created, created_date) VALUES (?,?,?,?,?,?,?)",
                 (m.chat.id, d['job'], d['city'], text, 'pending', datetime.now(), str(date.today())))
    conn.commit()
    jid = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    user_temp.pop(m.chat.id, None)

    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("✅ نشر", callback_data=f"ok_{jid}"), types.InlineKeyboardButton("❌ رفض", callback_data=f"no_{jid}"))
    bot.send_message(ADMIN_ID, f"🔔 طلب جديد #{jid}\n💼 {d['job']} في {d['city']}\n\n{text}", reply_markup=kb)
    bot.send_message(m.chat.id, f"تم #{jid} ✅ قيد المراجعة", reply_markup=main_menu())

@bot.callback_query_handler(func=lambda c: c.data.startswith(("ok_", "no_")))
def handle_admin(call):
    if call.from_user.id!= ADMIN_ID:
        bot.answer_callback_query(call.id, "للادمن فقط"); return
    jid = int(call.data.split("_")[1])
    row = conn.execute("SELECT user_id, job, city, details FROM jobs WHERE id=?", (jid,)).fetchone()
    if not row:
        bot.answer_callback_query(call.id, "انتهى"); return
    uid, job, city, details = row
    if call.data.startswith("ok_"):
        kb_chan = types.InlineKeyboardMarkup(row_width=1)
        kb_chan.add(types.InlineKeyboardButton("🚨 بلاغ عن وظيفة وهمية", url=REPORT_FORM))
        kb_chan.add(types.InlineKeyboardButton("📄 سجل كـ باحث عن عمل", url=FORM_SEEKER))
        try:
            bot.send_message(CHANNELS[city], f"📢 <b>وظيفة في {city}</b>\n\n💼 <b>{job}</b>\n\n📋 {details}\n\n━━━━━━━━━━━━\n⚠️ مجانية 100%\nلو طلبو قروش دوس بلاغ 👇", reply_markup=kb_chan)
            conn.execute("UPDATE jobs SET status='approved' WHERE id=?", (jid,))
            conn.commit()
            bot.send_message(uid, f"🎉 اتنشرت في {city}")
            bot.edit_message_text(f"تم النشر ✅ #{jid}", call.message.chat.id, call.message.message_id)
        except Exception as e:
            bot.send_message(call.message.chat.id, f"خطأ: {e}\nاتأكد البوت ادمن في القناة")
    else:
        conn.execute("UPDATE jobs SET status='rejected' WHERE id=?", (jid,))
        conn.commit()
        bot.send_message(uid, "❌ تم الرفض")
        bot.edit_message_text(f"تم الرفض ❌ #{jid}", call.message.chat.id, call.message.message_id)

print(f"البوت شغال ✅ ADMIN={ADMIN_ID}")
bot.infinity_polling(skip_pending=True)
