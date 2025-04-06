from app.models.TradeLog import TradeLog
import pandas as pd
import numpy as np

def calculate_pnl(initial_capital: float, trade_logs: list[TradeLog]) -> float:
    current_capital = initial_capital
    holdings = {}  # Dictionary to track holdings per ticker

    for trade in trade_logs:
        if trade.action == 'BUY':
            current_capital -= trade.price * trade.shares

            if trade.ticker in holdings:
                holdings[trade.ticker] += trade.shares
            else:
                holdings[trade.ticker] = trade.shares

        elif trade.action == 'SELL':
            if trade.ticker in holdings:
                sell_amount = trade.shares * trade.price
                holdings[trade.ticker] -= trade.shares
                current_capital += sell_amount
            else:
                print(f"No sufficient holdings found for {trade.ticker} to sell")

        else:
            print(f"Unexpected action type: {trade.action}")
    
    pnl = current_capital - initial_capital
    return pnl

def calculate_returns(initial_capital: float, trade_logs: list[TradeLog]) -> pd.DataFrame:
    """
    Calculate cumulative returns and daily changes from trade logs and return as DataFrame.
    
    Args:
        initial_capital: Initial investment amount
        trade_logs: List of trade log entries
    
    Returns:
        DataFrame with columns: 'cumulative_return', 'daily_change'
    """
    # Sort trade logs by date
    sorted_trades = sorted(trade_logs, key=lambda x: x.report_date)
    
    current_capital = initial_capital
    holdings = {}  # Dictionary to track holdings per ticker
    data = []  # List to store daily data
    previous_return = 0
    
    for trade in sorted_trades:
        date_key = trade.report_date
        
        # Process trade
        if trade.action == 'BUY':
            current_capital -= trade.price * trade.shares
            
            if trade.ticker in holdings:
                holdings[trade.ticker] += trade.shares
            else:
                holdings[trade.ticker] = trade.shares
                
        elif trade.action == 'SELL':
            if trade.ticker in holdings:
                sell_amount = trade.shares * trade.price
                holdings[trade.ticker] -= trade.shares
                current_capital += sell_amount
            else:
                print(f"No sufficient holdings found for {trade.ticker} to sell")
        
        # Calculate returns
        cumulative_return = ((current_capital - initial_capital) / initial_capital) * 100
        daily_change = cumulative_return - previous_return
        
        # Store daily data
        data.append({
            'date': date_key,
            'cumulative_return': cumulative_return,
            'daily_change': daily_change,
            'capital': current_capital
        })
        
        previous_return = cumulative_return
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Set date as index
    df.set_index('date', inplace=True)
    
    # Remove duplicate dates, keeping the last entry for each date
    df = df[~df.index.duplicated(keep='last')]
    
    return df

def calculate_max_drawdown(cumulative_returns):
    # Calculate cumulative returns
    peak = cumulative_returns[0]
    max_drawdown = 0
    
    for ret in cumulative_returns:
        if peak != 0:  # Check to prevent division by zero
            if ret > peak:
                peak = ret
            drawdown = (peak - ret) / peak
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        else:
            peak = ret  # Update the peak only if it's initially zero

    return max_drawdown

def calculate_sharpe_ratio(returns, risk_free_rate=0):
    # Calculate the Sharpe Ratio
    excess_returns = returns - risk_free_rate
    sharpe_ratio = np.mean(excess_returns) / np.std(excess_returns)
    return sharpe_ratio * np.sqrt(len(returns))  # Annualized

def calculate_downside_deviation(returns, MAR=0):
    """
    Calculate downside deviation of returns
    
    Parameters:
    returns (numpy.array): Array of returns
    MAR (float): Minimum Acceptable Return, defaults to 0
    
    Returns:
    float: Downside deviation
    """
    # Calculate negative deviations from MAR
    negative_deviations = np.minimum(returns - MAR, 0)
    
    # Square the deviations and take the mean
    squared_downside = np.square(negative_deviations)
    mean_squared_downside = np.mean(squared_downside)
    
    # Take the square root to get downside deviation
    downside_deviation = np.sqrt(mean_squared_downside)
    
    return downside_deviation