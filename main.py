from app.db.session import create_db_session
from app.analysis.CumRetAnalysis import CumRetAnalysis, CumRetAnalysisParam
from app.datafeed.DataFeeder import DataFeeder
from app.datafeed.TradeLogger import TradeLogger

from dotenv import load_dotenv
import os
import pandas as pd
from datetime import datetime

model = "CNNv0"
feature_set = "processed technical indicators (20 days)"

load_dotenv()
session = create_db_session(
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
    port=os.getenv("DB_PORT")
)

feeder = DataFeeder(session)
trade_logger = TradeLogger(session)
strategy_target = "RouletteStrategy"
strategy_benchmark = "BuyAndHoldStrategy"

# Initialize results storage
results = []

for ticker in ["AAPL", "AXP", "BA", "CAT", "CSCO", "CVX", "DD", "DIS", "GE", "HD", "IBM", "INTC", "JNJ", "JPM", "KO", "MCD", "MMM", "MRK", "MSFT", "NKE", "PFE", "PG", "TRV", "UNH", "UTX", "VZ", "WMT", "XOM"]:
    # Initialize analyzer
    analyzer = CumRetAnalysis(feeder, trade_logger)
    analyzer.setParam(
        CumRetAnalysisParam(
            benchmark_strategy=strategy_benchmark,
            benchmark_initial_capital=10000,
            target_strategy=strategy_target,
            target_initial_capital=10000,
            classifier_model=model,
            feature_set=feature_set,
            ticker=ticker
        )
    )
    
    # Run analysis
    df = analyzer.run()
    df.to_csv(f"{ticker}.csv")