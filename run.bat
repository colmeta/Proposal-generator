@echo off
echo Starting Professional Funding Proposal Generator...
echo.
echo Choose your interface:
echo 1. Web Interface (Streamlit) - Recommended
echo 2. Command Line Interface
echo.
set /p choice="Enter choice (1 or 2): "

if "%choice%"=="1" (
    echo Starting web interface...
    streamlit run app.py
) else if "%choice%"=="2" (
    echo Starting command line interface...
    python main.py
) else (
    echo Invalid choice. Starting web interface by default...
    streamlit run app.py
)

pause

