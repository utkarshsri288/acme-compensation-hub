setup:
	python3 -m venv .venv && . .venv/bin/activate && pip install -r backend/requirements.txt

backend:
	cd backend && python manage.py runserver 8000

frontend:
	cd frontend && npm run dev

test:
	cd backend && python manage.py test
