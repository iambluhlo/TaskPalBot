# Imported libraries
import telebot
import config
from config import bot_db
from telebot import types

# Activates bot using api key
bot = telebot.TeleBot(config.API_KEY)

# Bot cursor that points to the database + Database tables insert syntax for inserting users' information
dbcursor = bot_db.cursor(buffered=True)
users_table = 'INSERT INTO users (chat_id, name) VALUES (%s, %s) ON DUPLICATE KEY UPDATE name = %s'
tasks_list_table = 'INSERT INTO tasks_list (list_name, chat_id) VALUES (%s, %s)'
tasks_table = 'INSERT INTO tasks (task_description, due_time, status, list_id) VALUES (%s, %s, %s, %s)'

# States that declares at what part user is (Handles messages in certain order)
user_state = {}
start_state = "start"
newlist_state = "Add a New Task List"
newtask_state = "Add a New Task"
duetime_state = "Add a Due Time"


# Main Menu buttons for start state
def main_menu_buttons():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn1 = types.KeyboardButton('See Tasks List')
    btn2 = types.KeyboardButton('Add a New Task List')
    markup.add(btn1, btn2)
    return markup


# Back to the Main Menu button
def back_to_main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn1 = types.KeyboardButton('Back to The Main Menu')
    markup.add(btn1)
    return markup


# Bot Starter. Sends Welcome message. Inserts users information such as name, last name and chat id (which is unique for
# every user) into "users table". In the end it changes "user state" to proceed to the next state.
@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "hello dear!, Please select one of the options below", reply_markup=main_menu_buttons())
    users_table_values = (message.chat.id, f'({message.from_user.first_name} {message.from_user.last_name})',
                          f'({message.from_user.first_name} {message.from_user.last_name})')
    try:
        dbcursor.execute('SELECT COUNT(*) FROM users WHERE chat_id = %s', (message.chat.id,))
        user_exists = dbcursor.fetchone()[0]
        if user_exists == 0:
            dbcursor.execute(users_table, users_table_values)
            bot_db.commit()

            user_state[message.chat.id] = start_state

        else:
            user_state[message.chat.id] = start_state

    except Exception as e:
        bot.send_message(message.chat.id, f'error: {e}')


# This state occurs when user selects 'Add a New Task List' option from keyboard. It simply asks a name for the task
# list but doesn't insert anything to the database. In the end it changes "user state" to proceed to the next state.
@bot.message_handler(
    func=lambda message: message.text == 'Add a New Task List' and user_state.get(message.chat.id) == start_state)
def list_name(message):
    bot.reply_to(message, "please choose a name for your task list", reply_markup=back_to_main_menu())
    user_state[message.chat.id] = newlist_state


# In this state, based on what user desired to name their task list, function insert the list name into 'tasks_list'
# table. It also avoids entering duplicated list names. Then asks user to write a task for the next state.
# In the end it changes "user state" to proceed to the next state.
@bot.message_handler(func=lambda message: user_state.get(message.chat.id) == newlist_state)
def new_list(message):
    try:

        dbcursor.execute('SELECT COUNT(*) FROM tasks_list WHERE list_name = %s', (message.text,))
        list_exists = dbcursor.fetchone()[0]
        if list_exists == 0:
            tasks_list_table_values = (message.text, message.chat.id)
            dbcursor.execute(tasks_list_table, tasks_list_table_values)
            bot_db.commit()
            bot.send_message(message.chat.id, f'Task list created successfully! now you can write a task')
            user_state[message.chat.id] = newtask_state
        else:
            bot.send_message(message.chat.id, f'Task list already exists!')

    except Exception as e:
        bot.send_message(message.chat.id, f'Error: {e}')


# This function catches user's written task to the 'tasks table' and links the task to the tasks_list using
# tasks_list id. By default, sets task's status to "pending" since the tasks is newly added.
@bot.message_handler(func=lambda message: user_state.get(message.chat.id) == newtask_state)
def new_task_shit3(message):
    try:

        dbcursor.execute('SELECT COUNT(*) FROM tasks WHERE task_description = %s', (message.text,))
        list_exists = dbcursor.fetchone()[0]

        if list_exists == 0:
            dbcursor.execute('SELECT id FROM tasks_list WHERE chat_id = %s ORDER BY id DESC LIMIT 1',
                             (message.chat.id,))
            list_id = dbcursor.fetchone()[0]
            print(list_id)
            bot_db.commit()
            tasks_table_values = (message.text, None, 'pending', list_id)
            dbcursor.execute(tasks_table, tasks_table_values)
            bot_db.commit()
            bot.send_message(message.chat.id, 'task has been added successfully!')
        else:
            bot.send_message(message.chat.id, 'Task already exists!')
    except Exception as e:
        bot.send_message(message.chat.id, f'Error: {e}')


# This state occurs when user selects 'Add a New Task List' option from keyboard. It shows user's tasks list
# inside inline keyboad feature, so when user select the task list, they'll be able to do the changes to the list.
@bot.message_handler(func=lambda message: message.text == "See Tasks List")
def show_tasks(message):
    markup = types.InlineKeyboardMarkup()
    try:
        dbcursor.execute('SELECT list_name FROM tasks_list')
        tasks_lists = dbcursor.fetchall()
        for list_name in tasks_lists:
            markup.add(types.InlineKeyboardButton(f'{list_name[0]}', callback_data=f'{list_name[0]}'))

        # Send a message with the inline keyboard
        bot.send_message(message.chat.id, f"kosisher", reply_markup=markup)
    except Exception as e:
        bot.send_message(message.chat.id, f'Error: {e}')
    finally:
        dbcursor.close()

# Bot activator
if __name__ == '__main__':
    print("bot is running ...")
    bot.polling()
