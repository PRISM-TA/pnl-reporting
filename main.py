from app.db.session import create_db_session
from app.pnl.PnLReporting import calculate_downside_deviation
from app.analysis.CumRetAnalysis import CumRetAnalysis, CumRetAnalysisParam
from app.datafeed.DataFeeder import DataFeeder
from app.datafeed.TradeLogger import TradeLogger

from dotenv import load_dotenv
import os
import pandas as pd
from datetime import datetime

model = "MLPv2"
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
strategy_target = "RouletteStrategy_Confident"
strategy_benchmark = "BuyAndHoldStrategy"

header = "{:<10} | {:<12} | {:<15}".format(
    "Ticker", 
    "Benchmark Drawdown Dev. (%)",
    "Target Drawdown Dev. (%)"
)
print(header)

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

    # Calculate Downside Deviation
    benchmark_downside_deviation = calculate_downside_deviation(df['benchmark_return_change_pct'].values)
    target_downside_deviation = calculate_downside_deviation(df['target_return_change_pct'].values)

    # # Calculate Maximum Drawdown
    # benchmark_max_drawdown = calculate_max_drawdown(df['benchmark_cum_return_pct'].values)
    # target_max_drawdown = calculate_max_drawdown(df['target_cum_return_pct'].values)
    
    # # Calculate Sharpe Ratio
    # benchmark_sharpe_ratio = calculate_sharpe_ratio(
    #     df['benchmark_return_change_pct'].values, 0.0425
    # )
    # target_sharpe_ratio = calculate_sharpe_ratio(
    #     df['target_return_change_pct'].values, 0.0425
    # )


    print(f"{ticker:<10} | {benchmark_downside_deviation:<12} | {target_downside_deviation:<15}")
    