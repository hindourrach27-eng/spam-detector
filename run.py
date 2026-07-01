"""
run.py — Point d'entrée de l'application
"""

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5000)