# MoneyBot 🤖💰

An automated Telegram bot that sends economic data updates to your channel, including USD/RUB exchange rate, Bitcoin price, and Moscow Exchange Index (IMOEX).

## Features

- 📊 **Real-time Economic Data**
  - USD to RUB exchange rate from Central Bank of Russia
  - Bitcoin price in USD with fallback sources
  - Moscow Exchange Index (IMOEX)

- 🔄 **Smart Updates**
  - Creates new message on first run
  - Edits the same message on subsequent runs
  - Only updates when data actually changes
  - Handles API failures gracefully

- 🕐 **Automated Scheduling**
  - Runs every 5 minutes
  - Moscow timezone aware

## Local Development

### Requirements
- Python 3.9+
- Telegram Bot Token
- Channel with bot as admin

### Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/MoneyBot.git
cd MoneyBot

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export TELEGRAM_TOKEN="your_bot_token_here"
export TELEGRAM_CHAT_ID="@your_channel_here"

# Run the bot
python main.py
```

## Schedule

The bot runs:
- **Frequency**: Every 5 minutes

## Error Handling

The bot includes robust error handling:
- Retries failed API requests up to 3 times
- Falls back to alternative data sources for Bitcoin price
- Shows "N/A" for unavailable data instead of crashing
- Recreates messages if Telegram message ID becomes invalid
- Comprehensive logging for debugging

## API Sources

- **USD/RUB**: [cbr-xml-daily.ru](https://www.cbr-xml-daily.ru) (Central Bank of Russia)
- **Bitcoin**: [CoinGecko](https://www.coingecko.com) with fallbacks to Binance, Coinbase, Blockchain.info
- **IMOEX**: [Moscow Exchange](https://www.moex.com) official API

## Message Format

```
🟢 USD   98.50₽
🟠 BTC   45,000.00$
🔴 IMOEX   2,800.00₽
Обновлено сегодня в 14:30 МСК
```

## Troubleshooting

### "TELEGRAM_TOKEN environment variable is not set"
- Make sure you've added `TELEGRAM_TOKEN` to GitHub Secrets
- Check the secret name matches exactly (case-sensitive)

### "Bad Request: MESSAGE_ID_INVALID"
- The bot will automatically create a new message
- This happens when the original message is deleted

### "Forbidden: bot is not a member of the channel"
- Add your bot as an administrator to the channel
- Make sure the channel ID is correct

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally
5. Submit a pull request

## License

MIT License - feel free to use and modify as needed.
