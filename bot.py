import telebot
import google.generativeai as genai

# Telegram Bot Token (အသစ်ထည့်ပေးလိုက်ပါပြီ) နှင့် Gemini API Key
TELEGRAM_TOKEN = '9095644844:AAGB_To3jNbpl1eG9kNgXA_dmGM8CzgjFhs'
GEMINI_API_KEY = 'YOUR_GEMINI_API_KEY'  # မင်းရဲ့ Google Gemini API Key ထည့်ရန်

bot = telebot.TeleBot(TELEGRAM_TOKEN)
genai.configure(api_key=GEMINI_API_KEY)

# Gemini Model ကို သတ်မှတ်ခြင်း
generation_config = {"temperature": 0.7, "max_output_tokens": 500}
model = genai.GenerativeModel(model_name="gemini-pro", generation_config=generation_config)

# ၁။ Auto Welcome - Group ထဲ လူသစ်ဝင်လာရင် ကြိုဆိုခြင်း
@bot.message_handler(content_types=['new_chat_members'])
def welcome_new_member(message):
    for member in message.new_chat_members:
        name = member.first_name
        welcome_text = f"မင်္ဂလာပါ {name} ခင်ဗျာ! 🎉 ဒီ Group လေးမှ ကြိုဆိုပါတယ်။ အဆင်ပြေပျော်ရွှင်စွာ ဆွေးနွေးနိုင်ပါတယ်ခင်ဗျ။ 🌟"
        bot.reply_to(message, welcome_text)

# ၂။ Moderation - ဆဲဆိုသော စာသားများ သို့မဟုတ် Link များကို တားဆီးခြင်း
BAD_WORDS = ['ဆဲရေးစကား', 'badword1']  # လိုအပ်ပါက ထည့်ရန်

@bot.message_handler(func=lambda message: True, chat_types=['group', 'supergroup'])
def group_controller(message):
    if not message.text:
        return
        
    text_lower = message.text.lower()
    
    # ဆဲဆိုမှု စစ်ဆေးခြင်း
    for word in BAD_WORDS:
        if word in text_lower:
            try:
                bot.delete_message(message.chat.id, message.message_id)
                bot.send_message(message.chat.id, f"⚠️ ကျေးဇူးပြု၍ Group အတွင်း မသင့်လျော်သော စာသားများ မသုံးပါနဲ့ ခင်ဗျာ။")
            except Exception:
                pass
            return

    # ၃ & ၄။ AI Assistant - Bot ကို Tag ခေါ်လျှင် သို့မဟုတ် Reply ပေးလျှင် AI ဖြင့် ဖြေကြားခြင်း
    if (message.reply_to_message and message.reply_to_message.from_user.id == bot.get_me().id) or (f"@{bot.get_me().username}" in message.text):
        try:
            user_prompt = message.text.replace(f"@{bot.get_me().username}", "").strip()
            prompt = f"အောက်ပါမေးခွန်းကို ဖော်ရွေစွာနှင့် တိကျမှန်ကန်စွာ ဖြေကြားပေးပါ - {user_prompt}"
            response = model.generate_content(prompt)
            bot.reply_to(message, response.text)
        except Exception as e:
            bot.reply_to(message, "၀မ်းနည်းပါတယ်၊ အချက်အလက် ရှာဖွေရာတွင် အခက်အခဲ ရှိနေပါသည်ခင်ဗျ။")

# သီးသန့် Chat (Private Chat) တွင် မေးလာပါကလည်း AI ဖြင့် ဖြေကြားပေးရန်
@bot.message_handler(chat_types=['private'])
def private_chat(message):
    try:
        response = model.generate_content(message.text)
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, "၀မ်းနည်းပါတယ်၊ အခက်အခဲ ရှိနေပါသည်ခင်ဗျ။")

bot.infinity_polling()
