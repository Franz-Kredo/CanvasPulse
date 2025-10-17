# main.py
"""
Main entrypoint for the Canvas Assignment Fetcher.
"""
from app import Application

def main():
    """Initializes and runs the application."""
    try:
        app = Application()
        app.run()
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()