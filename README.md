# Pamplesneak

A real-time multiplayer word game built with Django and WebSocket technology. Players create and validate words in timed rounds while competing for points in an engaging party game format.

## Overview

Pamplesneak is a web-based multiplayer game where participants take turns creating and validating words. The game features real-time communication, progressive web app capabilities, and push notifications to enhance the gaming experience.

## Features

- **Real-time Multiplayer**: Live game sessions with WebSocket connections
- **Progressive Web App**: Installable on mobile devices with offline capabilities
- **Push Notifications**: Stay informed about game updates and turns
- **Responsive Design**: Optimized for both desktop and mobile experiences
- **User Authentication**: Secure login system with Django Allauth
- **Game Persistence**: Save and resume games with database storage
- **Admin Interface**: Comprehensive game management through Django admin

## Technology Stack

### Backend
- **Django 5.1.1**: Web framework and API development
- **Django Channels**: WebSocket support for real-time communication
- **Celery**: Background task processing and game state management
- **Redis**: Message broker and channel layer backend
- **SQLite/PostgreSQL**: Database with environment-based configuration

### Frontend
- **HTML5/CSS3**: Modern web standards
- **JavaScript**: Client-side interactivity and WebSocket handling
- **Tailwind CSS**: Utility-first CSS framework
- **jQuery**: DOM manipulation and AJAX requests

### Infrastructure
- **Docker**: Containerized deployment
- **Fly.io**: Cloud hosting platform
- **Daphne**: ASGI server for production deployment
- **Whitenoise**: Static file serving

## Architecture

### Application Structure
```
pamplesneak/
├── pamplesneak/          # Main Django project
│   ├── settings.py       # Configuration and environment variables
│   ├── urls.py          # URL routing
│   ├── asgi.py          # ASGI configuration for WebSockets
│   └── routing.py       # WebSocket routing
├── gameroom/            # Core game functionality
│   ├── models.py        # Game, Player, and Round models
│   ├── views.py         # Game logic and HTTP views
│   ├── consumers.py     # WebSocket consumers
│   ├── tasks.py         # Celery background tasks
│   └── utilities.py     # Game utilities and helpers
├── users/               # Custom user management
├── userprofile/         # User profile and game history
├── pwa/                 # Progressive web app configuration
├── templates/           # HTML templates
└── static/             # Static assets (CSS, JS, images)
```

### Real-time Communication Flow
1. Players join game rooms through WebSocket connections
2. Game state changes trigger Celery tasks
3. Tasks update the database and broadcast to all connected clients
4. Frontend receives updates and refreshes the UI accordingly

### Game State Management
- **Waiting**: Players join and wait for game start
- **Transition**: Brief preparation phase between rounds
- **Create**: Players submit words for validation
- **Play**: Other players validate submitted words
- **End**: Game completion and score calculation

## Installation

### Prerequisites
- Python 3.11+
- Redis server
- Node.js (for Tailwind CSS compilation)

### Local Development Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/pamplesneak2k24.git
cd pamplesneak2k24
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run migrations:
```bash
python manage.py migrate
python manage.py loaddata data/examplewords.json
```

6. Compile Tailwind CSS:
```bash
python manage.py tailwind install
python manage.py tailwind build
```

7. Start Redis server:
```bash
redis-server
```

8. Start Celery worker:
```bash
celery -A pamplesneak worker -l info
```

9. Run development server:
```bash
python manage.py runserver
```

## Deployment

### Fly.io Deployment

The application is configured for deployment on Fly.io with the following setup:

1. Install Fly CLI and authenticate
2. Deploy using the provided configuration:
```bash
fly deploy
```

### Environment Variables

Required environment variables for production:
- `SECRET_KEY`: Django secret key
- `DEBUG`: Set to "false" for production
- `DATABASE_URL`: Database connection string
- `REDIS_URL`: Redis connection URL
- `VAPID_PRIVATE_KEY`: Push notification private key
- `VAPID_PUBLIC_KEY`: Push notification public key
- `VAPID_ADMIN_EMAIL`: Admin email for push notifications

## Configuration

### Game Settings
Game parameters can be configured in the Django admin interface:
- Round duration
- Number of rounds per game
- Minimum players required
- Scoring system

### Push Notifications
The application supports web push notifications using VAPID keys. Configure the keys in your environment variables to enable this feature.

## API Endpoints

### Game Management
- `GET /gameroom/create/` - Create new game
- `POST /gameroom/join/` - Join existing game
- `GET /gameroom/{game_id}/` - Game lobby and play interface

### User Management
- `GET /accounts/login/` - User authentication
- `GET /user/games/` - User game history
- `POST /save_subscription/` - Push notification subscription

### WebSocket Endpoints
- `ws://localhost:8000/ws/gameroom/{game_id}/` - Real-time game communication

## Database Schema

### Core Models
- **Game**: Stores game instances, settings, and state
- **Player**: Links users to games with roles and scores
- **Round**: Manages individual game rounds and timing
- **CustomUser**: Extended Django user model

## Security Considerations

- CSRF protection enabled for all forms
- Secure WebSocket connections (WSS) in production
- Environment-based configuration management
- Input validation and sanitization
- HTTPS enforcement in production

## Performance Optimizations

- Redis-based session storage and caching
- Static file compression with Whitenoise
- Efficient WebSocket connection management
- Background task processing with Celery
- Database query optimization

## Browser Compatibility

Tested and optimized for:
- Chrome/Chromium browsers
- Firefox
- Safari
- Mobile browsers (iOS Safari, Chrome Mobile)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with appropriate tests
4. Submit a pull request

## Testing

Run the test suite:
```bash
python manage.py test
```

## License

This project is intended for portfolio demonstration purposes.

## Support

For questions or issues, please refer to the project documentation or create an issue in the repository.