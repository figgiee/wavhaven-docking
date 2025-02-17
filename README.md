<<<<<<< HEAD
# WavHaven - Beat Marketplace Platform

WavHaven is a modern beat marketplace platform where producers can showcase and sell their beats, and customers can discover and purchase them. The platform features a state-of-the-art audio player with persistent playback across page navigation.

## Features

### Audio Player
- Persistent audio playback across page navigation
- Interactive waveform visualization using WaveSurfer.js
- Continuous playback state management
- Volume control with mute toggle
- Track seeking with progress bar
- Loop mode support
- Keyboard shortcuts for playback control

### Beat Management
- Beat upload with cover image support
- Multiple audio format support (MP3, WAV)
- Genre categorization
- BPM and key information
- Custom tagging system
- Price setting and licensing options

### User Features
- User profiles with customizable avatars
- Producer portfolios
- Beat favorites system
- Purchase history
- Follow system for producers
- Comment system on beats
- User dashboard with analytics

### Shopping Features
- Shopping cart system
- Multiple license types
- Secure payment processing
- Download management
- Purchase history

### Search and Discovery
- Advanced beat search
- Genre-based filtering
- Tag-based search
- Producer search
- Sort by popularity/date/price

## Tech Stack

### Frontend
- HTML5/CSS3
- TailwindCSS for styling
- Alpine.js for reactivity
- WaveSurfer.js for waveform visualization
- Howler.js for audio playback
- Font Awesome for icons

### Backend
- Django 4.2+
- Django REST Framework for API
- SQLite (development) / PostgreSQL (production)
- Python 3.8+

### Key Libraries
- Pillow for image processing
- python-magic for file type detection
- whitenoise for static file serving
- django-storages for file storage
- pydub for audio processing

## Setup and Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/wavhaven.git
cd wavhaven
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
# Edit .env with your settings
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Create superuser:
```bash
python manage.py createsuperuser
```

7. Run development server:
```bash
python manage.py runserver
```

## Development Guidelines

### Code Structure
- `store/` - Main application directory
  - `templates/` - HTML templates
  - `static/` - Static files (JS, CSS, images)
  - `models.py` - Database models
  - `views.py` - View controllers
  - `urls.py` - URL routing

### Commit Guidelines
- Use clear, descriptive commit messages
- Start with a verb (Add, Update, Fix, etc.)
- Reference issue numbers when applicable

### Code Style
- Follow PEP 8 for Python code
- Use consistent indentation (4 spaces for Python, 2 spaces for HTML/JS)
- Add comments for complex logic
- Use meaningful variable and function names

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- WaveSurfer.js for waveform visualization
- Howler.js for audio handling
- TailwindCSS for styling
- Alpine.js for reactivity
- Django community for the amazing framework
=======
# WavHaven BACKEND

## Venv
The venv includes only django for now, i decided not to use restapi yet

## Tech stack
- HTML/CSS
- JavaScript
- Alpine.js
- Tailwind CSS
- Python
- Django
- REST Framework
- SQLite

## Functionality
- Create accounts
- Log in
- Upload beats
- Manage beats
- Buy/View beats
- Search for keywords
- View sales, beat views, analytics, etc
- Admin portal
>>>>>>> 43e6d2dca8d245f001e712240bfadecec0527f1e
