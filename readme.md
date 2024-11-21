
# Ivan Fazlic Flask API

This project uses Flask for the backend and SQLAlchemy for database management. Follow the instructions below to set up your environment and start the application.

## Requirements

Make sure you have Python 3.7+ installed. You will also need `pip` to install dependencies.

## Setting up the environment

1. **Create a virtual environment**: Open your terminal and navigate to the project directory. Run the following command to create a `.venv` environment:

   ```bash
   python -m venv .venv
   ```

2. **Activate the virtual environment**:
   - On **Windows**:
     ```bash
     .venv\Scripts\activate
     ```
   - On **macOS/Linux**:
     ```bash
     source .venv/bin/activate
     ```

3. **Install the required dependencies**: After activating the virtual environment, install the required packages using:

   ```bash
   pip install -r requirements.txt
   ```

## Database Setup

1. **Initialize the database**: To initialize the database, run the following commands:

   ```bash
   flask db init
   ```

2. **Create a migration**: Generate a migration script by running:

   ```bash
   flask db migrate -m "Your migration message"
   ```

3. **Apply the migration**: Apply the migration to the database:

   ```bash
   flask db upgrade
   ```

## Starting the Server

After setting up the environment and database, you can start the Flask server with:

```bash
python run.py
```

The server should now be running locally.
