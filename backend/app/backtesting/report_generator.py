"""Report generator for backtest results."""

import json
from typing import Dict, Any
from datetime import datetime
from pathlib import Path


class ReportGenerator:
    """Generate HTML/PDF reports from backtest results."""
    
    @staticmethod
    def generate_html_report(results: Dict[str, Any], output_path: str = "backtest_report.html") -> str:
        """
        Generate HTML report from backtest results.
        
        Args:
            results: Backtest results dictionary
            output_path: Output file path
        
        Returns:
            Path to generated report
        """
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Backtest Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }}
        h1 {{ color: #333; }}
        h2 {{ color: #666; border-bottom: 2px solid #ddd; padding-bottom: 10px; }}
        .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }}
        .metric-card {{ background: #f9f9f9; padding: 15px; border-radius: 5px; border-left: 4px solid #4CAF50; }}
        .metric-label {{ font-size: 12px; color: #666; text-transform: uppercase; }}
        .metric-value {{ font-size: 24px; font-weight: bold; color: #333; margin-top: 5px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #4CAF50; color: white; }}
        .positive {{ color: #4CAF50; }}
        .negative {{ color: #f44336; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Backtest Report</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <h2>Performance Summary</h2>
        <div class="metrics">
            <div class="metric-card">
                <div class="metric-label">Total Return</div>
                <div class="metric-value {'positive' if results.get('total_return', 0) > 0 else 'negative'}">
                    {results.get('total_return', 0):.2f}%
                </div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Sharpe Ratio</div>
                <div class="metric-value">{results.get('sharpe_ratio', 0):.2f}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Max Drawdown</div>
                <div class="metric-value negative">{results.get('max_drawdown', 0):.2f}%</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Win Rate</div>
                <div class="metric-value">{results.get('win_rate', 0):.2f}%</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Total Trades</div>
                <div class="metric-value">{results.get('total_trades', 0)}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Profit Factor</div>
                <div class="metric-value">{results.get('profit_factor', 0):.2f}</div>
            </div>
        </div>
        
        <h2>Trade Statistics</h2>
        <table>
            <tr>
                <th>Metric</th>
                <th>Value</th>
            </tr>
            <tr><td>Average Win</td><td>${results.get('avg_win', 0):.2f}</td></tr>
            <tr><td>Average Loss</td><td>${results.get('avg_loss', 0):.2f}</td></tr>
            <tr><td>Largest Win</td><td>${results.get('largest_win', 0):.2f}</td></tr>
            <tr><td>Largest Loss</td><td>${results.get('largest_loss', 0):.2f}</td></tr>
            <tr><td>Expectancy</td><td>${results.get('expectancy', 0):.2f}</td></tr>
        </table>
        
        <h2>Risk Metrics</h2>
        <table>
            <tr>
                <th>Metric</th>
                <th>Value</th>
            </tr>
            <tr><td>Sortino Ratio</td><td>{results.get('sortino_ratio', 0):.2f}</td></tr>
            <tr><td>Calmar Ratio</td><td>{results.get('calmar_ratio', 0):.2f}</td></tr>
            <tr><td>Recovery Factor</td><td>{results.get('recovery_factor', 0):.2f}</td></tr>
            <tr><td>Longest Win Streak</td><td>{results.get('longest_win_streak', 0)}</td></tr>
            <tr><td>Longest Loss Streak</td><td>{results.get('longest_loss_streak', 0)}</td></tr>
        </table>
    </div>
</body>
</html>
"""
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(html)
        
        return output_path
    
    @staticmethod
    def generate_json_report(results: Dict[str, Any], output_path: str = "backtest_report.json") -> str:
        """
        Generate JSON report from backtest results.
        
        Args:
            results: Backtest results dictionary
            output_path: Output file path
        
        Returns:
            Path to generated report
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "results": results
        }
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        return output_path

