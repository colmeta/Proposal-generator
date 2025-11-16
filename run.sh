#!/bin/bash

echo "Starting Professional Funding Proposal Generator..."
echo ""
echo "Choose your interface:"
echo "1. Web Interface (Streamlit) - Recommended"
echo "2. Command Line Interface"
echo ""
read -p "Enter choice (1 or 2): " choice

if [ "$choice" == "1" ]; then
    echo "Starting web interface..."
    streamlit run app.py
elif [ "$choice" == "2" ]; then
    echo "Starting command line interface..."
    python main.py
else
    echo "Invalid choice. Starting web interface by default..."
    streamlit run app.py
fi

