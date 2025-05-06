# Airbnb Revenue Dashboard

**Airbnb Revenue Dashboard** is an interactive Streamlit application that helps Airbnb hosts visualize and analyze their pending reservation earnings. The dashboard provides:
- An at-a-glance view of total upcoming gross revenue and monthly revenue trends.
- Automatic detection of potential duplicate bookings.
- Support for both English and French CSV exports.
- Lead-time analysis showing how many days in advance guests book.

## Features

- **KPI Dashboard**: View total gross revenue and key booking metrics.
- **Deduplication**: Flags duplicate reservation records by confirmation code.
- **Language Support**: Parse and display CSV exports in English or French; toggle UI language in the sidebar.
- **Lead-Time Analysis**: Distribution charts of booking lead times.

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/gonzague/Airbnb-Revenue-Dashboard.git
   cd Airbnb-Revenue-Dashboard
   ```
2. **Create and activate a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate    # on macOS/Linux
   .\venv\Scripts\activate   # on Windows
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Export your pending revenues CSV**  
   From your Airbnb host dashboard, download the “Pending revenues” CSV (see Airbnb’s instructions: https://www.airbnb.fr/help/article/3632).

2. **Run the Streamlit app**:
   ```bash
   streamlit run streamlit_airbnb_dashboard.py
   ```
   This will open the dashboard in your default browser.

3. **Upload your CSV**  
   Use the file uploader in the app to select `airbnb_pending.csv` (or your export). The dashboard will parse and display your data.

4. **Explore**  
   - Toggle language (English/French) in the sidebar.  
   - View KPIs, monthly revenue charts, lead-time distribution, and potential duplicates.


## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests. Please ensure code follows the project style and includes tests for new functionality.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.