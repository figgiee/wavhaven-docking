# WAVHaven API Documentation

## Overview

The WAVHaven API provides endpoints for managing beats, user profiles, and transactions. This documentation covers all available endpoints, authentication methods, and common patterns.

## Authentication

All authenticated endpoints require a JWT token in the Authorization header:

```
Authorization: Bearer <token>
```

To obtain a token, use the login endpoint:

```http
POST /api/auth/token/
Content-Type: application/json

{
    "username": "your_username",
    "password": "your_password"
}
```

Response:
```json
{
    "access": "your.jwt.token",
    "refresh": "your.refresh.token"
}
```

## Rate Limiting

- Authenticated endpoints: 100 requests per minute
- Unauthenticated endpoints: 20 requests per minute
- File upload endpoints: 10 requests per minute

## Endpoints

### Beats

#### List Beats
```http
GET /api/beats/
```

Query Parameters:
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20, max: 100)
- `search`: Search term
- `genre`: Filter by genre
- `price_min`: Minimum price
- `price_max`: Maximum price
- `sort`: Sort field (created_at, price, popularity)
- `order`: Sort order (asc, desc)

Response:
```json
{
    "count": 100,
    "next": "http://api.wavhaven.com/api/beats/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "title": "Summer Vibes",
            "producer": {
                "id": 1,
                "username": "producer1",
                "avatar_url": "..."
            },
            "cover_image": "...",
            "preview_url": "...",
            "price": 29.99,
            "genre": "Hip Hop",
            "bpm": 140,
            "key": "C minor",
            "tags": ["melodic", "summer", "upbeat"],
            "created_at": "2024-02-24T12:00:00Z",
            "waveform_url": "...",
            "duration": 180
        }
    ]
}
```

#### Get Beat Details
```http
GET /api/beats/{id}/
```

Response: Same as single beat object from list endpoint

#### Create Beat
```http
POST /api/beats/
Content-Type: multipart/form-data

{
    "title": "New Beat",
    "audio_file": <file>,
    "cover_image": <file>,
    "price": 29.99,
    "genre": "Hip Hop",
    "bpm": 140,
    "key": "C minor",
    "tags": ["melodic", "summer"],
    "description": "A summer vibe beat"
}
```

#### Update Beat
```http
PATCH /api/beats/{id}/
Content-Type: application/json

{
    "title": "Updated Title",
    "price": 39.99
}
```

#### Delete Beat
```http
DELETE /api/beats/{id}/
```

### Users

#### Get Profile
```http
GET /api/users/profile/
```

Response:
```json
{
    "id": 1,
    "username": "producer1",
    "email": "producer1@example.com",
    "avatar_url": "...",
    "bio": "...",
    "website": "...",
    "social_links": {
        "twitter": "...",
        "instagram": "...",
        "soundcloud": "..."
    },
    "beats_count": 50,
    "followers_count": 1000,
    "following_count": 500
}
```

#### Update Profile
```http
PATCH /api/users/profile/
Content-Type: multipart/form-data

{
    "avatar": <file>,
    "bio": "New bio",
    "website": "https://example.com",
    "social_links": {
        "twitter": "https://twitter.com/producer1"
    }
}
```

### Transactions

#### Purchase Beat
```http
POST /api/transactions/purchase/
Content-Type: application/json

{
    "beat_id": 1,
    "payment_method_id": "pm_..."
}
```

Response:
```json
{
    "id": "tr_...",
    "status": "completed",
    "amount": 29.99,
    "beat": {
        "id": 1,
        "title": "Summer Vibes",
        "download_url": "..."
    },
    "created_at": "2024-02-24T12:00:00Z"
}
```

### Playlists

#### List Playlists
```http
GET /api/playlists/
```

#### Create Playlist
```http
POST /api/playlists/
Content-Type: application/json

{
    "name": "My Favorites",
    "description": "My favorite beats",
    "is_public": true
}
```

#### Add Beat to Playlist
```http
POST /api/playlists/{id}/beats/
Content-Type: application/json

{
    "beat_id": 1
}
```

## Error Responses

All error responses follow this format:
```json
{
    "status_code": 400,
    "message": "Error message",
    "errors": {
        "field": ["Error details"]
    }
}
```

Common status codes:
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 429: Too Many Requests

## Pagination

All list endpoints support pagination with these response fields:
- `count`: Total number of items
- `next`: URL for next page (null if no more pages)
- `previous`: URL for previous page (null if first page)
- `results`: Array of items for current page

## Filtering and Sorting

Most list endpoints support:
- Field filtering: `?field=value`
- Search: `?search=term`
- Sorting: `?sort=field&order=asc|desc`

## File Upload Guidelines

- Audio files: MP3, WAV (max 50MB)
- Images: JPG, PNG (max 5MB)
- File naming: lowercase, no spaces
- Audio quality: minimum 192kbps for MP3

## Webhook Events

Subscribe to webhooks for real-time updates:
```http
POST /api/webhooks/
Content-Type: application/json

{
    "url": "https://your-domain.com/webhook",
    "events": ["beat.purchased", "user.followed"]
}
```

Available events:
- beat.created
- beat.updated
- beat.purchased
- user.followed
- playlist.updated 