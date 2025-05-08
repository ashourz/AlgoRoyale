from algo_royale.for_your_eyes_only.backtest_visualizer import BacktestVisualizer
from algo_royale.for_your_eyes_only.config.config import load_config
import streamlit as st
from pathlib import Path
import pandas as pd
import os

class BacktestDashboard:
    def __init__(self):
        self.config = load_config()
        self.results_dir = Path(self.config["results_dir"])
        self.available_files = self._find_result_files()
        self.visualizer = None
        self.selected_strategies = []
        self.selected_symbols = []
        self.file_groups = {}
        self.selected_strategy = None
        self.selected_symbol = None

        print(f"Searching for results in: {self.results_dir.absolute()}")
        print(f"Found {len(self.available_files)} files in subdirectories")
        for f in self.available_files[:3]:
            print(f"Sample file: {f}")
        if len(self.available_files) > 3:
            print(f"...and {len(self.available_files)-3} more")
    
    def _find_result_files(self):
        """Find all CSV result files in strategy/symbol subdirectories"""
        result_files = []
        
        for strategy_dir in self.results_dir.glob("*"):
            if strategy_dir.is_dir():
                for symbol_dir in strategy_dir.glob("*"):
                    if symbol_dir.is_dir():
                        for csv_file in symbol_dir.glob("*.csv"):
                            result_files.append(csv_file)
        
        if not result_files:
            print(f"No CSV files found in {self.results_dir}/*/*/")
            print(f"Directory structure should be: {self.results_dir}/strategy/symbol/files.csv")
        
        return result_files

    def _load_selected_file(self, file_path):
        """Load file and extract strategy/symbol from path"""
        try:
            parts = file_path.parts
            strategy_name = parts[-3]
            symbol_name = parts[-2]
            
            df = pd.read_csv(file_path, parse_dates=['timestamp'])
            
            if 'strategy' not in df.columns:
                df['strategy'] = strategy_name
            if 'symbol' not in df.columns:
                df['symbol'] = symbol_name
                
            self.visualizer = BacktestVisualizer(data=df)
            return True
            
        except Exception as e:
            st.error(f"Error loading {file_path.name}: {str(e)}")
            return False

    def run(self):
        """Main entry point with corrected layout"""
        self._build_file_hierarchy()
        
        # Sidebar - ONLY for controls/selection
        with st.sidebar:
            st.header("Data Selection")
            
            if not self.available_files:
                st.error("No result files found!")
                return
                
            self.selected_strategy = st.selectbox(
                "Select Strategy",
                options=list(self.file_groups.keys())
            )
            
            if self.selected_strategy:
                self.selected_symbol = st.selectbox(
                    "Select Symbol",
                    options=list(self.file_groups[self.selected_strategy].keys())
                )
                
                if self.selected_symbol:
                    selected_file = self.file_groups[self.selected_strategy][self.selected_symbol]
                    
                    if st.button("Load Results"):
                        if self._load_selected_file(selected_file):
                            st.success("Results loaded!")
                            self._update_selections_from_data()
        
        # Main area - ONLY for visualizations/results
        if hasattr(self, 'visualizer') and self.visualizer is not None:
            self._display_main_content()

    def _display_main_content(self):
        """Display all visualizations in main area"""
        st.title("Backtest Analysis Dashboard")
        
        tab1, tab2, tab3 = st.tabs(["📊 Overview", "📈 Performance", "🔍 Trade Analysis"])

        with tab1:
            self._show_overview()

        with tab2:
            self._show_performance()

        with tab3:
            self._show_trade_analysis()

    def _build_file_hierarchy(self):
        """Organize files by strategy/symbol"""
        self.file_groups = {}
        for f in self.available_files:
            parts = f.parts
            strategy = parts[-3]
            symbol = parts[-2]
            
            if strategy not in self.file_groups:
                self.file_groups[strategy] = {}
            self.file_groups[strategy][symbol] = f

    def _update_selections_from_data(self):
        """Update selections based on loaded data"""
        if self.visualizer and hasattr(self.visualizer, 'data'):
            df = self.visualizer.data
            self.selected_strategies = df['strategy'].unique().tolist()
            self.selected_symbols = df['symbol'].unique().tolist()

    def _display_dashboard(self):  # Now only called after successful load
        tab1, tab2, tab3 = st.tabs(["📊 Overview", "📈 Performance", "🔍 Trade Analysis"])

        with tab1:
            self._show_overview()

        with tab2:
            self._show_performance()

        with tab3:
            self._show_trade_analysis()

    def _show_overview(self):
        st.header("Strategy Overview")
        
        if not self.selected_strategies:
            st.warning("No strategies loaded yet")
            return
            
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Strategies Loaded", len(self.selected_strategies))
        with col2:
            st.metric("Symbols Loaded", len(self.selected_symbols))
        with col3:
            total_trades = self.visualizer.data['signal'].count() if hasattr(self.visualizer, 'data') else 0
            st.metric("Total Trades", total_trades)

    def _show_performance(self):
        st.header("Performance Analysis")
        
        if hasattr(self.visualizer, 'data'):
            fig = self.visualizer.plot_equity_curve(
                strategies=self.selected_strategies,
                symbols=self.selected_symbols
            )
            st.plotly_chart(fig, use_container_width=True)

            fig = self.visualizer.plot_drawdown(
                strategies=self.selected_strategies,
                symbols=self.selected_symbols
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No data loaded to display performance")

    def _show_trade_analysis(self):
        st.header("Trade Analysis")
        
        if hasattr(self.visualizer, 'data'):
            strategy = st.selectbox("Select Strategy", self.selected_strategies, key="trade_strategy")
            symbol = st.selectbox("Select Symbol", self.selected_symbols, key="trade_symbol")
            
            fig = self.visualizer.plot_trades(
                symbol=symbol,
                strategy=strategy,
                days=7
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No data loaded to analyze trades")

def main():
    st.set_page_config(
        layout="wide",
        page_title="AlgoRoyale Backtest Analyzer",
        initial_sidebar_state="expanded"
    )
    dashboard = BacktestDashboard()
    dashboard.run()

if __name__ == "__main__":
    main()