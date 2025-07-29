# Query Based Reports

A data ingestion and analysis system that processes Excel files and similar data formats, stores them in SQL databases, and provides AI-powered querying capabilities for intelligent data insights.

## 🎯 Project Overview

This project enables automated data processing and intelligent querying through a two-stage pipeline:

1. **Data Ingestion**: Processes Excel files and stores structured data in SQL database tables
2. **AI-Powered Analysis**: Uses Generative AI API models to analyze stored data and answer queries

## 🏗️ Architecture

```
DataRetrievalintoSQL/
├── DATA/                          # Data storage directory
├── feature_ingestion/             # Data ingestion service
│   ├── app/
│   │   ├── venv/                  # Virtual environment
│   │   ├── ingest.py              # Main ingestion script
│   │   ├── requirements.txt       # Python dependencies
│   │   └── [data files]           # Excel files to be processed
│   ├── .env                       # Environment configuration
│   └── docker-compose.yml         # Docker configuration
├── queryGeneration/               # AI query interface
│   └── sql_query.ipynb           # Jupyter notebook for AI queries
└── README.md
```

## 🛠️ Technologies Used

### Core Libraries
- **pandas** - Data manipulation and analysis
- **sqlalchemy** - SQL toolkit and ORM
- **openpyxl** - Excel file processing
- **psycopg2-binary** - PostgreSQL adapter
- **python-dotenv** - Environment variable management
- **pymysql** - MySQL database connector

### Infrastructure
- **Docker** - Containerized deployment
- **SQL Database** - Data storage (PostgreSQL/MySQL)
- **Jupyter Notebooks** - Interactive analysis interface
- **Generative AI API(GEMINI Currently)** - Intelligent query processing

## 🚀 Getting Started

### Prerequisites
- Docker and Docker Compose
- Python 3.x
- SQL Database (PostgreSQL or MySQL)

### Installation & Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd DataRetrievalintoSQL
   ```

2. **Configure environment**
   ```bash
   cd feature_ingestion
   # Edit .env file with your database credentials
   ```

3. **Start the ingestion service**
   ```bash
   docker-compose up
   ```

## 📊 Usage Workflow

### Step 1: Data Ingestion

1. **Prepare your data file**
   - Place your Excel file in `/feature_ingestion/app/` directory
   - Ensure SQL database connection is properly configured

2. **Run the ingestion process**
   ```bash
   cd feature_ingestion/app
   python ingest.py
   ```
   
   This will:
   - Process the Excel file
   - Create a dedicated table for the file
   - Store structured data with proper column mapping


### Step 2: AI-Powered Analysis

1. **Open the query interface**
   ```bash
   cd queryGeneration
   jupyter notebook sql_query.ipynb
   ```

2. **Configure the notebook**
   - Set the correct database connection path
   - Specify the target table name
   - Run the notebook cells

3. **Query your data**
   - Ask questions about your data in natural language
   - Get AI-generated summaries and insights
   - Receive intelligent answers based on your dataset

## 💡 Key Features

- **Multi-format Support**: Handles Excel files and similar data formats
- **AutomateA
