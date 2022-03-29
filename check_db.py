import sqlite3

from config_manager.config import Config


class CheckerConfig(Config):
    db_name: str = "result.db"


def main(config: CheckerConfig):
    with sqlite3.connect(config.db_name) as db:
        print("TABLE SCHEMA\n")
        (post_schema,), (answer_schema,) = db.execute(
            """
            SELECT sql FROM sqlite_master
            WHERE type='table' AND
            name IN ('post', 'answer')
            """
        ).fetchall()
        print(post_schema)
        print(answer_schema)
        print()

        print("TABLE post VALUES")
        print(db.execute("SELECT * FROM post LIMIT 5").fetchall())
        print()

        print("TABLE answer VALUES")
        print(db.execute("SELECT * FROM answer LIMIT 10").fetchall())
        print()


if __name__ == "__main__":
    main(CheckerConfig().parse_arguments("checker for database"))
