# TinyRisks.art

A minimalist art portfolio website built with Flask and semantic HTML.

## Features

- Simple, clean design with semantic HTML and CSS
- Community gallery for showcasing artwork
- Admin panel for content management
- Image upload with metadata support
- Responsive design

## Local Development

### Prerequisites

- Python 3.8 or higher
- pip

### Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/anditherobot/tinyrisks.art.git
   cd tinyrisks.art
   ```

2. **Create and activate a virtual environment:**
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the database:**
   ```bash
   python init_db.py
   ```
   *Note: This creates the SQLite database and a default admin user.*

### Running the App

Start the development server:
```bash
python app.py
```

- **Website:** [http://localhost:5000](http://localhost:5000)
- **Admin Panel:** [http://localhost:5000/login](http://localhost:5000/login)

### Admin Credentials

Default credentials (please change after first login):
- **Username:** `admin`
- **Password:** `adminpass123`

## Testing

Run the test suite to ensure everything is working correctly:
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
