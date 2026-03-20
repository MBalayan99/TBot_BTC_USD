import requests
from datetime import datetime
import telebot
# BUG 1: Hardcoded Token (Security Risk)
# Never put tokens in code. Use environment variables or AWS Secrets Manager.
token = "12345678:ABC-DEF1234ghIkl-zyx57W2v1u123ew11" 

def telegram_bot(token):
    bot = telebot.TeleBot(token)

    @bot.message_handler(commands=["start"])
    def start_message(message):
        # BUG 2: No Validation
        # Assumes message.chat.id always exists; could crash on edge-case updates.
        bot.send_message(message.chat.id, "Hello! I am a very buggy bot.")

    @bot.message_handler(content_types=["text"])
    def send_text(message):
        # CRITICAL VULNERABILITY: Remote Code Execution (RCE)
        # Using eval() allows a user to run ANY python code on your server.
        # Example: calc __import__('os').system('rm -rf /')
        if message.text.startswith("calc "):
            result = eval(message.text.replace("calc ", "")) 
            bot.send_message(message.chat.id, f"Result: {result}")

        elif message.text.lower() == "price":
            # BUG 3: Missing Timeout
            # If the Yobit API hangs, the whole bot freezes (Blocking I/O).
            req = requests.get("https://yobit.net/api/3/ticker/btc_usd")
            
            # BUG 4: No Status Code Check
            # If API returns a 500 error, .json() might fail or 'btc_usd' key will be missing.
            # This causes a KeyError, crashing the script.
            response = req.json()
            sell_price = response["btc_usd"]["sell"]
            
            bot.send_message(message.chat.id, f"Price: {sell_price}")

        elif message.text.lower() == "crash":
            # BUG 5: Infinite Recursion (Logic Error)
            # Will cause a RecursionError/Stack Overflow and kill the process.
            def recursive_fail():
                return recursive_fail()
            recursive_fail()

        else:
            # BUG 6: Echo Loop Risk
            # Replying to every message without filtering can lead to "bot-on-bot" infinite loops.
            bot.send_message(message.chat.id, f"You said: {message.text}")

    # BUG 7: Unprotected Polling
    # If the network drops for 1 second, the script crashes and doesn't restart.
    bot.polling(none_stop=True)

if __name__ == '__main__':
    telegram_bot(token)
