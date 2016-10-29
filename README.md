# What's DiaryBot?

Ever wanted to log your day to keep / send to someone, but too lazy to do it? DiaryBot was made with this exact scenario in mind.

DiaryBot is a telegram bot that sends your text to an email with the current date as the subject.

## Instructions

1) Fill in the following environment variables with your own:
 - TELEGRAM_DIARYBOT_TOKEN
 - MY_EMAIL_ADDRESS
 - MY_EMAIL_PASSWORD
 - EMAIL_TO_SEND_TO
 
2) Simply run the bot, (Replace the userNotAuthorised() function with your own telegram handle) and use /log <whatever you wanna say here> and thats it.

## Future Work
This was a very quick script, so currently it only does the job of sending the text via email to the specified email address. 

Future work such as making it usable for multiple people is in the works.
