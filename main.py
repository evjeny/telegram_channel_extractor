import asyncio

import aiosqlite
from config_manager.config import Config
from telethon import TelegramClient
from telethon import errors
import tqdm


class ExtractorConfig(Config):
    api_id: int
    api_hash: str
    channel_name: str
    channel_posts_limit: int = None
    channel_comments_limit: int = None
    db_name: str = "result.db"
    takeout: bool = False


async def setup_database(db: aiosqlite.Connection):
    await db.executescript(
        """
        DROP TABLE IF EXISTS post;
        CREATE TABLE post(
            message_id INTEGER PRIMARY KEY,
            date TIMESTAMP,
            text TEXT,
            from_id INTEGER,
            views INTEGER
        );

        DROP TABLE IF EXISTS answer;
        CREATE TABLE answer(
            message_id INTEGER PRIMARY KEY,
            date TIMESTAMP,
            text TEXT,
            from_id INTEGER,
            post_id INTEGER,
            reply_to_msg_id INTEGER,
            FOREIGN KEY(post_id) REFERENCES post(message_id) ON DELETE CASCADE
        );
        """
    )


async def message_handler(client: TelegramClient, db: aiosqlite.Connection, channel, message, config: ExtractorConfig):
    def _get_from_id(message):
        _from_id = None
        if hasattr(message.from_id, "user_id"):
            _from_id = message.from_id.user_id
        elif hasattr(message.from_id, "channel_id"):
            _from_id = message.from_id.channel_id
        return _from_id

    await db.execute(
        """
        INSERT INTO post(message_id, date, text, from_id, views)
        VALUES (?, ?, ?, ?, ?)
        """,
        (message.id, message.date, message.message, _get_from_id(message), message.views)
    )
    
    try:
        async for answer in client.iter_messages(channel, limit=config.channel_comments_limit, reply_to=message.id):
            await db.execute(
                """
                INSERT INTO answer(message_id, date, text, from_id, post_id, reply_to_msg_id)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (answer.id, answer.date, answer.message, _get_from_id(answer), message.id, answer.reply_to.reply_to_msg_id)
            )
    except:
        pass

    await db.commit()


async def message_fetcher(client: TelegramClient, db: aiosqlite.Connection, config: ExtractorConfig):
    channel = await client.get_input_entity(config.channel_name)
                
    pbar = tqdm.tqdm(desc="parsing posts")
    async for message in client.iter_messages(channel, limit=config.channel_posts_limit):
        if message.peer_id.channel_id != channel.channel_id:
            continue

        await message_handler(client, db, channel, message, config)
        pbar.update()


async def main(config: ExtractorConfig):
    global fetched_posts

    client = TelegramClient("extractor", config.api_id, config.api_hash)

    async with client, aiosqlite.connect(config.db_name) as db:
        await setup_database(db)

        if config.takeout:
            print("Starting in takeout mode...")
            try:
                async with client.takeout() as takeout:
                    await message_fetcher(takeout, db, config)
            except errors.TakeoutInitDelayError as e:
                print(f"Must wait {e.seconds} before takeout")
        else:
            print("Starting in client mode...")
            await message_fetcher(client, db, config)
        

if __name__ == "__main__":
    config = ExtractorConfig().parse_arguments("Telegram channel extractor")
    asyncio.run(main(config))
