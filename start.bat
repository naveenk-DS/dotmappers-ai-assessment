@echo off

echo Starting DOTMappers AI Support Ticket System...
echo.

start "FastAPI" cmd /k "python -m uvicorn app.main:app --host 127.0.0.1 --port 8000"

timeout /t 3 /nobreak >nul

start "Streamlit" cmd /k "python -m streamlit run ui/streamlit_app.py"

echo.
echo FastAPI: http://127.0.0.1:8000
echo API Docs: http://127.0.0.1:8000/docs
echo Streamlit will open automatically.
echo.
pause