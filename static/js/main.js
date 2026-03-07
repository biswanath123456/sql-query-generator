// ===== GLOBAL STATE =====
let currentSQL = '';
let schemaLoaded = false;

// ===== SCHEMA TEMPLATES =====
const templates = {
    ecommerce: `Table: customers
- id: INTEGER
- name: TEXT
- email: TEXT
- phone: TEXT
- created_at: TIMESTAMP

Table: products
- id: INTEGER
- name: TEXT
- description: TEXT
- price: REAL
- stock: INTEGER
- category: TEXT

Table: orders
- id: INTEGER
- customer_id: INTEGER
- order_date: TIMESTAMP
- total_amount: REAL
- status: TEXT

Table: order_items
- id: INTEGER
- order_id: INTEGER
- product_id: INTEGER
- quantity: INTEGER
- price: REAL`,

    social: `Table: users
- id: INTEGER
- username: TEXT
- email: TEXT
- created_at: TIMESTAMP
- followers_count: INTEGER

Table: posts
- id: INTEGER
- user_id: INTEGER
- content: TEXT
- created_at: TIMESTAMP
- likes_count: INTEGER

Table: comments
- id: INTEGER
- post_id: INTEGER
- user_id: INTEGER
- content: TEXT
- created_at: TIMESTAMP`,

    hr: `Table: employees
- id: INTEGER
- first_name: TEXT
- last_name: TEXT
- email: TEXT
- hire_date: DATE
- salary: REAL
- department_id: INTEGER

Table: departments
- id: INTEGER
- name: TEXT
- manager_id: INTEGER
- location: TEXT

Table: projects
- id: INTEGER
- name: TEXT
- start_date: DATE
- end_date: DATE
- budget: REAL

Table: employee_projects
- employee_id: INTEGER
- project_id: INTEGER
- role: TEXT
- hours_allocated: INTEGER`
};

// ===== DOM READY =====
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
});

// ===== EVENT LISTENERS =====
function initializeEventListeners() {
    const queryInput = document.getElementById('queryInput');
    
    // Enter key to submit (Shift+Enter for new line)
    if (queryInput) {
        queryInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                generateSQL();
            }
        });
    }
}

// ===== LOAD TEMPLATE =====
function loadTemplate(templateName) {
    const schemaInput = document.getElementById('schemaInput');
    schemaInput.value = templates[templateName];
    schemaInput.focus();
    
    // Smooth scroll to textarea
    schemaInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

// ===== SAVE SCHEMA =====
async function saveSchema() {
    const schemaInput = document.getElementById('schemaInput');
    const saveBtn = document.getElementById('saveSchemaBtn');
    const statusDiv = document.getElementById('schemaStatus');
    
    const schemaText = schemaInput.value.trim();
    
    if (!schemaText) {
        showSchemaStatus('Please enter a database schema', 'error');
        return;
    }
    
    // Show loading
    saveBtn.disabled = true;
    saveBtn.innerHTML = '<span class="btn-icon">⏳</span> Saving...';
    
    try {
        const response = await fetch('/save-schema', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ schema: schemaText })
        });
        
        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.error);
        }
        
        // Success
        showSchemaStatus(
            `✓ Schema saved! Found ${data.tables.length} table(s): ${data.tables.join(', ')}`,
            'success'
        );
        
        schemaLoaded = true;
        
        // Show query section
        document.getElementById('querySection').style.display = 'block';
        document.getElementById('clearSchemaBtn').style.display = 'block';
        
        // Display current schema
        displayCurrentSchema(schemaText);
        
        // Generate example queries
        generateExampleQueries(data.tables);
        
        // Smooth scroll to query section
        setTimeout(() => {
            document.getElementById('querySection').scrollIntoView({ 
                behavior: 'smooth', 
                block: 'start' 
            });
        }, 300);
        
    } catch (error) {
        showSchemaStatus(`Error: ${error.message}`, 'error');
    } finally {
        saveBtn.disabled = false;
        saveBtn.innerHTML = '<span class="btn-icon">💾</span> Save Schema';
    }
}

// ===== CLEAR SCHEMA =====
async function clearSchema() {
    if (!confirm('Are you sure you want to clear the schema?')) {
        return;
    }
    
    try {
        await fetch('/clear-schema', { method: 'POST' });
        
        // Reset UI
        document.getElementById('schemaInput').value = '';
        document.getElementById('schemaStatus').style.display = 'none';
        document.getElementById('querySection').style.display = 'none';
        document.getElementById('clearSchemaBtn').style.display = 'none';
        document.getElementById('currentSchemaDisplay').style.display = 'none';
        document.getElementById('resultsContainer').classList.remove('show');
        
        schemaLoaded = false;
        
        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
        
    } catch (error) {
        alert('Error clearing schema: ' + error.message);
    }
}

// ===== SHOW SCHEMA STATUS =====
function showSchemaStatus(message, type) {
    const statusDiv = document.getElementById('schemaStatus');
    statusDiv.textContent = message;
    statusDiv.className = `schema-status ${type}`;
}

// ===== DISPLAY CURRENT SCHEMA =====
function displayCurrentSchema(schemaText) {
    const display = document.getElementById('currentSchemaDisplay');
    const schemaDisplay = document.getElementById('schemaDisplay');
    
    // Parse schema
    const lines = schemaText.split('\n');
    let html = '';
    let currentTable = '';
    let columns = [];
    
    lines.forEach(line => {
        line = line.trim();
        if (line.toLowerCase().startsWith('table:')) {
            // Save previous table
            if (currentTable) {
                html += createTableHTML(currentTable, columns);
            }
            currentTable = line.split(':')[1].trim();
            columns = [];
        } else if (line.startsWith('-')) {
            columns.push(line.substring(1).trim());
        }
    });
    
    // Save last table
    if (currentTable) {
        html += createTableHTML(currentTable, columns);
    }
    
    schemaDisplay.innerHTML = html;
    display.style.display = 'block';
}

function createTableHTML(tableName, columns) {
    let html = `<div class="schema-table-display">
                    <h4>${tableName}</h4>
                    <ul>`;
    
    columns.forEach(col => {
        const [name, type] = col.split(':');
        html += `<li><span class="field-type">${type.trim()}</span> ${name.trim()}</li>`;
    });
    
    html += '</ul></div>';
    return html;
}

// ===== GENERATE EXAMPLE QUERIES =====
function generateExampleQueries(tables) {
    const container = document.getElementById('examplesContainer');
    
    const examples = [
        `Show me all records from ${tables[0]}`,
        `Count the total number of rows in ${tables[0]}`,
        tables.length > 1 ? `Join ${tables[0]} and ${tables[1]}` : `Find records in ${tables[0]} ordered by id`,
        `Get the top 10 records from ${tables[0]}`,
    ];
    
    let html = '';
    examples.forEach(ex => {
        html += `<div class="example-item" onclick="fillExample(this)">${ex}</div>`;
    });
    
    container.innerHTML = html;
}

// ===== FILL EXAMPLE QUERY =====
function fillExample(element) {
    const queryInput = document.getElementById('queryInput');
    queryInput.value = element.textContent.trim();
    queryInput.focus();
    queryInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

// ===== GENERATE SQL =====
async function generateSQL() {
    if (!schemaLoaded) {
        alert('Please save your database schema first!');
        return;
    }
    
    const queryInput = document.getElementById('queryInput');
    const generateBtn = document.getElementById('generateBtn');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const resultsContainer = document.getElementById('resultsContainer');
    
    const userQuery = queryInput.value.trim();
    
    if (!userQuery) {
        showError('Please enter a query description!');
        return;
    }
    
    // Reset UI
    hideAllResults();
    
    // Show loading
    generateBtn.disabled = true;
    generateBtn.innerHTML = '<span class="btn-icon">⏳</span> Generating...';
    loadingIndicator.classList.add('active');
    
    try {
        const response = await fetch('/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query: userQuery })
        });
        
        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.error);
        }
        
        displayResults(data);
        
    } catch (error) {
        showError(error.message);
    } finally {
        generateBtn.disabled = false;
        generateBtn.innerHTML = '<span class="btn-icon">✨</span> Generate SQL Query';
        loadingIndicator.classList.remove('active');
    }
}

// ===== DISPLAY RESULTS =====
function displayResults(data) {
    const resultsContainer = document.getElementById('resultsContainer');
    
    document.getElementById('naturalQuery').textContent = data.natural_query;
    
    currentSQL = data.sql_query;
    const highlightedSQL = highlightSQL(data.sql_query);
    document.getElementById('sqlQuery').innerHTML = highlightedSQL;
    
    displayValidationStatus(data.validation);
    
    resultsContainer.classList.add('show');
    resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// ===== DISPLAY VALIDATION STATUS =====
function displayValidationStatus(validation) {
    const statusDiv = document.getElementById('validationStatus');
    const resultsSection = document.getElementById('resultsSection');
    const errorSection = document.getElementById('errorSection');
    
    if (validation.valid) {
        statusDiv.innerHTML = `<div class="status status-valid">✓ Query is valid</div>`;
        
        if (validation.results && validation.results.length > 0) {
            resultsSection.style.display = 'block';
            document.getElementById('rowCount').textContent = validation.row_count;
            displayDataTable(validation.columns, validation.results);
        } else if (validation.message) {
            resultsSection.style.display = 'block';
            document.getElementById('dataTableContainer').innerHTML = 
                `<p style="text-align: center; color: var(--gray-600);">${validation.message}</p>`;
        } else {
            resultsSection.style.display = 'none';
        }
        
        errorSection.style.display = 'none';
    } else {
        statusDiv.innerHTML = `<div class="status status-invalid">✗ SQL has errors</div>`;
        errorSection.style.display = 'block';
        document.getElementById('errorMessage').textContent = `SQL Error: ${validation.error}`;
        resultsSection.style.display = 'none';
    }
}

// ===== SQL SYNTAX HIGHLIGHTING =====
function highlightSQL(sql) {
    const keywords = [
        'SELECT', 'FROM', 'WHERE', 'JOIN', 'LEFT', 'RIGHT', 'INNER', 'OUTER',
        'ON', 'ORDER BY', 'GROUP BY', 'HAVING', 'LIMIT', 'OFFSET',
        'COUNT', 'SUM', 'AVG', 'MAX', 'MIN', 'AS', 'AND', 'OR', 'NOT',
        'IN', 'LIKE', 'BETWEEN', 'IS', 'NULL', 'DESC', 'ASC',
        'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP', 'ALTER', 'DISTINCT'
    ];
    
    let highlighted = sql;
    
    keywords.forEach(keyword => {
        const regex = new RegExp(`\\b${keyword}\\b`, 'gi');
        highlighted = highlighted.replace(regex, match => 
            `<span class="sql-keyword">${match.toUpperCase()}</span>`
        );
    });
    
    highlighted = highlighted.replace(/'([^']*)'/g, 
        `<span class="sql-string">'$1'</span>`);
    
    highlighted = highlighted.replace(/\b(\d+)\b/g, 
        `<span class="sql-number">$1</span>`);
    
    return highlighted;
}

// ===== DISPLAY DATA TABLE =====
function displayDataTable(columns, rows) {
    const tableContainer = document.getElementById('dataTableContainer');
    
    let html = '<table class="data-table"><thead><tr>';
    
    columns.forEach(col => {
        html += `<th>${escapeHtml(col)}</th>`;
    });
    html += '</tr></thead><tbody>';
    
    const displayRows = rows.slice(0, 10);
    displayRows.forEach(row => {
        html += '<tr>';
        row.forEach(cell => {
            if (cell === null) {
                html += '<td style="color: var(--gray-400); font-style: italic;">NULL</td>';
            } else {
                html += `<td>${escapeHtml(String(cell))}</td>`;
            }
        });
        html += '</tr>';
    });
    
    html += '</tbody></table>';
    
    if (rows.length > 10) {
        html += `<p style="margin-top: 1rem; color: var(--gray-600); font-size: 0.875rem; text-align: center;">
                 Showing first 10 of ${rows.length} results</p>`;
    }
    
    tableContainer.innerHTML = html;
}

// ===== COPY SQL TO CLIPBOARD =====
async function copySQLToClipboard() {
    if (!currentSQL) return;
    
    try {
        await navigator.clipboard.writeText(currentSQL);
        
        const btn = event.target;
        const originalText = btn.textContent;
        btn.textContent = '✓';
        
        setTimeout(() => {
            btn.textContent = originalText;
        }, 2000);
    } catch (err) {
        alert('Failed to copy SQL to clipboard');
    }
}

// ===== ERROR HANDLING =====
function showError(message) {
    const resultsContainer = document.getElementById('resultsContainer');
    const errorSection = document.getElementById('errorSection');
    const errorMessage = document.getElementById('errorMessage');
    
    errorMessage.textContent = message;
    errorSection.style.display = 'block';
    resultsContainer.classList.add('show');
    
    document.getElementById('resultsSection').style.display = 'none';
    document.getElementById('validationStatus').innerHTML = '';
}

// ===== UTILITY FUNCTIONS =====
function hideAllResults() {
    const resultsContainer = document.getElementById('resultsContainer');
    resultsContainer.classList.remove('show');
    
    document.getElementById('resultsSection').style.display = 'none';
    document.getElementById('errorSection').style.display = 'none';
}

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}