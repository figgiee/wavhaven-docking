# WavHaven - Beat Marketplace

A modern beat marketplace platform built with Django and Alpine.js.

## Features

- User authentication and profiles
- Beat upload and management
- Audio playback with visualization using Howler.js and Web Audio API
- Beat preview and purchase functionality
- Responsive design with Tailwind CSS
- Real-time search and filtering
- Secure payment processing
- User favorites and playlists
- Admin dashboard for content management

## Technologies Used

### Backend
- Django
- PostgreSQL
- Redis for caching
- Celery for background tasks
- Django REST Framework for API

### Frontend
- Alpine.js for reactivity
- Tailwind CSS for styling
- Howler.js for audio playback
- Web Audio API for visualization
- Font Awesome icons
- HTMX for dynamic content

### Infrastructure
- Docker for containerization
- Nginx as reverse proxy
- Gunicorn as WSGI server
- AWS S3 for file storage
- Stripe for payments

## Getting Started

1. Clone the repository:
```bash
git clone https://github.com/yourusername/wavhaven.git
cd wavhaven
```

2. Create and activate a virtual environment:
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
```

6. Create a superuser:
```bash
python manage.py createsuperuser
```

7. Run the development server:
```bash
python manage.py runserver
```

## Development

### Frontend Development

The frontend uses Alpine.js for reactivity and Tailwind CSS for styling. The main components are:

1. Audio Player
   - Uses Howler.js for audio playback
   - Web Audio API for frequency visualization
   - Supports play/pause, seek, volume control
   - Playlist management with shuffle and loop modes

2. Beat Cards
   - Preview functionality
   - Quick purchase options
   - Favorite/unfavorite actions
   - Share buttons

3. Search and Filters
   - Real-time search results
   - Genre and tag filtering
   - Price range slider
   - Sort options

### Backend Development

The Django backend provides:

1. REST API endpoints for:
   - Beat upload and management
   - User authentication
   - Purchase processing
   - Favorites and playlists
   - Search and filtering

2. Admin interface for:
   - Content moderation
   - User management
   - Sales tracking
   - Analytics

## Deployment

1. Build the Docker images:
```bash
docker-compose build
```

2. Start the services:
```bash
docker-compose up -d
```

3. Run migrations:
```bash
docker-compose exec web python manage.py migrate
```

4. Collect static files:
```bash
docker-compose exec web python manage.py collectstatic
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Django community
- Alpine.js team
- Tailwind CSS team
- Howler.js developers
- All contributors and users

## Tag Management

WavHaven uses django-taggit for managing tags on beats. This provides a robust tagging system with the following features:

### Basic Tag Operations

```python
# Adding tags to a beat
beat.tags.add("hip-hop", "dark", "trap")

# Removing tags
beat.tags.remove("trap")

# Setting tags (replaces existing)
beat.tags.set(["hip-hop", "melodic"])

# Getting all tags
tags = beat.tags.names()
```

### Advanced Tag Features

1. **Similar Beats**
   ```python
   # Get beats with similar tags
   similar_beats = beat.get_similar_beats(limit=5)
   ```

2. **Tag Statistics**
   ```python
   # Get tag usage statistics
   tag_cloud = beat.get_tag_cloud()
   
   # Get most popular tags
   popular_tags = Beat.get_popular_tags(limit=10)
   ```

3. **Tag Search**
   ```python
   # Search beats by tags
   matching_beats = Beat.search_by_tags(["hip-hop", "dark"])
   ```

### Template Usage

```html
<!-- Displaying tags -->
{% for tag in beat.tags.all %}
    <a href="{% url 'beat_list' %}?tag={{ tag.name }}" class="tag">{{ tag.name }}</a>
{% endfor %}

<!-- Popular tags -->
{% for tag in popular_tags %}
    <a href="{% url 'beat_list' %}?tag={{ tag.name }}" class="tag">
        {{ tag.name }} ({{ tag.count }})
    </a>
{% endfor %}
```

### API Endpoints

Tags are included in the Beat API responses:

```json
{
    "id": 1,
    "title": "Summer Vibes",
    "tags": ["hip-hop", "summer", "melodic"],
    // ... other fields
}
```

### Form Handling

When creating or editing beats, tags can be entered as comma-separated values:

```html
<input type="text" name="tags" class="tag-input" placeholder="Enter tags separated by commas">
```

The form will automatically convert the comma-separated string into individual tags.
