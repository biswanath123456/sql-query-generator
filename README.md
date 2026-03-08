# 🤖 SQL Query Generator


Convert natural language questions into SQL queries using AI. Supports **SQLite, MySQL, Oracle, and PostgreSQL** with database-specific syntax generation. Define your own database schema and let the LLM generate accurate, production-ready SQL queries instantly.
=======
Convert natural language questions into SQL queries using AI. Define your own database schema and let the LLM generate accurate SQL queries instantly.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)
![Groq](https://img.shields.io/badge/Groq-API-purple.svg)
![Databases](https://img.shields.io/badge/Databases-4-orange.svg)
=======
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 🌟 Features

- **Multi-Database Support** - SQLite, MySQL, Oracle, PostgreSQL
- **Database-Specific Syntax** - Generates correct SQL for each database type
- **Custom Schema Support** - Define your own database structure
- **Natural Language Processing** - Ask questions in plain English
- **Real-time SQL Generation** - Powered by Groq's Llama 3.3 70B model
- **Query Validation** - Automatic syntax checking (SQLite)
- **Query Execution** - Test queries and see results instantly (SQLite)
- **Schema Templates** - Pre-built templates for common use cases
- **Syntax Reference** - Database-specific syntax guides
=======
- **Custom Schema Support** - Define your own database structure
- **Natural Language Processing** - Ask questions in plain English
- **Real-time SQL Generation** - Powered by Groq's Llama 3.3 70B model
- **Query Validation** - Automatic syntax checking against SQLite
- **Query Execution** - Test queries and see results instantly
- **Schema Templates** - Pre-built templates for common use cases
>>>>>>> 433536f84ea5ecac1a929fb0fe11a5cb34acad8c
- **Syntax Highlighting** - Beautiful SQL code display
- **Copy to Clipboard** - One-click SQL copying
- **Responsive Design** - Works on desktop and mobile

## 📋 Table of Contents

- [Demo](#-demo)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [How It Works](#-how-it-works)
- [API Endpoints](#-api-endpoints)
- [Configuration](#-configuration)
- [Examples](#-examples)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

## 🎬 Demo


### Step 1: Select Database Type
Choose from: **SQLite** 🗄️ | **MySQL** 🐬 | **Oracle** 🏛️ | **PostgreSQL** 🐘

### Step 2: Define Your Schema
=======
### Step 1: Define Your Schema
```
Table: users
- id: INTEGER
- username: TEXT
- email: TEXT
- created_at: TIMESTAMP

Table: posts
- id: INTEGER
- user_id: INTEGER
- content: TEXT
- likes: INTEGER
```


### Step 3: Ask Questions (Database-Specific Output!)

**Input:** "Show me all users who joined in the last 30 days"

**SQLite Output:**
=======
### Step 2: Ask Questions
**Input:** "Show me all users who joined in the last 30 days"

**Output:**
```sql
SELECT * FROM users 
WHERE created_at >= DATE('now', '-30 days')
ORDER BY created_at DESC;
```

**MySQL Output:**
```sql
SELECT * FROM users 
WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
ORDER BY created_at DESC;
```

**Oracle Output:**
```sql
SELECT * FROM users 
WHERE created_at >= SYSDATE - 30
ORDER BY created_at DESC;
```

**PostgreSQL Output:**
```sql
SELECT * FROM users 
WHERE created_at >= NOW() - INTERVAL '30 days'
ORDER BY created_at DESC;
```

=======
>>>>>>> 433536f84ea5ecac1a929fb0fe11a5cb34acad8c
## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Groq API key (free tier available)

### Step 1: Clone the Repository

```bash

git clone https://github.com/biswanath123456/sql-query-generator.git
=======
git clone https://github.com/yourusername/sql-query-generator.git
cd sql-query-generator
```

### Step 2: Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Get Groq API Key

1. Visit [Groq Console](https://console.groq.com)
2. Sign up for a free account
3. Navigate to API Keys section
4. Create a new API key

### Step 5: Configure Environment Variables

Create a `.env` file in the project root:

```bash
GROQ_API_KEY=your_api_key_here
```

**Important:** Never commit your `.env` file to version control!

## ⚡ Quick Start

1. **Start the application:**
   ```bash
   python app.py
   ```

2. **Open your browser:**
   ```
   http://localhost:5000
   ```

3. **Define your schema:**
   - Use a template or write your own
   - Click "Save Schema"

4. **Generate queries:**
   - Type what data you need in plain English
   - Click "Generate SQL Query"
   - Copy and use the SQL!

## 📖 Usage

### Selecting Database Type

Choose your target database before defining the schema:

| Database | Best For | Syntax Features |
|----------|----------|----------------|
| **SQLite** | Development, Testing, Small Apps | `DATE('now')`, `||` concatenation |
| **MySQL** | Web Apps, Medium Scale | `NOW()`, `CONCAT()`, `INTERVAL` |
| **Oracle** | Enterprise, Large Scale | `SYSDATE`, `FETCH FIRST`, Sequences |
| **PostgreSQL** | Advanced Features, JSON | `CURRENT_DATE`, `INTERVAL`, JSONB |

=======

### Defining a Schema

Your schema should follow this format:

```
Table: table_name
- column_name: DATA_TYPE
- another_column: DATA_TYPE

Table: another_table
- column_name: DATA_TYPE
```

**Supported Data Types:**
- `INTEGER` - Whole numbers
- `TEXT` - String/text data
- `REAL` / `DECIMAL` / `NUMERIC` - Decimal numbers
- `TIMESTAMP` / `DATETIME` - Date and time
- `DATE` - Date only
- `BOOLEAN` - True/false values
- `VARCHAR(n)` - Variable length string (MySQL, Oracle, PostgreSQL)

### Example Queries by Database

**SQLite:**
| Natural Language | Generated SQL |
|-----------------|---------------|
| "Show all users" | `SELECT * FROM users;` |
| "Users from last week" | `SELECT * FROM users WHERE created_at >= DATE('now', '-7 days');` |
| "Top 5 posts" | `SELECT * FROM posts ORDER BY likes DESC LIMIT 5;` |

**MySQL:**
| Natural Language | Generated SQL |
|-----------------|---------------|
| "Recent orders" | `SELECT * FROM orders WHERE order_date >= DATE_SUB(NOW(), INTERVAL 7 DAY);` |
| "Concatenate names" | `SELECT CONCAT(first_name, ' ', last_name) AS full_name FROM users;` |
| "Top 10 products" | `SELECT * FROM products ORDER BY sales DESC LIMIT 10;` |

**Oracle:**
| Natural Language | Generated SQL |
|-----------------|---------------|
| "Recent records" | `SELECT * FROM users WHERE created_at >= SYSDATE - 7;` |
| "Top 5 employees" | `SELECT * FROM employees ORDER BY salary DESC FETCH FIRST 5 ROWS ONLY;` |
| "Pagination" | `SELECT * FROM posts OFFSET 20 ROWS FETCH NEXT 10 ROWS ONLY;` |

**PostgreSQL:**
| Natural Language | Generated SQL |
|-----------------|---------------|
| "Last month data" | `SELECT * FROM sales WHERE sale_date >= NOW() - INTERVAL '1 month';` |
| "Case-insensitive search" | `SELECT * FROM users WHERE username ILIKE '%john%';` |
| "Array operations" | `SELECT * FROM posts WHERE tags && ARRAY['tech', 'ai'];` |
=======
- `REAL` - Decimal numbers
- `TIMESTAMP` - Date and time
- `DATE` - Date only
- `BOOLEAN` - True/false values

### Example Queries

Once your schema is loaded, try these:

| Natural Language | Generated SQL |
|-----------------|---------------|
| "Show all users" | `SELECT * FROM users;` |
| "Count total posts" | `SELECT COUNT(*) FROM posts;` |
| "Top 5 most liked posts" | `SELECT * FROM posts ORDER BY likes DESC LIMIT 5;` |
| "Users with no posts" | `SELECT * FROM users WHERE id NOT IN (SELECT DISTINCT user_id FROM posts);` |
| "Posts by user alice" | `SELECT posts.* FROM posts JOIN users ON posts.user_id = users.id WHERE users.username = 'alice';` |

### Using Templates

Click any template button to auto-fill the schema:

- **🛒 E-commerce** - Customers, Products, Orders
- **👥 Social Media** - Users, Posts, Comments
- **💼 HR System** - Employees, Departments, Projects

## 📁 Project Structure

```
sql-query-generator/
├── app.py                      # Flask backend application
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (not in git)
├── README.md                   # This file
├── templates/
│   └── index.html             # Main HTML template
├── static/
│   ├── css/
│   │   └── style.css          # All styles
│   └── js/
│       └── main.js            # Frontend logic
└── user_database.db           # SQLite database (auto-generated)
```

## 🔧 How It Works

### Architecture Flow

```
┌─────────────┐
│    User     │
│   (Browser) │
└──────┬──────┘
       │ 1. Define Schema
       ▼
┌─────────────────┐
│  Flask Backend  │
│   (Session)     │ ← Stores schema
└────────┬────────┘
         │ 2. Natural Language Query
         ▼
┌──────────────────┐
│   Groq API       │
│ (Llama 3.3 70B)  │ ← Converts to SQL
└────────┬─────────┘
         │ 3. Generated SQL
         ▼
┌──────────────────┐
│ SQLite Database  │ ← Validates & executes
│  (Optional)      │
└────────┬─────────┘
         │ 4. Results
         ▼
┌─────────────┐
│  Frontend   │ ← Displays results
│   (HTML/JS) │
└─────────────┘
```

### Key Components

1. **Schema Parser** (`parse_schema_input()`)
   - Converts user text into structured format
   - Validates table and column definitions

2. **Prompt Engineer** (`generate_sql_query()`)
   - Builds context-aware prompts
   - Includes schema and examples
   - Calls Groq API

3. **Query Validator** (`validate_query()`)
   - Tests SQL against SQLite
   - Returns errors or results

4. **Session Manager** (Flask sessions)
   - Stores schema across requests
   - Maintains state

## 🔌 API Endpoints

### POST `/save-schema`

Saves user-defined database schema.

**Request:**
```json
{
  "schema": "Table: users\n- id: INTEGER\n- name: TEXT"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Schema saved successfully!",
  "tables": ["users"],
  "database_created": true
}
```

### POST `/generate`

Generates SQL from natural language.

**Request:**
```json
{
  "query": "Show me all users"
}
```

**Response:**
```json
{
  "success": true,
  "natural_query": "Show me all users",
  "sql_query": "SELECT * FROM users;",
  "validation": {
    "valid": true,
    "columns": ["id", "name"],
    "results": [[1, "Alice"], [2, "Bob"]],
    "row_count": 2
  }
}
```

### POST `/clear-schema`

Clears stored schema and database.

**Response:**
```json
{
  "success": true,
  "message": "Schema cleared"
}
```

## ⚙️ Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GROQ_API_KEY` | Yes | - | Your Groq API key |

### Model Configuration

In `app.py`, you can change the AI model:

```python
model="llama-3.3-70b-versatile"  # Current
# model="llama-3.1-8b-instant"   # Faster, less accurate
# model="mixtral-8x7b-32768"     # Alternative
```

### Temperature Setting

Adjust creativity vs consistency:

```python
temperature=0.1  # More consistent (recommended for SQL)
# temperature=0.5  # More creative
```

## 💡 Examples

### E-commerce Database

**Schema:**
```
Table: products
- id: INTEGER
- name: TEXT
- price: REAL
- category: TEXT

Table: orders
- id: INTEGER
- product_id: INTEGER
- quantity: INTEGER
- order_date: TIMESTAMP
```

**Queries:**
- "Show products under $50" → `SELECT * FROM products WHERE price < 50;`
- "Total revenue by category" → `SELECT category, SUM(price) FROM products GROUP BY category;`
- "Orders from last week" → `SELECT * FROM orders WHERE order_date >= DATE('now', '-7 days');`

### Social Media Database

**Schema:**
```
Table: users
- id: INTEGER
- username: TEXT
- followers: INTEGER

Table: posts
- id: INTEGER
- user_id: INTEGER
- content: TEXT
- likes: INTEGER
```

**Queries:**
- "Top 10 users by followers" → `SELECT * FROM users ORDER BY followers DESC LIMIT 10;`
- "Posts with more than 100 likes" → `SELECT * FROM posts WHERE likes > 100;`
- "User activity summary" → `SELECT users.username, COUNT(posts.id) as post_count FROM users LEFT JOIN posts ON users.id = posts.user_id GROUP BY users.id;`

## 🐛 Troubleshooting

### Common Issues

**1. "Model decommissioned" error**

Update the model name in `app.py`:
```python
model="llama-3.3-70b-versatile"  # Use latest model
```

**2. "API key not found" error**

Ensure `.env` file exists with:
```
GROQ_API_KEY=your_actual_key_here
```

**3. "Schema not found" error**

Click "Save Schema" before generating queries.

**4. Invalid SQL generated**

- Make sure your schema is properly formatted
- Use the exact table/column names from your schema
- Try rephrasing your question

**5. Port already in use**

Change the port in `app.py`:
```python
app.run(debug=True, port=5001)  # Change from 5000
```

### Getting Help

- Check the [Issues](https://github.com/biswanath123456/sql-query-generator/issues) page
- Review Groq [API Documentation](https://console.groq.com/docs)
- Ensure all dependencies are installed: `pip install -r requirements.txt`

## 🎓 Learning Objectives

This project teaches:

1. **LLM Integration** - How to use language models via API
2. **Prompt Engineering** - Crafting effective prompts for SQL generation
3. **Flask Web Development** - Building REST APIs
4. **Session Management** - Storing state across requests
5. **Frontend Development** - HTML/CSS/JavaScript interaction
6. **Database Basics** - SQLite and SQL queries
7. **Error Handling** - Validating and catching errors
8. **API Design** - Creating clean, RESTful endpoints

## 🚧 Roadmap


### ✅ Completed Features

- [x] Support for MySQL and Oracle and PostgreSQL
- [x] Database-specific syntax generation
- [x] Visual database type selection
- [x] Syntax reference guides

### 🔜 Future Enhancements

- [ ] Direct database connection (connect to live databases)
- [ ] Query history and favorites
- [ ] Export results to CSV/Excel
- [ ] Multi-user authentication
- [ ] Query optimization suggestions
- [ ] Dark mode toggle
- [ ] SQL query explanation feature (explain what the query does)
- [ ] Advanced filtering and sorting in results
- [ ] Database schema import from live databases
- [ ] SQL to Natural Language (reverse translation)
=======
Future enhancements:

- [ ] Support for MySQL and PostgreSQL
- [ ] Query history and favorites
- [ ] Export results to CSV/Excel
- [ ] Database connection from external sources
- [ ] Multi-user authentication
- [ ] Query optimization suggestions
- [ ] Dark mode toggle
- [ ] SQL query explanation feature
- [ ] Advanced filtering and sorting

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guide for Python
- Add comments for complex logic
- Test thoroughly before submitting
- Update documentation as needed

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Groq](https://groq.com) - For providing free LLM API access
- [Flask](https://flask.palletsprojects.com/) - Micro web framework

- [SQLite](https://www.sqlite.org/) - Embedded database for testing
- [MySQL](https://www.mysql.com/) - World's most popular open-source database
- [Oracle](https://www.oracle.com/database/) - Enterprise database system
- [PostgreSQL](https://www.postgresql.org/) - Advanced open-source database
=======
- [SQLite](https://www.sqlite.org/) - Embedded database
- Meta's [Llama 3.3](https://ai.meta.com/llama/) - Language model

## 📞 Contact

**Project Link:** [https://github.com/biswanath123456/sql-query-generator](https://github.com/biswanath123456/sql-query-generator)


**Author:** Your Name
- Email: biswanath2048@gmail.com
- LinkedIn: [Biswanath Mahapatra](https://www.linkedin.com/in/biswanath-mahapatra/))


---

**Built with ❤️ for learning LLM applications**

*Supports 4 major databases: SQLite • MySQL • Oracle • PostgreSQL*

*Star ⭐ this repo if you find it helpful!*