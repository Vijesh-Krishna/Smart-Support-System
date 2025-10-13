# Smart Support System (RAG customer support)

## Quick start (local)

# backend

cd backend
python -m venv venv

# windows: venv\Scripts\activate  linux/mac: source venv/bin/activate

pip install -r requirements.txt
export ALLOWED_ORIGINS=http://localhost:5173
uvicorn app.main:app --reload --port 8000

# frontend
cd ../frontend
npm install
echo "VITE_API_BASE_URL=http://127.0.0.1:8000" > .env.local
npm run dev
