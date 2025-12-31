# TinyRisks.art

A minimalist art portfolio website built with Flask and semantic HTML.

## Features

- Simple, clean design with semantic HTML and CSS
- Community gallery for showcasing artwork
- Admin panel for content management
- Image upload with metadata support
- Responsive design

## Setup

### Prerequisites

- Python 3.7 or higher
- pip

### Installation

1. Clone the repository:
```bash
git clone https://github.com/anditherobot/tinyrisks.art.git
cd tinyrisks.art
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Initialize the database:
```bash
python3 init_db.py
```

Or run the app directly (it will initialize on first run):
```bash
python app.py
```

The database will be automatically initialized with a default admin user.

### Admin Credentials

Default admin credentials (change after first login):
- **Username:** admin
- **Password:** adminpass123

## Running the Application

```bash
python app.py
```

The server will start at `http://localhost:5000`

## Admin Panel

Access the admin panel at `/admin` to:
- Upload images to the community gallery
- Manage gallery items with full CRUD operations
- Add titles, captions, and descriptions
- Upload multiple images per gallery item (min 1, max 9)

## Environment Variables

- `SECRET_KEY`: Flask secret key for sessions (auto-generated in development)

## Testing

Run tests with pytest:
```bash
pytest
```

## Project Structure

```
tinyrisks.art/
├── app.py              # Flask application
├── models.py           # Database models
├── htdocs/             # Static HTML files
│   ├── index.html
│   ├── gallery.html
│   ├── admin.html
│   ├── 404.html
│   └── 500.html
├── tests/              # Test files
└── requirements.txt    # Python dependencies
```

## License

© TinyRisks.art
