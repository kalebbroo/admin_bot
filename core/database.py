import discord
from discord.ext import commands
from dotenv import load_dotenv
import sqlite3
import threading
import os
load_dotenv()

class Database(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot
        self.conn = self.load_db()
        self.c = self.conn.cursor() if self.conn else None
        self.backup_task = self.bot.loop.create_task(self.backup_database())
        self.db_lock = threading.Lock()

    @staticmethod
    def load_db():
        try:
            sqlite_db = os.getenv('SQLITEDB')
            conn = sqlite3.connect(sqlite_db)
            return conn
        except Exception as e:
            print(f"Error connecting to SQLite database: {e}")
            return None

    def setup_database(self, guild_id):
        try:
            self.c.execute(f"""
                CREATE TABLE IF NOT EXISTS users_{guild_id}(
                    id INTEGER PRIMARY KEY,
                    xp INTEGER,
                    level INTEGER,
                    last_message_time FLOAT,
                    spam_count INTEGER,
                    warnings TEXT,
                    message_count INTEGER,
                    last_warn_time FLOAT,
                    emoji_count INTEGER,
                    name_changes INTEGER
                )
            """)
            self.conn.commit()
        except Exception as e:
            print(f"Error setting up database for guild {guild_id}: {e}")


    def get_user(self, user_id, guild_id):
        with self.db_lock:
            # Check if the user is a bot
            member = self.bot.get_guild(guild_id).get_member(user_id)
            if member is not None and member.bot:
                return None
            
            self.c.execute(f"SELECT * FROM users_{guild_id} WHERE id = ?", (user_id,))
            data = self.c.fetchone()
            if data is None:
                data = (user_id, 0, 0, 0, 0, '[]', 0, None, 0, 0)  # Provide values for all 10 columns
                self.c.execute(f"INSERT INTO users_{guild_id} VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", data)
                self.conn.commit()

            # Convert the tuple to a dictionary
            user = {
                'id': data[0],
                'xp': data[1],
                'level': data[2],
                'last_message_time': data[3],
                'spam_count': data[4],
                'warnings': data[5],
                'message_count': data[6],
                'last_warn_time': data[7],
                'emoji_count': data[8],
                'name_changes': data[9]
            }
            return user


    def update_user(self, user, guild_id):
        with self.db_lock:
            self.c.execute(f'''UPDATE users_{guild_id} SET xp = ?, level = ?, 
                        last_message_time = ?, spam_count = ?, warnings = ?, 
                        message_count = ?, last_warn_time = ?, emoji_count = ?, name_changes = ? WHERE id = ?''', 
                        (user['xp'], user['level'], user['last_message_time'], user['spam_count'], 
                            user['warnings'], user['message_count'], user['last_warn_time'], 
                            user['emoji_count'], user['name_changes'], user['id']))
            self.conn.commit()


    async def get_top_users(self, guild_id, limit):
        with self.db_lock:
            self.c.execute(f"SELECT * FROM users_{guild_id} ORDER BY xp DESC LIMIT ?", (limit * 2,))  # Fetch twice the limit
            data = self.c.fetchall()

            # Convert the list of tuples to a list of dictionaries
            users = []
            for user_data in data:
                user = {
                    'id': user_data[0],
                    'xp': user_data[1],
                    'level': user_data[2],
                    'last_message_time': user_data[3],
                    'spam_count': user_data[4],
                    'warnings': user_data[5],
                    'message_count': user_data[6],
                    'last_warn_time': user_data[7],
                    'emoji_count': user_data[8],
                    'name_changes': user_data[9]
                }
                users.append(user)

            # Filter out users that are no longer in the server
            bot = self.bot  # Assuming that self.bot is your bot instance
            guild = bot.get_guild(guild_id)
            valid_users = []
            for user in users:
                try:
                    member = await guild.fetch_member(user['id'])
                    valid_users.append(user)
                    if len(valid_users) == limit:  # Stop when we have enough valid users
                        break
                except discord.NotFound:
                    continue

            return valid_users

    
    def get_rank(self, user_id, guild_id):
        with self.db_lock:
            # Get all users in the guild, ordered by XP in descending order
            self.c.execute(f"SELECT id FROM users_{guild_id} ORDER BY xp DESC")
            users = self.c.fetchall()

            # Find the rank of the user
            for i, user in enumerate(users, start=1):
                if user[0] == user_id:
                    return i
            return None  # Return None if the user is not found

    async def backup_database(self):
        for guild in self.bot.guilds:
            owner = guild.owner
            try:
                # Open the database file in binary mode
                with open(os.getenv('SQLITEDB'), 'rb') as fp:
                    # Send the database file
                    channel =  os.getenv('ADMIN_CHANNEL')
                    #await owner.send("Here is your database backup:", file=discord.File(fp, 'backup.db'), allowed_mentions=discord.AllowedMentions.none())
                    await self.bot.get_channel(channel).send("Database backup:", file=discord.File(fp, 'backup.db'), 
                                                                        allowed_mentions=discord.AllowedMentions.none())
            except Exception as e:
                print(f"Error backing up database: {e}")




    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        self.setup_database(guild.id)  # Set up the database for the guild


async def setup(bot:commands.Bot):
    await bot.add_cog(Database(bot))
