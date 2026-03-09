from flask import Flask, render_template, request, jsonify, session
import sqlite3
import os
from groq import Groq
from dotenv import load_dotenv
import secrets

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(16))

# Initialize Groq client
groq_client = Groq(api_key=os.getenv('GROQ_API_KEY'))

# Database file path (for SQLite testing)
DB_PATH = 'user_database.db'

# Database-specific syntax rules
DATABASE_SYNTAX = {
    'sqlite': {
        'name': 'SQLite',
        'current_timestamp': "DATETIME('now')",
        'current_date': "DATE('now')",
        'date_add': "DATE('now', '+N days')",
        'date_sub': "DATE('now', '-N days')",
        'limit': 'LIMIT N',
        'string_concat': '||',
        'auto_increment': 'AUTOINCREMENT',
        'if_null': 'IFNULL(column, value)',
        'case_sensitive': 'COLLATE NOCASE',
        'examples': {
            'date_range': "WHERE date_column >= DATE('now', '-7 days')",
            'pagination': "LIMIT 10 OFFSET 20",
            'concat': "first_name || ' ' || last_name AS full_name"
        }
    },
    'mysql': {
        'name': 'MySQL',
        'current_timestamp': 'NOW()',
        'current_date': 'CURDATE()',
        'date_add': 'DATE_ADD(NOW(), INTERVAL N DAY)',
        'date_sub': 'DATE_SUB(NOW(), INTERVAL N DAY)',
        'limit': 'LIMIT N',
        'string_concat': 'CONCAT()',
        'auto_increment': 'AUTO_INCREMENT',
        'if_null': 'IFNULL(column, value)',
        'case_sensitive': 'COLLATE utf8mb4_general_ci',
        'examples': {
            'date_range': "WHERE date_column >= DATE_SUB(NOW(), INTERVAL 7 DAY)",
            'pagination': "LIMIT 20, 10",
            'concat': "CONCAT(first_name, ' ', last_name) AS full_name",
            'top_n': "SELECT * FROM table ORDER BY column LIMIT 10"
        }
    },
    'oracle': {
        'name': 'Oracle',
        'current_timestamp': 'SYSDATE',
        'current_date': 'TRUNC(SYSDATE)',
        'date_add': 'SYSDATE + N',
        'date_sub': 'SYSDATE - N',
        'limit': 'FETCH FIRST N ROWS ONLY',
        'string_concat': '||',
        'auto_increment': 'Generated as Identity',
        'if_null': 'NVL(column, value)',
        'case_sensitive': 'UPPER() or LOWER()',
        'examples': {
            'date_range': "WHERE date_column >= SYSDATE - 7",
            'pagination': "OFFSET 20 ROWS FETCH NEXT 10 ROWS ONLY",
            'concat': "first_name || ' ' || last_name AS full_name",
            'top_n': "SELECT * FROM table ORDER BY column FETCH FIRST 10 ROWS ONLY",
            'sequence': "column_id NUMBER GENERATED ALWAYS AS IDENTITY"
        }
    },
    'postgresql': {
        'name': 'PostgreSQL',
        'current_timestamp': 'NOW()',
        'current_date': 'CURRENT_DATE',
        'date_add': "NOW() + INTERVAL 'N days'",
        'date_sub': "NOW() - INTERVAL 'N days'",
        'limit': 'LIMIT N',
        'string_concat': '||',
        'auto_increment': 'SERIAL',
        'if_null': 'COALESCE(column, value)',
        'case_sensitive': 'ILIKE for case-insensitive',
        'examples': {
            'date_range': "WHERE date_column >= NOW() - INTERVAL '7 days'",
            'pagination': "LIMIT 10 OFFSET 20",
            'concat': "first_name || ' ' || last_name AS full_name",
            'top_n': "SELECT * FROM table ORDER BY column LIMIT 10"
        }
    }
}

def parse_schema_input(schema_text):
    """
    Parses user-provided schema text into a structured format.
    """
    schema = {}
    current_table = None
    
    lines = schema_text.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if line.lower().startswith('table:'):
            table_name = line.split(':', 1)[1].strip()
            current_table = table_name
            schema[current_table] = []
        
        elif line.startswith('-') and current_table:
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

def get_database_specific_rules(db_type):
    """
    Returns database-specific SQL syntax rules.
    """
    syntax = DATABASE_SYNTAX.get(db_type, DATABASE_SYNTAX['sqlite'])
    
    rules = f"""
DATABASE TYPE: {syntax['name']}

SYNTAX RULES FOR {syntax['name'].upper()}:
1. Current Timestamp: {syntax['current_timestamp']}
2. Current Date: {syntax['current_date']}
3. Date Addition: {syntax['date_add']}
4. Date Subtraction: {syntax['date_sub']}
5. Limit Clause: {syntax['limit']}
6. String Concatenation: {syntax['string_concat']}
7. Auto Increment: {syntax['auto_increment']}
8. NULL Handling: {syntax['if_null']}

EXAMPLES FOR {syntax['name'].upper()}:
"""
    
    for example_name, example_sql in syntax['examples'].items():
        rules += f"- {example_name.replace('_', ' ').title()}: {example_sql}\n"
    
    return rules

def create_database_from_schema(schema):
    """
    Creates a SQLite database from the user's schema for testing.
    (Only works for SQLite)
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        for table in tables:
            cursor.execute(f"DROP TABLE IF EXISTS {table[0]}")
        
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

def generate_sql_query(natural_language_query, schema_text, db_type='sqlite'):
    """
    Uses Groq API to convert natural language into SQL for specific database.
    """
    try:
        # Get database-specific rules
        db_rules = get_database_specific_rules(db_type)
        
        # Build the prompt
        prompt = f"""{schema_text}

{db_rules}

TASK: Convert the following natural language query into a valid {DATABASE_SYNTAX[db_type]['name']} SQL query.

CRITICAL RULES:
1. Return ONLY the SQL query, no explanations or markdown
2. Use {DATABASE_SYNTAX[db_type]['name']} syntax EXCLUSIVELY
3. Use exact table and column names from the schema
4. Follow the syntax examples provided above
5. For date operations, use {DATABASE_SYNTAX[db_type]['name']}-specific functions
6. Use appropriate JOIN syntax when querying multiple tables
7. Include ORDER BY and LIMIT/FETCH when relevant

GENERAL EXAMPLES (adapt to {DATABASE_SYNTAX[db_type]['name']} syntax):

User: "Show all records from the first table"
SQL: SELECT * FROM [table_name];

User: "Find records from last 7 days"
SQL: Use {db_type}-specific date subtraction shown above

User: "Get top 5 records"
SQL: Use {db_type}-specific LIMIT/FETCH syntax shown above

User: "Join two tables"
SQL: SELECT t1.*, t2.* FROM table1 t1 JOIN table2 t2 ON t1.id = t2.foreign_key;

NOW CONVERT THIS QUERY TO {DATABASE_SYNTAX[db_type]['name'].upper()}:

User: "{natural_language_query}"
SQL:"""

        # Call Groq API
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": f"You are a {DATABASE_SYNTAX[db_type]['name']} expert. Generate only valid {DATABASE_SYNTAX[db_type]['name']} queries using the exact syntax for this database. Never use syntax from other databases."
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
        
        sql_query = chat_completion.choices[0].message.content.strip()
        
        # Clean up formatting
        sql_query = sql_query.replace('```sql', '').replace('```', '').strip()
        sql_query = sql_query.rstrip(';') + ';'
        
        return {
            'success': True,
            'sql': sql_query,
            'database_type': DATABASE_SYNTAX[db_type]['name']
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def validate_query(sql_query, db_type='sqlite'):
    """
    Validates SQL query (only executes for SQLite).
    """
    if db_type != 'sqlite':
        return {
            'valid': True,
            'message': f'Query generated for {DATABASE_SYNTAX[db_type]["name"]}. Test it in your {DATABASE_SYNTAX[db_type]["name"]} environment.'
        }
    
    try:
        if not os.path.exists(DB_PATH):
            return {
                'valid': True,
                'message': 'Query syntax looks valid (no test database available)'
            }
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute(sql_query)
        
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
    return render_template('index.html')

@app.route('/save-schema', methods=['POST'])
def save_schema():
    """
    Saves the user's custom schema and database type to session.
    """
    try:
        data = request.get_json()
        schema_text = data.get('schema', '').strip()
        db_type = data.get('db_type', 'sqlite').lower()
        
        if not schema_text:
            return jsonify({
                'success': False,
                'error': 'Please provide a database schema'
            }), 400
        
        if db_type not in DATABASE_SYNTAX:
            return jsonify({
                'success': False,
                'error': 'Invalid database type'
            }), 400
        
        parsed_schema = parse_schema_input(schema_text)
        
        if not parsed_schema:
            return jsonify({
                'success': False,
                'error': 'Could not parse schema. Please check the format.'
            }), 400
        
        # Store in session
        session['schema_text'] = schema_text
        session['parsed_schema'] = parsed_schema
        session['db_type'] = db_type
        
        # Create SQLite database for testing (only if SQLite selected)
        db_created = False
        if db_type == 'sqlite':
            db_created = create_database_from_schema(parsed_schema)
        
        return jsonify({
            'success': True,
            'message': f'Schema saved for {DATABASE_SYNTAX[db_type]["name"]}!',
            'tables': list(parsed_schema.keys()),
            'database_created': db_created,
            'db_type': DATABASE_SYNTAX[db_type]['name']
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/generate', methods=['POST'])
def generate():
    """
    Generates SQL query for the selected database type.
    """
    try:
        data = request.get_json()
        user_query = data.get('query', '').strip()
        
        if not user_query:
            return jsonify({
                'success': False,
                'error': 'Please provide a query'
            }), 400
        
        if 'schema_text' not in session:
            return jsonify({
                'success': False,
                'error': 'Please provide a database schema first'
            }), 400
        
        schema_text = format_schema_for_prompt(session.get('parsed_schema', {}))
        db_type = session.get('db_type', 'sqlite')
        
        # Generate SQL
        result = generate_sql_query(user_query, schema_text, db_type)
        
        if not result['success']:
            return jsonify(result), 500
        
        # Validate (only for SQLite)
        validation = validate_query(result['sql'], db_type)
        
        return jsonify({
            'success': True,
            'natural_query': user_query,
            'sql_query': result['sql'],
            'database_type': result['database_type'],
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
    session.pop('db_type', None)
    
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    
    return jsonify({
        'success': True,
        'message': 'Schema cleared'
    })

@app.route('/get-db-info/<db_type>', methods=['GET'])
def get_db_info(db_type):
    """
    Returns syntax information for a specific database type.
    """
    if db_type not in DATABASE_SYNTAX:
        return jsonify({
            'success': False,
            'error': 'Invalid database type'
        }), 404
    
    return jsonify({
        'success': True,
        'syntax': DATABASE_SYNTAX[db_type]
    })

if __name__ == '__main__':
    print("\n🚀 SQL Query Generator is running!")
    print("📍 Open http://localhost:5000 in your browser")
    print("✨ Now supports SQLite, MySQL, Oracle, and PostgreSQL!\n")
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)