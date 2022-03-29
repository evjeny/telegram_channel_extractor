# telegram_channel_extractor

Export channel posts with text of comments

---

## Requirements

Python: `3.9.11`

Packages: `python -m pip install -r requirements.txt`

## Run

To use script, you should get `api_id` and `api_hash` from the [Telegram site](https://my.telegram.org/apps): fields called **App api_id** and **App api_hash** respectively 

By default you can run parsing of all the posts (starting from most recent) without any limitations on number of comments:

```bash
python main.py --api_id 12345 \
    --api_hash 0123456789abcdef0123456789abcdef \
    --channel_name $some_channel_you_may_know \
    --db_name $some_channel_you_may_know.db
```

To limit posts' or comments count, you can use `--channel_posts_limit` and `--channel_comments_limit` parameters, e.g. get maximum 10 posts with 50 comments each:

```bash
python main.py --api_id 12345 \
    --api_hash 0123456789abcdef0123456789abcdef \
    --channel_name $some_channel_you_may_know \
    --db_name $some_channel_you_may_know.db \
    --channel_posts_limit 10 \
    --channel_comments_limit 50
```

## Fetch data from database

Data is being saved to sqlite3 database.
To get data schema you can run [check_db.py](check_db.py):

```bash
python check_db.py --db_name $some_channel_you_may_know.db
```
