# Planetarium
Planetarium API IService

This API provides ease and clear way to handle of planetarium working.

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Getting access](#getting-access)
- [License](#license)
- [Running Tests](#running-tests)
- [Contact Information](#contact-information)

## Features
- JWT authentication
- Admin panel /admin
- Managing reservations and tickets
- Managing planetarium workers
- Creation and handling of planetarium domes, astronomy shows, show sessions, tickets.
- Validation tickets and working time of show speakers.

## Installation

Run with Docker:
- docker-compose up --build

## Getting access
- create user via api/user/register
- get access token via api/user/token

## License

All conditions for using this API [here](https://github.com/VladyslavBazhyn/Planetarium/blob/main/LICENSE)

## Running Tests

For running test:
- docker-compose exec planetarium sh    
- python manage.py test

## Contact Information

This project was created by [Vladyslav Bazhyn](https://github.com/VladyslavBazhyn/)
- Mail: mr.darmstadtium@gmail.com
- Telegram: [MrDarmstadtium](https://t.me/MrDarmstadtium)

### Prerequisites
- Python 3.x
- Docker
- Docker Compose
