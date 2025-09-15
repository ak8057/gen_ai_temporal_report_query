# Query Based Reports

*Transform your Excel data into intelligent, queryable insights*

---

## What This Does?

Ever wished you could just ask your spreadsheets questions and get smart answers back? That's exactly what this project does. Drop in an Excel, PDF, images or any other files, and suddenly you can have all data extracted and stored in the Sql database.

## How It Works

The magic happens in two simple steps:

**1. Data Ingestion** → Your Excel files get processed and stored in a proper SQL database  
**2. AI Analysis** → Ask questions in plain English and get intelligent answers about your data

Think of it as giving your spreadsheets a brain.

## Project Structure

```
DataRetrievalintoSQL/
│
├── 📂 DATA/                     # Where your processed data lives
│
├── 📂 feature_ingestion/        # The data processing engine
│   ├── app/
│   │   ├── venv/               # Python environment
│   │   ├── ingest.py           # The main processor
│   │   ├── requirements.txt    # What we need to run
│   │   └── [your-files.xlsx]   # Drop your Excel files here
│   ├── .env                    # Your database secrets
│   └── docker-compose.yml      # One-click deployment
│
├── 📂 queryGeneration/          # Where the AI magic happens
│   └── sql_query.ipynb         # Your data conversation interface
│
└── README.md                   # You are here
```

## What's Under the Hood

**Data Handling**
- `pandas` for data wrangling
- `openpyxl` for Excel file processing
- `sqlalchemy` for database operations

**Database Support**
- PostgreSQL with `psycopg2-binary`
- MySQL with `pymysql`

**Infrastructure**
- Docker for easy deployment
- Jupyter for interactive analysis
- GEMINI AI for intelligent querying

## Getting Started

### What You Need
- Docker (for easy setup)
- A SQL database (PostgreSQL or MySQL or mongoDB based on the usage)
- Python 3.x if you want to run things locally

### Quick Setup

**Step 1: Get the code**
```bash
git clone <your-repo-url>
cd DataRetrievalintoSQL
```

**Step 2: Configure your database**
```bash
cd feature_ingestion
# Edit the .env file with your database details
```

**Step 3: Fire it up**
```bash
docker-compose up
```

That's it. You're ready to process data.

## Using the System

### Processing Your First File

1. **Drop your Excel file** into `/feature_ingestion/app/`
2. **Make sure** your database connection is working
3. **Run the processor**:
   ```bash
   cd feature_ingestion/app
   python ingest.py
   ```

Watch as your Excel data gets transformed into a queryable database table.

### Asking Questions About Your Data

1. **Open the AI interface**:
   ```bash
   cd queryGeneration
   jupyter notebook sql_query.ipynb
   ```

2. **Connect to your data**:
   - Point it to your database
   - Tell it which table to analyze

3. **Start asking questions**:
   - "What are the top 5 categories by sales?"
   - "Show me trends from the last quarter"
   - "Which products are underperforming?"

The model will analyze your data and give you intelligent, contextual answers.

## What Makes This Special

**Smart Processing** → Handles messy Excel files and creates clean database structures

**Natural Language Queries** → No need to write SQL. Just ask questions like you're talking to a colleague

**Flexible Database Support** → Works with PostgreSQL, MySQL, and can be extended to others

**Containerized Deployment** → Docker makes setup painless across different environments

**Interactive Analysis** → Jupyter notebooks provide a familiar interface for data exploration

## Real-World Example

Let's say you have a sales report in Excel:

1. **Before**: Manually sorting through rows, creating pivot tables, struggling with complex formulas
2. **After**: "Hey, what were our best-selling products last month?" → Get instant insights with charts and explanations

## What Makes This Special

**Smart Processing** → Handles messy Excel files and creates clean database structures

**Natural Language Queries** → No need to write SQL. Just ask questions like you're talking to a colleague

**Flexible Database Support** → Works with PostgreSQL, MySQL, and can be extended to others

**Containerized Deployment** → Docker makes setup painless across different environments

**Interactive Analysis** → Jupyter notebooks provide a familiar interface for data exploration

## Real-World Example

Let's say you have a sales report in Excel:

1. **Before**: Manually sorting through rows, creating pivot tables, struggling with complex formulas
2. **After**: "Hey, what were our best-selling products last month?" → Get instant insights with charts and explanations

## Contributing

Found a bug? Have an idea? Contributions are welcome. This project grows better with community input.

## Database Configuration

Your `.env` file should look something like this:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_database
DB_USER=your_username
DB_PASSWORD=your_password
DB_TYPE=postgresql  # or mysql
```

## Troubleshooting

**Can't connect to database?** → Check your `.env` file and ensure your database is running

**Excel file not processing?** → Make sure the file isn't password-protected and has clear headers

**AI giving weird answers?** → Verify your table name is correct in the notebook configuration

---

*Built for intelligent data analysis and insights.*

## Troubleshooting

**Can't connect to database?** → Check your `.env` file and ensure your database is running

**Excel file not processing?** → Make sure the file isn't password-protected and has clear headers

**AI giving weird answers?** → Verify your table name is correct in the notebook configuration

---


