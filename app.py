from flask import Flask, render_template, request, jsonify, session
import sqlite3
import os
from groq import Groq
from dotenv import load_dotenv
import re
import secrets

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # For session management

# Initialize Groq client
groq_client = Groq(api_key=os.getenv('GROQ_API_KEY'))

# Database file path (for optional testing)
DB_PATH = 'user_database.db'

def parse_schema_input(schema_text):
    """
    Parses user-provided schema text into a structured format.
    
    Expected format:
    Table: users
    - id: INTEGER
    - username: TEXT
    - email: TEXT
    
    Table: posts
    - id: INTEGER
    - user_id: INTEGER
    - content: TEXT
    
    Returns a dictionary with table information
    """
    schema = {}
    current_table = None
    
    lines = schema_text.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if it's a table definition
        if line.lower().startswith('table:'):
            table_name = line.split(':', 1)[1].strip()
            current_table = table_name
            schema[current_table] = []
        
        # Check if it's a column definition
        elif line.startswith('-') and current_table:
            # Remove the dash and parse column
            col_def = line[1:].strip()
            if ':' in col_def:
                col_name, col_type = col_def.split(':', 1)
                schema[current_table].append({
                    'name': col_name.strip(),
                    'type': col_type.strip()
                })
    
    return schema

def format_schema_for_prompt(schema):
    """
    Formats the parsed schema into a string for the LLM prompt.
    """
    if not schema:
        return "No schema provided."
    
    formatted = "DATABASE SCHEMA:\n\n"
    
    for table_name, columns in schema.items():
        formatted += f"Table: {table_name}\n"
        for col in columns:
            formatted += f"- {col['name']}: {col['type']}\n"
        formatted += "\n"
    
    return formatted

def create_database_from_schema(schema):
    """
    Optional: Creates a SQLite database from the user's schema
    so they can test queries against it.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Drop existing tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        for table in tables:
            cursor.execute(f"DROP TABLE IF EXISTS {table[0]}")
        
        # Create new tables from schema
        for table_name, columns in schema.items():
            col_defs = []
            for col in columns:
                col_defs.append(f"{col['name']} {col['type']}")
            
            create_stmt = f"CREATE TABLE {table_name} ({', '.join(col_defs)})"
            cursor.execute(create_stmt)
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error creating database: {e}")
        return False

def generate_sql_query(natural_language_query, schema_text):
    """
    Uses Groq API to convert natural language into SQL.
    
    Args:
        natural_language_query: User's request in plain English
        schema_text: Formatted schema string
        
    Returns:
        dict with 'success', 'sql', and optional 'error' keys
    """
    try:
        # Build the prompt with custom schema and examples
        prompt = f"""{schema_text}

TASK: Convert the following natural language query into a valid SQLite SQL query.

RULES:
1. Return ONLY the SQL query, no explanations or markdown
2. Use SQLite syntax (e.g., DATE('now') for current date)
3. Use JOINs when querying multiple tables
4. Use appropriate WHERE clauses for filtering
5. Include ORDER BY and LIMIT when relevant
6. Use the exact table and column names from the schema above

EXAMPLES:

User: "Show me all records from the first table"
SQL: SELECT * FROM [first_table_name];

User: "Find records with a specific value"
SQL: SELECT * FROM [table_name] WHERE [column_name] = 'value';

User: "Get the top 5 records ordered by a column"
SQL: SELECT * FROM [table_name] ORDER BY [column_name] DESC LIMIT 5;

User: "Join two tables"
SQL: SELECT t1.*, t2.* FROM [table1] t1 JOIN [table2] t2 ON t1.id = t2.foreign_key;

User: "Count records in a table"
SQL: SELECT COUNT(*) FROM [table_name];

NOW CONVERT THIS QUERY:

User: "{natural_language_query}"
SQL:"""

        # Call Groq API
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a SQL expert. Generate only valid SQLite queries without any explanations. Use the exact table and column names provided in the schema."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.1,
            max_tokens=500
        )
        
        # Extract SQL from response
        sql_query = chat_completion.choices[0].message.content.strip()
        
        # Clean up common formatting issues
        sql_query = sql_query.replace('```sql', '').replace('```', '').strip()
        
        # Remove any trailing semicolon issues
        sql_query = sql_query.rstrip(';') + ';'
        
        return {
            'success': True,
            'sql': sql_query
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def validate_query(sql_query):
    """
    Validates SQL query by checking syntax (optional execution).
    """
    try:
        # Check if database exists
        if not os.path.exists(DB_PATH):
            return {
                'valid': True,
                'message': 'Query syntax looks valid (no test database available)'
            }
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Execute query
        cursor.execute(sql_query)
        
        # Fetch results (if SELECT query)
        if sql_query.strip().upper().startswith('SELECT'):
            results = cursor.fetchall()
            column_names = [description[0] for description in cursor.description] if cursor.description else []
            
            conn.close()
            
            return {
                'valid': True,
                'columns': column_names,
                'results': results,
                'row_count': len(results)
            }
        else:
            conn.commit()
            conn.close()
            return {
                'valid': True,
                'message': 'Query executed successfully'
            }
            
    except sqlite3.Error as e:
        return {
            'valid': False,
            'error': str(e)
        }

@app.route('/')
def home():
    """Serves the main HTML page"""
    return render_template('index.html')

@app.route('/save-schema', methods=['POST'])
def save_schema():
    """
    Saves the user's custom schema to the session.
    """
    try:
        data = request.get_json()
        schema_text = data.get('schema', '').strip()
        
        if not schema_text:
            return jsonify({
                'success': False,
                'error': 'Please provide a database schema'
            }), 400
        
        # Parse the schema
        parsed_schema = parse_schema_input(schema_text)
        
        if not parsed_schema:
            return jsonify({
                'success': False,
                'error': 'Could not parse schema. Please check the format.'
            }), 400
        
        # Store in session
        session['schema_text'] = schema_text
        session['parsed_schema'] = parsed_schema
        
        # Optional: Create SQLite database for testing
        db_created = create_database_from_schema(parsed_schema)
        
        return jsonify({
            'success': True,
            'message': 'Schema saved successfully!',
            'tables': list(parsed_schema.keys()),
            'database_created': db_created
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/generate', methods=['POST'])
def generate():
    """
    API endpoint that receives natural language and returns SQL.
    """
    try:
        data = request.get_json()
        user_query = data.get('query', '').strip()
        
        if not user_query:
            return jsonify({
                'success': False,
                'error': 'Please provide a query'
            }), 400
        
        # Check if schema exists in session
        if 'schema_text' not in session:
            return jsonify({
                'success': False,
                'error': 'Please provide a database schema first'
            }), 400
        
        schema_text = format_schema_for_prompt(session.get('parsed_schema', {}))
        
        # Generate SQL using LLM
        result = generate_sql_query(user_query, schema_text)
        
        if not result['success']:
            return jsonify(result), 500
        
        # Validate the generated SQL (optional)
        validation = validate_query(result['sql'])
        
        return jsonify({
            'success': True,
            'natural_query': user_query,
            'sql_query': result['sql'],
            'validation': validation
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/clear-schema', methods=['POST'])
def clear_schema():
    """
    Clears the stored schema from session.
    """
    session.pop('schema_text', None)
    session.pop('parsed_schema', None)
    
    # Remove test database
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    
    return jsonify({
        'success': True,
        'message': 'Schema cleared'
    })

if __name__ == '__main__':
    print("\n🚀 SQL Query Generator is running!")
    print("📍 Open http://localhost:5000 in your browser\n")
    app.run(debug=True, port=5000)