import os
from supabase import create_client
from aiogram import Bot, Dispatcher, executor, types

# Hidden Keys (we will add these to Render later)
TOKEN = os.getenv("BOT_TOKEN")
SB_URL = os.getenv("SUPABASE_URL")
SB_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SB_URL, SB_KEY)
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    uid = message.from_user.id
    # Check if user exists
    user = supabase.table("users").select("*").eq("user_id", uid).execute()

    if not user.data:
        # Check for referrer in the link (e.g., /start 12345)
        ref_id = message.get_args()
        ref_id = int(ref_id) if ref_id.isdigit() else None

        # Create new user
        supabase.table("users").insert({"user_id": uid, "referred_by": ref_id}).execute()

        # IF there is a referrer, give them $5 bonus!
        if ref_id:
            supabase.rpc("increment_balance", {"row_id": ref_id, "amount": 5}).execute()
            await bot.send_message(ref_id, "🎁 You received a $5 Referral Bonus!")

    await message.answer("🚀 Welcome to BitcoinFun! Click Wallet to see your balance.")

if __name__ == '__main__':
    executor.start_polling(dp)
