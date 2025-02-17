# WavHaven API Documentation

## Authentication

### POST /api/auth/login/
Login with username and password.

**Request:**
```json
{
    "username": "string",
    "password": "string"
}
```

**Response:**
```json
{
    "token": "string",
    "user": {
        "id": "integer",
        "username": "string",
        "email": "string"
    }
}
```

### POST /api/auth/register/
Register a new user account.

**Request:**
```json
{
    "username": "string",
    "email": "string",
    "password": "string",
    "password_confirm": "string"
}
```

## Beats

### GET /api/beats/
List all beats with optional filtering.

**Query Parameters:**
- `genre`: Filter by genre name
- `producer`: Filter by producer username
- `q`: Search query
- `sort`: Sort by (price, date, popularity)
- `page`: Page number
- `page_size`: Results per page

### POST /api/beats/
Upload a new beat (requires authentication).

**Request:**
```json
{
    "title": "string",
    "price": "decimal",
    "audio_file": "file",
    "cover_image": "file (optional)",
    "genre": "integer",
    "bpm": "integer (optional)",
    "key": "string (optional)",
    "tags": "string (optional)"
}
```

### GET /api/beats/{id}/
Get detailed information about a specific beat.

### PATCH /api/beats/{id}/
Update a beat (requires authentication and ownership).

### DELETE /api/beats/{id}/
Delete a beat (requires authentication and ownership).

## User Profiles

### GET /api/profiles/{username}/
Get user profile information.

### PATCH /api/profiles/{username}/
Update user profile (requires authentication and ownership).

**Request:**
```json
{
    "display_name": "string (optional)",
    "bio": "string (optional)",
    "avatar": "file (optional)",
    "website": "string (optional)",
    "social_links": {
        "soundcloud": "string (optional)",
        "youtube": "string (optional)",
        "instagram": "string (optional)"
    }
}
```

## Favorites

### POST /api/favorites/{beat_id}/
Add a beat to favorites (requires authentication).

### DELETE /api/favorites/{beat_id}/
Remove a beat from favorites (requires authentication).

### GET /api/favorites/check/{beat_id}/
Check if a beat is in user's favorites (requires authentication).

## Cart

### POST /api/cart/add/
Add a beat to cart (requires authentication).

**Request:**
```json
{
    "beat_id": "integer",
    "license_type": "string"
}
```

### GET /api/cart/check/{beat_id}/
Check if a beat is in user's cart (requires authentication).

### GET /api/cart/
Get cart contents (requires authentication).

### DELETE /api/cart/{item_id}/
Remove item from cart (requires authentication).

## Comments

### POST /api/beats/{beat_id}/comments/
Add a comment to a beat (requires authentication).

**Request:**
```json
{
    "content": "string",
    "parent_id": "integer (optional, for replies)"
}
```

### DELETE /api/comments/{comment_id}/
Delete a comment (requires authentication and ownership).

### POST /api/comments/{comment_id}/upvote/
Upvote a comment (requires authentication).

## Follow System

### POST /api/profiles/{username}/follow/
Follow a user (requires authentication).

### POST /api/profiles/{username}/unfollow/
Unfollow a user (requires authentication).

## Error Responses

All endpoints may return these error responses:

### 400 Bad Request
```json
{
    "error": "string",
    "details": "object (optional)"
}
```

### 401 Unauthorized
```json
{
    "error": "Authentication credentials were not provided"
}
```

### 403 Forbidden
```json
{
    "error": "You do not have permission to perform this action"
}
```

### 404 Not Found
```json
{
    "error": "Requested resource was not found"
}
```

## Authentication

All API endpoints except login and registration require JWT authentication.
Include the JWT token in the Authorization header:

```
Authorization: Bearer <your_token>
```

## Rate Limiting

API requests are rate limited to:
- 100 requests per minute for authenticated users
- 20 requests per minute for anonymous users

## Pagination

List endpoints return paginated results:

```json
{
    "count": "integer",
    "next": "string (url)",
    "previous": "string (url)",
    "results": []
}
``` 