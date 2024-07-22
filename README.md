# LLM-Based SQL Interaction Program

This repository contains an LLM (Language Learning Model) based SQL interaction program. The program allows users to interact with an SQLite database using natural language queries. It leverages Python, LangChain, and LangGraph to provide an intuitive interface for querying data.

## Getting Started

Follow these steps to set up and run the program:

1. **Install Dependencies:**
   - Make sure you have Python installed (version 3.6 or higher).
   - Open a terminal or command prompt and navigate to the project directory.
   - Run the following command to install the required dependencies:
     ```
     pip install -r requirements.txt
     ```

2. **Configure Database Path:**
   - Open `src/main.py` in a text editor.
   - Locate the `db_path` variable and update it with the path to your SQLite database file (e.g., `./database/chinook.db`).

3. **Run the Program:**
   - In the terminal, execute the following command to start the program:
     ```
     streamlit run ./src/main.py
     ```
   - This will launch a Streamlit web app where you can input natural language queries to interact with the database.

## Usage

1. Open the web app in your browser (usually at `http://localhost:8501`).
2. Enter your SQL question in the provided input field.
3. Click the "Submit" button to execute the query.
4. View the results displayed on the page.

## Notes

- The LLM model parses your natural language query and translates it into SQL.
- Make sure your database schema aligns with the expected queries for accurate results.

Remember to replace the placeholders with actual details relevant to your project. Let me know if you need any further assistance! 😊
