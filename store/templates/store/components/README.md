# Components Documentation

## Overview
This directory contains reusable template components that can be included in other templates. Each component is designed to be self-contained and follows consistent styling and behavior patterns.

## Available Components

### Audio Player
- **File**: `audio_player.html`
- **Purpose**: Provides audio playback functionality with waveform visualization
- **Dependencies**: 
  - Howler.js for audio playback
  - Web Audio API for visualization
  - Alpine.js for state management
- **Usage**:
```html
{% include 'store/components/audio_player.html' with 
    track_id=beat.id 
    audio_url=beat.audio_file.url 
    title=beat.title 
%}
```

### Comments Section
- **File**: `comments.html`
- **Purpose**: Displays and manages comments and replies
- **Features**:
  - Nested comments support
  - Upvoting system
  - Reply functionality
  - Real-time updates
- **Usage**:
```html
{% include 'store/components/comments.html' with 
    comments=beat.comments.all 
    object_id=beat.id 
%}
```

### Tag Display
- **File**: `tag_display.html`
- **Purpose**: Consistent tag rendering and interaction
- **Features**:
  - Tag count indicators
  - Filtering links
  - Truncation for long lists
- **Usage**:
```html
{% include 'store/components/tag_display.html' with 
    tags=object.tags.all 
    selected_tags=selected_tags 
%}
```

### Loading States
- **File**: `loading.html`
- **Purpose**: Consistent loading indicators
- **Variants**:
  - Spinner
  - Skeleton loader
  - Progress bar
- **Usage**:
```html
{% include 'store/components/loading.html' with 
    type='spinner'
    size='medium' 
%}
```

### Alert Messages
- **File**: `alerts.html`
- **Purpose**: Standardized alert and notification display
- **Types**:
  - Success
  - Error
  - Warning
  - Info
- **Usage**:
```html
{% include 'store/components/alerts.html' with 
    messages=messages 
%}
```

### Pagination
- **File**: `pagination.html`
- **Purpose**: Consistent pagination controls
- **Features**:
  - Page numbers
  - Previous/Next buttons
  - Current page indicator
- **Usage**:
```html
{% include 'store/components/pagination.html' with 
    page_obj=page_obj 
    is_paginated=is_paginated 
%}
```

## Component Guidelines

### State Management
Components use Alpine.js for state management:
```html
<div x-data="componentState()">
    <!-- Component content -->
</div>
```

### Event Handling
Components emit and listen for events:
```javascript
// Emit event
$dispatch('event-name', { data: value })

// Listen for event
@event-name.window="handleEvent"
```

### Styling
Components follow Tailwind CSS conventions:
```html
<div class="component-base">
    <div class="component-header">
        <!-- Header content -->
    </div>
    <div class="component-body">
        <!-- Main content -->
    </div>
</div>
```

### Accessibility
Components include necessary accessibility attributes:
```html
<button 
    aria-label="Play audio"
    role="button"
    tabindex="0"
>
    <!-- Button content -->
</button>
```

## Best Practices

1. **Modularity**
   - Keep components focused on a single responsibility
   - Avoid tight coupling with specific templates
   - Use props for configuration

2. **Reusability**
   - Design components to be context-agnostic
   - Document required context and variables
   - Provide sensible defaults

3. **Performance**
   - Minimize DOM operations
   - Use template fragment caching
   - Lazy load when appropriate

4. **Maintenance**
   - Keep styling consistent
   - Document component interfaces
   - Version control changes

5. **Testing**
   - Test components in isolation
   - Verify accessibility
   - Check responsive behavior 