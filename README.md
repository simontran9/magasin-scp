# magasin-scp

My high school's intended rewards system

## Features

- Authentication with school email and option password reset
- Student account with associated rewards points balance
- Teacher's account with access to admin page for managing students account (e.g. distributing rewards points, students credentials if needed)
- Interface for purchasing rewards with their points with immediate updates to their account balance

## Usage

Use `docker compose up` to test the web app in a Docker container, and create a `.env` file inside the `magasinscp` package with the following variables

```
KEY=YOUR_KEY
MESSAGE_SENDER_EMAIL_ADDRESS=SENDER_EMAIL_ADDRESS
MESSAGE_SENDER_PASSWORD=SENDER_PASSWORD
STAFF_EMAIL_ADDRESS=STAFF_EMAIL_ADDRESS
```
