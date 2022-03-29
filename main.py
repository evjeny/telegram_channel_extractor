import asyncio
import json
import time

from config_manager.config import Config
from telethon import TelegramClient
from telethon import errors
import tqdm


fetched_posts: list[dict] = []


class ExtractorConfig(Config):
    api_id: int
    api_hash: str
    channel_name: str
    channel_posts_limit: int = None
    channel_comments_limit: int = None
    json_path: str = "result.json"
    takeout: bool = False


def message_to_dict(message) -> dict:
    return {
        "id": message.id,
        "date": message.date,
        "text": message.message
    }


async def message_fetcher(client):
    channel = await client.get_input_entity(config.channel_name)
                
    pbar = tqdm.tqdm(desc="parsing posts")
    async for message in client.iter_messages(channel, limit=config.channel_posts_limit):
        if message.peer_id.channel_id != channel.channel_id:
            continue

        cur_message = message_to_dict(message)
        cur_message["views"] = message.views
        cur_message["comments"] = []
        
        try:
            async for answer in client.iter_messages(channel, limit=config.channel_comments_limit, reply_to=message.id):
                cur_answer = message_to_dict(answer)
                cur_answer["reply_to_msg_id"] = answer.reply_to.reply_to_msg_id
                cur_message["comments"].append(cur_answer)
        except:
            pass
        
        fetched_posts.append(cur_message)
        pbar.update()


async def main(config: ExtractorConfig):
    global fetched_posts

    client = TelegramClient("extractor", config.api_id, config.api_hash)

    if config.takeout:
        while True:
            try:
                async with client, client.takeout() as takeout:
                    await message_fetcher(takeout)
            except errors.TakeoutInitDelayError as e:
                print(f"Must wait {e.seconds} before takeout...")
                time.sleep(e.seconds)
                print("Trying again...")
            break
    else:
        async with client:
            await message_fetcher(client)
        

if __name__ == "__main__":
    config = ExtractorConfig().parse_arguments("Telegram channel extractor")

    try:
        asyncio.run(main(config))
    except KeyboardInterrupt:
        with open(config.json_path, "w+", encoding="utf-8") as f:
            json.dump(fetched_posts, f, default=str, ensure_ascii=False)
