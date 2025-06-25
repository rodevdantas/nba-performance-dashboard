# 🏀 NBA Data Analysis Dashboard 📊

## Project Overview

This project represents a complete immersion into my two passions: sports and technology. Driven by the fascination of transforming raw data into actionable insights, I built an **ETL (Extract, Transform, Load) data pipeline**, resulting in an interactive Dashboard for in-depth exploration of athlete performance per season.

The main goal was to demonstrate the ability to build an end-to-end data solution, from automated data collection to interactive visualization, applying good data engineering and critical analysis practices.

## Project Goals

* **Build a Robust ETL Pipeline:** Automate the process of collecting (Extract), cleaning and enriching (Transform), and loading (Load) NBA data into a relational database.

* **Data Modeling and Organization:** Design and implement a database schema in MySQL, utilizing an Object-Relational Mapper (ORM) to ensure data consistency and scalability.

* **Data Analysis and Insight Generation:** Perform analyses in SQL, using Window Functions, to identify performance evolution patterns of players across seasons.

* **Interactive Data Visualization:** Develop a dynamic and user-friendly dashboard, allowing users to explore player statistics, rankings, and relationships between metrics per season.

* **Apply Best Practices:** Incorporate code modularization, secure environment variable management (`.env`), version control, and caching strategies to optimize performance and maintainability.

## Technologies and Libraries Used

* **Python:** Main programming language for all pipeline stages and dashboard development.

* **Pandas:** For data manipulation, cleaning, transformation, and enrichment.

* **nba_api:** Library used to extract raw player statistics data from the unofficial NBA API.

* **MySQL:** Used for persistent and organized storage of transformed data.

* **SQLAlchemy:** Library that allowed for robust, scalable, and object-oriented interaction with the MySQL database, facilitating modeling and load/query operations.

* **PyMySQL:** Python driver for MySQL, used by SQLAlchemy to establish the database connection.

* **Streamlit:** Open-source Python framework for rapidly creating interactive web applications and dashboards, making insights accessible through a user-friendly interface.

* **Plotly:** Visualization library that generates interactive and aesthetically pleasing charts, integrated with Streamlit.

* **python-dotenv:** Library for securely loading environment variables from `.env` files, protecting sensitive credentials.

* **pathlib:** Python module for object-oriented manipulation of file and directory paths, ensuring portability across operating systems.

* **os / sys:** Modules for interacting with the operating system, including manipulating `sys.path` to ensure recognition of internal project packages.

## Project Structure

The project organization follows a modular and scalable structure:

• `nba-performance-dashboard/`
  • `.env`
  • `.gitignore`
  • `README.md`
  • `requirements.txt`
  • `src/`
    • `__init__.py`
    • `etl/`
      • `__init__.py`
      • `extract.py`
      • `transform.py`
      • `load.py`
    • `dashboard/`
      • `__init__.py`
      • `app.py`
      • `db_setup.py`
  • `data/`
    • `raw/`
      • `nba_stats_brutas.csv`
    • `processed/`
      • `nba_stats_transformadas.csv`

## Analyses and Insights Generated

The dashboard offers various perspectives on NBA player performance:

1.  **Player Performance Evolution Across Consecutive Seasons:**
    The analysis uses **Window Functions (`LAG()`) in SQL** to calculate the difference in points, assists, and rebounds between consecutive seasons for each player. Crucially, to avoid distortions, **only players with a minimum of 50 games played in *both* compared seasons** were considered. This ensures that "evolution" is representative of consistent performance.

    * Insight: Helps identify a player's ascension moment and the positive impact they might have generated for their teams, highlighting the value of their performance.

2.  **Detailed Seasonal Analysis:**
    The dashboard allows the user to select a specific season via a dropdown.

    * Top N Players by Metric: Displays a ranking of top players by points per game, assists per game, and rebounds per game for the selected season. The number of players in the ranking can be adjusted using a slider.

    * Aggregated Statistics: Presents the average and standard deviation of points, assists, and rebounds per game for all players in the selected season. This "per player" metric (e.g., "Average Points per Game (per player)") helps understand the distribution and variability of individual performance in the league. An expandable section explains the meaning and importance of Standard Deviation.

    * Relationship between Points and Assists: A Scatter Plot shows the correlation between Points per Game and Assists per Game for the selected season. The size of the points on the graph represents the number of games played by the athlete, adding visual context to the performance.

## Important Notes, Challenges, and Learnings

This project was a journey of continuous learning and overcoming practical challenges, reflecting the daily life of a data professional:

* **Modularization and Project Architecture:** The transition from isolated scripts to a modular folder structure (`src/`, `etl/`, `dashboard/`) required a deep understanding of how Python manages **packages and modules (with `__init__.py`)** and how to manipulate `sys.path` to ensure imports work correctly from any execution point. This was one of the biggest technical challenges and learnings.

* **Centralization of Database Configuration (`db_setup.py`):** The decision to isolate ORM definitions (data models) and database connection configuration in a dedicated module (`db_setup.py`) was fundamental to avoid code duplication and optimize project maintainability and scalability.

* **Optimization in SQL Analysis:** The experience with `nba_api` and the need to filter "noise" in the data (such as cases of players with atypical seasons due to injuries) reinforced the importance of critical thinking and applying business logic in SQL to generate **truly useful and representative insights**, not just numbers.

* **Interface Design and Customization (`Streamlit` and `CSS`):** Developing the dashboard in Streamlit was a significant leap, allowing me to create interactive web interfaces with Python. Furthermore, enhancing the visual design required the use of **injected CSS** via `st.markdown`, expanding my skills in Front-End development with Python – an unexpected and valuable learning experience.

* **Debugging Process:** The persistence in solving errors (like `ModuleNotFoundError` which challenged the understanding of package architecture) solidified my debugging skills and technical resilience.

This project represents the practical consolidation of skills in SQL, Python, data modeling, data engineering (ETL), and visualization, with special attention to code clarity, reproducibility, and insight communication. I continue in constant evolution and am very proud of this delivery!

## How to Run the Project

To run this project locally, follow the steps below:

1.  **Clone the Repository:**
    ```bash
    git clone [YOUR_GITHUB_LINK_HERE]
    cd nba-performance-dashboard
    ```

2.  **Create and Activate a Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    # On Windows:
    .\venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **MySQL Database Configuration:**
    * Open your MySQL client (e.g., MySQL Workbench).
    * Connect to your server.
    * Execute the following SQL commands to create the database and user (if you haven't already):
        ```sql
        CREATE DATABASE IF NOT EXISTS nba_data_warehouse;
        CREATE USER IF NOT EXISTS 'nba_user'@'localhost' IDENTIFIED BY 'safe_password_example'; -- Replace with your password
        GRANT ALL PRIVILEGES ON nba_data_warehouse.* TO 'nba_user'@'localhost';
        FLUSH PRIVILEGES;
        ```
    * Create the tables in the correct order (first `jogadores`, then `estatisticas_temporada`):
        ```sql
        USE nba_data_warehouse;

        CREATE TABLE IF NOT EXISTS jogadores (
            id_jogador INT PRIMARY KEY,
            nome_jogador VARCHAR(300) NOT NULL
        );

        CREATE TABLE IF NOT EXISTS estatisticas_temporada (
            id_estatistica INT AUTO_INCREMENT PRIMARY KEY,
            id_jogador INT NOT NULL,
            temporada VARCHAR(10) NOT NULL,
            id_time INT NOT NULL,
            sigla_time VARCHAR(10),
            jogos_jogados INT NOT NULL,
            pontos INT NOT NULL,
            assistencias INT NOT NULL,
            rebotes INT NOT NULL,
            perc_arremessos_quadra DECIMAL(5,3) NOT NULL,
            perc_arremessos_3pts DECIMAL(5,3) NOT NULL,
            perc_lances_livres DECIMAL(5,3) NOT NULL,
            CONSTRAINT fk_jogador_stats
                FOREIGN KEY (id_jogador)
                REFERENCES jogadores(id_jogador)
                ON DELETE CASCADE
        );
        ```

5.  **Create the `.env` File:**
    * In the **root of your project** (`nba-performance-dashboard/`), create a file named `.env`.
    * Add your database credentials:
        ```
        DB_HOST=localhost
        DB_NAME=nba_data_warehouse
        DB_USER=nba_user
        DB_PASSWORD=safe_password_example # Use the password you defined in MySQL
        ```

6.  **Execute the ETL Pipeline (Sequentially from the Project Root):**
    * Ensure you are in the **root of the project** (`nba-performance-dashboard/`) in your terminal.
    * Execute each script in order:
        ```bash
        python src/etl/extract.py
        python src/etl/transform.py
        python src/etl/load.py
        ```
        *(Note: `extract.py` may take a few minutes to complete, due to API data collection. Please be patient.)*

7.  **Start the Streamlit Dashboard:**
    * Still in the **root of the project** (`nba-performance-dashboard/`) in your terminal.
    * ```bash
        streamlit run src/dashboard/app.py
        ```
    * This will open the dashboard automatically in your browser. If it doesn't update with the latest data, click the "hamburger" icon in the top right corner of the dashboard and select "Clear cache".

## Contribution

Feel free to explore the code, suggest improvements, or report issues. All contributions are welcome!



