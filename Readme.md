# Masters: Sheriff Spider Project

A Scrapy-based web scraping project that collects sheriff sale data from [salesweb.civilview.com](https://salesweb.civilview.com/). The **sheriffspider** uses [Scrapy Playwright](https://github.com/scrapy-plugins/scrapy-playwright) to handle JavaScript rendering and navigates through county listings to extract detailed property information. The data is cleaned and validated by the **MastersPipeline**, then saved to a **PostgreSQL** database (via the **SaveToPostgresPipeline**, which can be enabled or disabled).

## Table of Contents

1. [Project Structure](#project-structure)
2. [Key Features](#key-features)
3. [Dependencies and Installation](#dependencies-and-installation)
4. [How to Run](#how-to-run)
5. [Database Integration](#database-integration)
6. [Extending or Reusing This Project](#extending-or-reusing-this-project)
7. [Contributing](#contributing)
8. [License](#license)

---

## Project Structure


- **`sheriffspider.py`**: The main spider that starts at `salesweb.civilview.com`, navigates to specific counties, follows property links, and extracts key property details.
- **`items.py`**: Defines the data structure (`SheriffPropertyItem`) for scraped data.
- **`pipelines.py`**: Contains:
    - **MastersPipeline**: Cleans and processes data (e.g., parsing amounts, cleaning up fields).
    - **SaveToPostgresPipeline**: Inserts property data into a PostgreSQL database.
- **`settings.py`**: Configures Scrapy, Playwright, concurrency, and item pipelines.

---

## Key Features

1. **JavaScript Rendering**: Uses [Playwright](https://playwright.dev/) through Scrapy to handle dynamic content.
2. **Item Pipeline**: Cleans and normalizes scraped data (addresses, monetary values, dates).
3. **PostgreSQL Integration**: Directly saves the data to a table (`sheriff_property`) and its related `status_history` table.
4. **Robust Logging**: Outputs warnings and debug info if certain fields are missing or malformed.
5. **Configurable**: Adjust concurrency, retries, cookies, and more via `settings.py`.

---

## Dependencies and Installation

1. **Python & Conda**:
    - Recommended to use a Conda environment for consistent package versions.
    - Alternatively, you can use `virtualenv` + `pip`.

1. **Scrapy**
    - `pip install scrapy` or install via Conda.

1. **Scrapy Playwright**
    - `pip install scrapy-playwright`
    - Also install the Playwright browsers

1. **PostgreSQL**
    - Make sure PostgreSQL is installed and running if you intend to use the `SaveToPostgresPipeline`.
    - `pip install psycopg2` or `pip install psycopg2-binary` (depending on your setup).

1. **Other Requirements**
    - Your environment might include additional libraries like `requests`, `lxml`, `pandas`, etc.
    - See your `requirements.txt` or `environment.yml` for a full list.

## How to Run

1. **Activate your environment** (e.g., `conda activate sheriffspider`).
2. **Run the spider**:
    `scrapy crawl sheriffspider`
3. **Monitor logs**:
    - Scrapy will display info or warnings in your console.
    - Look for “Spider closed” message when it's finished.

---

## Database Integration

- The `SaveToPostgresPipeline` is **uncommented** in `settings.py`, meaning it’s **enabled** and ready to insert data into the database.
- Update your database credentials in the pipeline code (`SaveToPostgresPipeline.__init__()`), or set them as environment variables.
- The pipeline automatically creates two tables if they don’t exist:
    - **`sheriff_property`**: Main property data (address, sale date, etc.)
    - **`status_history`**: Changes in status for each property (inserted as separate rows).

---

## Extending or Reusing This Project

This project can be adapted for **any** dynamic web scraping task requiring:

- **Playwright** for modern JavaScript-heavy sites.
- **Structured Database Storage** for large amounts of data.

**Possible use cases**:

- **Real Estate & Property Data**: Expand to other county listings or real-estate-focused sites.
- **Automated Data Pipelines**: Integrate the spider with ETL flows (e.g., Airflow, Luigi) to schedule recurring data collection.
- **Data Analysis & Reporting**: Once data is in PostgreSQL (or another DB), connect your favorite BI tools (Tableau, Power BI) or scripts for deeper analysis.
- **Machine Learning**: Train property-price prediction models by combining these scraped properties with external datasets (demographics, economic indicators, etc.).