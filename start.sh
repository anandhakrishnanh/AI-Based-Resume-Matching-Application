#!/bin/bash
# Start the ollama server in the background
ollama serve &
# Start the Streamlit app
streamlit run app.py