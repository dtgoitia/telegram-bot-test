from telegram_bot.config import get_config


def main() -> None:
    token = get_config('TOKEN')


if __name__ == '__main__':
    main()
