# 🌐 SQLSphere
### AI-Powered Conversational Database Assistant

<p align="center">
  <img src="https://img.shields.io/badge/AI-Gemini-blueviolet?style=for-the-badge&logo=google" alt="Gemini">
  <img src="https://img.shields.io/badge/Backend-Flask-black?style=for-the-badge&logo=flask" alt="Flask">
  <img src="https://img.shields.io/badge/Frontend-React-61DAFB?style=for-the-badge&logo=react" alt="React">
  <img src="https://img.shields.io/badge/Database-MySQL-4479A1?style=for-the-badge&logo=mysql" alt="MySQL">
  <img src="https://img.shields.io/badge/Language-Python-3776AB?style=for-the-badge&logo=python" alt="Python">
</p>

<p align="center">
  <b>Talk to your database in natural language. 💬 → 🧠 → 🗄️ → 📊</b>
</p>

<p align="center">
  SQLSphere transforms everyday questions into SQL queries using AI, executes them securely against a relational database, and presents the results through an intuitive interactive dashboard.
</p>

---

## ✨ What is SQLSphere?

**SQLSphere** is an AI-powered conversational database assistant designed to make relational databases easier to interact with.

Instead of writing SQL manually, users can simply ask questions such as:

> 💬 **"Show students with CGPA above 8"**

or

> 💬 **"Show students from CSE"**

SQLSphere understands the request, generates the appropriate SQL query, validates it, executes it against MySQL, and displays the results in a clean dashboard.

### 🚀 The idea is simple:

```text
Natural Language
       ↓
   React UI
       ↓
    Flask API
       ↓
 Value Grounding
       ↓
    Gemini AI
       ↓
 Generated SQL
       ↓
 SQL Security Validation
       ↓
      MySQL
       ↓
 Results + Charts + Explanation
```

---

# 💎 Key Features

## 🗣️ Natural Language → SQL

Ask questions using normal human language instead of manually writing SQL.

Examples:

```text
Show all students with CGPA above 8

Show students from CSE

Show the average CGPA of students in each department

Show students with attendance below 75 percent

Show all students with their departments
```

SQLSphere converts these requests into executable SQL.

---

## 🧠 AI-Powered SQL Generation

SQLSphere uses **Google Gemini** to understand natural-language questions and generate SQL queries based on the actual database schema.

The generated SQL is displayed to the user before/alongside the results so that the database interaction remains transparent.

---

## 🎯 Value Grounding

One of SQLSphere's important features is **Value Grounding**.

It connects words used by the user with actual values stored in the database.

For example:

```text
CSE
 ↓
Computer Science and Engineering
```

Similarly:

```text
Computer Science
 ↓
Computer Science and Engineering
```

This helps prevent the AI from treating user terminology and database terminology as completely unrelated values.

### 🔐 Ambiguity Protection

SQLSphere does **not blindly guess** when multiple database values could match a user's request.

For example:

```text
Show students from the engineering department
```

If the database contains:

```text
Computer Science and Engineering
Electronics and Communication Engineering
Mechanical Engineering
Electrical and Electronics Engineering
```

SQLSphere can detect the ambiguity and ask the user for clarification instead of silently choosing one.

---

## 💬 Conversational Context

SQLSphere supports follow-up questions.

For example:

```text
User:
Show students with CGPA above 8

User:
Now show only their names
```

The second question can use the context of the previous request rather than starting from scratch.

---

## 🔧 Automatic Query Repair

If an AI-generated SQL query encounters an execution error, SQLSphere can attempt to repair the query using Gemini.

Example flow:

```text
Generated SQL
      ↓
Execution Error
      ↓
Query Repair
      ↓
Gemini
      ↓
Corrected SQL
      ↓
Validation
      ↓
Execution
```

The dashboard can also show that the query was automatically repaired and allow the corrected SQL to be viewed.

---

## 🛡️ SQL Security

SQLSphere is designed for **read-only database interaction**.

Potentially destructive operations are blocked, including:

```text
INSERT
UPDATE
DELETE
DROP
ALTER
CREATE
TRUNCATE
REPLACE
GRANT
REVOKE
CALL
LOAD
LOCK
UNLOCK
SET
USE
RENAME
```

SQL comments and multiple SQL statements are also rejected.

For example:

```sql
DROP TABLE students;
```

is blocked instead of being executed.

This provides an additional security layer between AI-generated SQL and the database.

---

## 📊 Automatic Data Visualization

SQLSphere can automatically generate visualizations from query results.

Supported visualization types include:

- 📊 Bar Chart
- 📈 Line Chart
- 🥧 Pie Chart
- 🍩 Doughnut Chart

The system determines an appropriate visualization based on the returned data.

---

## 🧾 SQL Explanation

SQLSphere can explain generated SQL in simple language.

For example:

```sql
SELECT T2.department_name, AVG(T1.cgpa)
FROM students AS T1
JOIN departments AS T2
ON T1.department_id = T2.department_id
GROUP BY T2.department_name;
```

The dashboard provides a human-readable explanation of what the query is doing.

---

## 🕘 Query History

Previous queries can be accessed through the Query History section.

Users can:

- View previous questions
- View generated SQL
- Run a previous query again
- Review previous query results

---

## 🗄️ Dynamic Schema Explorer

SQLSphere provides a database Schema Explorer that dynamically displays:

- Database tables
- Columns
- Data types
- Primary keys
- Foreign keys
- Table relationships

This makes the database structure easier to understand without manually inspecting MySQL.

---

## 📤 Export Results

Query results can be exported in multiple formats:

- 📄 CSV
- 📊 Excel
- 📑 PDF

This makes the generated results easier to reuse in reports, analysis, and documentation.

---

## 📈 Evaluation & Debugging

SQLSphere includes a development evaluation system for tracking AI/database performance.

It can record information such as:

```text
Question
Generated SQL
Grounded Values
Confidence Score
Validation Result
Execution Success
Row Count
Repair Attempt
Repair Success
Final SQL
Response Time
Context Used
Error
Timestamp
```

This makes it easier to evaluate the reliability of the natural-language-to-SQL pipeline.

---

# 🏗️ System Architecture

```text
                    ┌─────────────────────┐
                    │      User Query     │
                    │   Natural Language  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    React Frontend   │
                    │  Interactive UI     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │     Flask REST API  │
                    │      /query         │
                    └──────────┬──────────┘
                               │
                ┌──────────────┴──────────────┐
                │                             │
                ▼                             ▼
       ┌─────────────────┐          ┌─────────────────┐
       │ Value Grounding │          │ Conversation    │
       │                 │          │ Context        │
       └────────┬────────┘          └────────┬────────┘
                │                            │
                └──────────────┬─────────────┘
                               ▼
                    ┌─────────────────────┐
                    │    Gemini AI        │
                    │   SQL Generation    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   SQL Security      │
                    │    Validation       │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │       MySQL         │
                    │ student_management   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Results + Charts    │
                    │ Explanation + Export│
                    └─────────────────────┘
```

---

# 🗃️ Database

SQLSphere currently works with a relational **MySQL `student_management` database** containing:

```text
students
departments
faculty
courses
enrollments
marks
attendance
```

### Relationships

```text
students ──────── departments
    │
    ├──────────── enrollments ─────── courses
    │
    ├──────────── marks ───────────── courses
    │
    └──────────── attendance ──────── courses

faculty ───────── departments
courses ───────── departments
courses ───────── faculty
```

---

# 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| 🎨 Frontend | React.js |
| ⚙️ Backend | Python + Flask |
| 🧠 AI | Google Gemini API |
| 🗄️ Database | MySQL |
| 🔌 API Communication | REST API |
| 📊 Visualization | Chart.js |
| 📑 Excel Export | XLSX |
| 📄 PDF Export | jsPDF |
| 🔐 Configuration | Python dotenv |
| 🌐 Cross-Origin Support | Flask-CORS |

---

# 📁 Project Structure

```text
SQLSphere/
│
├── backend/
│   ├── app.py
│   ├── config.py
│   ├── gemini_service.py
│   ├── value_grounding.py
│   ├── conversation_context.py
│   ├── query_history.py
│   ├── sql_explainer.py
│   ├── sql_security.py
│   ├── evaluation.py
│   └── .env
│
├── frontend/
│   ├── src/
│   │   ├── Dashboard.js
│   │   ├── AutoChart.jsx
│   │   ├── SchemaExplorer.jsx
│   │   ├── Earth3D.jsx
│   │   └── App.css
│   ├── package.json
│   └── public/
│
├── database/
│   └── student_management.sql
│
└── README.md
```

> Folder/file names may vary slightly depending on the current repository organization.

---

# ⚙️ Installation & Setup

## 1️⃣ Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/SQLSphere.git
cd SQLSphere
```

---

## 2️⃣ Configure MySQL

Create the database:

```sql
CREATE DATABASE student_management;
```

Import the project database/schema into MySQL.

Make sure the required tables are available:

```text
students
departments
faculty
courses
enrollments
marks
attendance
```

---

## 3️⃣ Configure Backend

Navigate to the backend:

```bash
cd backend
```

Create a `.env` file:

```env
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=student_management
GEMINI_API_KEY=your_gemini_api_key
```

---

## 4️⃣ Install Python Dependencies

```bash
pip install flask flask-cors mysql-connector-python python-dotenv google-genai
```

---

## 5️⃣ Start the Backend

```bash
python app.py
```

The Flask API will run on:

```text
http://127.0.0.1:5000
```

---

## 6️⃣ Start the Frontend

Open another terminal:

```bash
cd frontend
npm install
npm start
```

The React application will normally open at:

```text
http://localhost:3000
```

---

# 💬 Example Queries

Try asking SQLSphere:

```text
Show all students
```

```text
Show students with CGPA above 8
```

```text
Show students from CSE
```

```text
Show students from Computer Science
```

```text
Show students with attendance below 75 percent
```

```text
Show the average CGPA of students in each department
```

```text
Show all students with their departments
```

```text
Now show only their names
```

---

# 🔐 Security Philosophy

AI-generated SQL should never be trusted blindly.

SQLSphere therefore follows a validation pipeline:

```text
User Input
    ↓
AI SQL Generation
    ↓
SQL Validation
    ↓
Read-only Check
    ↓
Database Execution
```

The security layer prevents destructive SQL operations from reaching the database.

> **AI generates the query. SQLSphere decides whether the query is safe to execute.**

---

# 🧪 Testing & Evaluation

SQLSphere has been tested across multiple areas including:

- Natural-language SQL generation
- Multi-table JOIN queries
- Filtering
- Aggregation
- GROUP BY
- ORDER BY
- SQL validation
- Destructive SQL blocking
- Value Grounding
- Conversation Context
- Query History
- SQL Explanation
- Query Repair
- Gemini temporary-failure retry
- Database Schema Explorer
- Result visualization
- CSV/Excel/PDF export
- Evaluation logging

### Example Security Test

```sql
DELETE FROM students;
```

Expected:

```text
❌ Blocked
```

### Example Context Test

```text
Show students with CGPA above 8
```

followed by:

```text
Now show only their names
```

Expected:

```text
Previous filtering context is preserved.
```

### Example Ambiguity Test

```text
Show students belonging to the engineering department
```

If several department values match:

```text
Computer Science and Engineering
Electronics and Communication Engineering
Mechanical Engineering
Electrical and Electronics Engineering
```

Expected:

```text
⚠️ Clarification required
```

SQLSphere should not silently choose one.

---

# 🌟 Why SQLSphere?

Traditional database interaction often requires users to understand SQL syntax.

SQLSphere aims to make database interaction more accessible:

```text
Traditional Approach

Question
   ↓
Learn SQL
   ↓
Write SQL
   ↓
Debug SQL
   ↓
Execute SQL
   ↓
Analyze Results
```

SQLSphere:

```text
Question
   ↓
Ask SQLSphere
   ↓
AI + Grounding + Validation
   ↓
Results
   ↓
Visualization
```

The goal is not simply to generate SQL.

The goal is to build a **safer, more transparent and conversational interface for relational databases.**

---

# 🎯 Future Enhancements

Possible future improvements include:

- 🔑 Role-based database access
- 🧠 Improved semantic value matching
- 💾 Persistent conversation history
- 📊 Advanced analytics dashboards
- 📈 More visualization types
- 🔍 Improved query optimization
- 🌐 Multi-database support
- 👥 Multi-user support
- 📱 Responsive mobile interface
- 🧪 Automated benchmark evaluation for Text-to-SQL accuracy

---

# 👩‍💻 Project

### SQLSphere — AI-Powered Conversational Database Assistant

Built as a major academic project exploring:

```text
Artificial Intelligence
        +
Natural Language Processing
        +
Text-to-SQL
        +
Relational Databases
        +
Web Development
        +
Data Visualization
        +
Database Security
```

---

<p align="center">
  <b>💙 Making databases easier to talk to.</b>
</p>

<p align="center">
  ⭐ If you find SQLSphere interesting, consider giving the repository a star!
</p>

<p align="center">
  <i>SQLSphere — Ask. Understand. Query. Explore. 🚀</i>
</p>
