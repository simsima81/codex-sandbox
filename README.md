# CANSLIM Stock Screener

This project provides a simple command line interface to screen U.S. stocks using
the CANSLIM methodology powered by the Financial Modeling Prep Ultimate API.

## Setup

1. Create a `.env` file in the project root containing your API key.

   ```env
   FMP_KEY=YOUR_FMP_KEY
   ```

2. Install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the screener:

   ```bash
   python src/canslim.py
   ```

The program prints the passing tickers and their key metrics and also saves a
timestamped CSV named `canslim_YYYYMMDD_HHMMSS.csv` in the project root.

![console screenshot](docs/screenshot.png)

You can view an example CSV at [`docs/sample.csv`](docs/sample.csv).
