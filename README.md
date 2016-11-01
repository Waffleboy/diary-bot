# What's DiaryBot?

Ever wanted to log your day to keep / send to someone, but too lazy to do it? DiaryBot was made with this exact scenario in mind.

DiaryBot is a telegram bot that sends your text to an email with the current date as the subject.

## Instructions (V0.2)

Version 0.2 is now a full bot, able to serve any number of users, and hence relies on a database. If you're looking for the old version that serves just one user but easy to set up, check branch 'v1'.

1) Fill in the following environment variables with your own:
 - TELEGRAM_DIARYBOT_TOKEN (Telegram API key)
 - PRODUCTION (set to any string)
 - DIARYBOT_DB (URL for postgres database)
 
2) Simply run the bot using python diarybot.py (alternatively, deploy to heroku)

3) In telegram to the bot, /register first, then you can /log <whatever you wanna say here> and thats it.

## Future Work
- Refactoring
- Unit tests
- Prevent suspension by heroku due to inactivity
