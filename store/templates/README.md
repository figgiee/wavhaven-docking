# Templates Documentation

## Directory Structure

```
store/templates/
├── store/
│   ├── auth/           # Authentication related templates
│   ├── beats/          # Beat listing, detail, and upload templates
│   ├── cart/           # Shopping cart and checkout templates
│   ├── explore/        # Explore and discovery templates
│   ├── producers/      # Producer profiles and listings
│   ├── profile/        # User profile templates
│   ├── components/     # Reusable template components
│   ├── base.html       # Base template with common structure
│   ├── landing_page.html # Homepage template
│   └── search.html     # Search results template
```

## Template Descriptions

### Base Template
- `base.html`: The main template that all other templates extend from
  - Includes common CSS and JavaScript dependencies
  - Defines the basic page structure and navigation
  - Handles Alpine.js initialization and global state
  - Manages audio player functionality

### Authentication Templates
- Located in `auth/`
- Handles user registration, login, and password reset
- Consistent styling with the main application theme

### Beat Templates
- Located in `beats/`
- `beat_list.html`: Grid display of beats with filtering and sorting
- `beat_detail.html`: Detailed view of a single beat with:
  - Audio player integration
  - Tag management
  - Similar beats suggestions
  - Comments section
- `upload.html`: Beat upload form with:
  - File upload handling
  - Tag management
  - Genre and metadata input

### Cart Templates
- Located in `cart/`
- Shopping cart management
- Checkout process
- Order confirmation

### Component Templates
- Located in `components/`
- Reusable template fragments
- Includes common UI elements like:
  - Audio player controls
  - Comment sections
  - Tag displays
  - Loading states

### Search Template
- `search.html`: Advanced search interface with:
  - Tag filtering
  - Genre filtering
  - Price and BPM range filters
  - Sort options
  - Results display

## Template Features

### Tag Management
All templates support django-taggit integration:
- Tag display with count indicators
- Tag filtering and search
- Popular tags suggestions
- Tag input with auto-complete

### Audio Player Integration
Beat-related templates include:
- Howler.js integration for audio playback
- Play state management with Alpine.js
- Waveform visualization with Web Audio API
- Queue management and controls

### Styling
Templates use a consistent styling approach:
- Tailwind CSS for responsive design
- Custom components using @apply directives
- Dark theme with accent colors
- Consistent spacing and typography

### JavaScript Integration
Templates integrate with:
- Alpine.js for reactivity
- HTMX for dynamic content
- Font Awesome icons
- Custom event handling

## Usage Guidelines

### Extending Base Template
```html
{% extends 'store/base.html' %}
{% load static %}

{% block content %}
    <!-- Your template content here -->
{% endblock %}

{% block extra_js %}
    <!-- Additional JavaScript if needed -->
{% endblock %}
```

### Using Components
```html
{% include 'store/components/audio_player.html' %}
{% include 'store/components/comments.html' with beat=beat %}
```

### Tag Implementation
```html
<!-- Display tags -->
{% if object.tags.all %}
<div class="flex flex-wrap gap-2">
    {% for tag in object.tags.all|slice:":3" %}
    <a href="?tag={{ tag.name }}" 
       class="tag-pill {% if tag.name in selected_tags %}active{% endif %}">
        {{ tag.name }}
    </a>
    {% endfor %}
</div>
{% endif %}

<!-- Tag input -->
<div x-data="tagInput()" class="tag-input">
    <!-- Tag input implementation -->
</div>
```

### Audio Player Implementation
```html
<div x-data="{ 
    isPlaying: false,
    track: {
        id: {{ beat.id }},
        title: '{{ beat.title|escapejs }}',
        audioUrl: '{{ beat.audio_file.url|escapejs }}'
    }
}">
    <!-- Audio player implementation -->
</div>
```

## Best Practices

1. **Template Organization**
   - Keep templates modular and focused
   - Use includes for repeated components
   - Maintain consistent naming conventions

2. **Performance**
   - Minimize template inheritance depth
   - Use template fragment caching where appropriate
   - Optimize media queries and responsive design

3. **Accessibility**
   - Include proper ARIA attributes
   - Maintain semantic HTML structure
   - Ensure keyboard navigation support

4. **Security**
   - Always escape user input
   - Use CSRF protection
   - Implement proper permission checks

5. **Maintenance**
   - Document template blocks and variables
   - Keep styling consistent
   - Update dependencies regularly 