# Data Analytics Processing App

A Django-based application for processing and managing data analytics workflows.

## Tech Stack

* Python 3.11
* Django 5.2
* Django REST Framework
* SQLite (Development)

## Project Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd Data-Analytics-Processing-App
```

### 2. Create a virtual environment

```bash
python3.11 -m venv .venv
```

### 3. Activate the virtual environment

**macOS / Linux:**

```bash
source .venv/bin/activate
```

**Windows:**

```bash
.venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure environment variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
```

### 6. Run migrations

```bash
python manage.py migrate
```

### 7. Start the development server

```bash
python manage.py runserver
```

The application will be available at:

```text
http://127.0.0.1:8000/
```

## Project Structure

```text
Data-Analytics-Processing-App/
├── config/
├── processor/
├── manage.py
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

## Environment Variables

| Variable        | Description                             |
| --------------- | --------------------------------------- |
| `SECRET_KEY`    | Django secret key                       |
| `DEBUG`         | Enables/disables Django debug mode      |
| `ALLOWED_HOSTS` | Hosts allowed to access the application |

> Do not commit the `.env` file to the repository. Use `.env.example` for sharing required environment variables with the team.

## Development

Activate the virtual environment before running Django commands:

```bash
source .venv/bin/activate
```

Run the development server:

```bash
python manage.py runserver
```

## License

This project is intended for internal development and use.
