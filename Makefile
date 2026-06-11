.PHONY: setup backend frontend clean

setup:
	cd backend && pip install -r requirements.txt
	cd frontend && npm install

backend:
	cd backend && uvicorn app.main:app --reload --port 8000

frontend:
	cd frontend && npm run dev

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name node_modules -exec rm -rf {} +
	rm -rf frontend/.next
