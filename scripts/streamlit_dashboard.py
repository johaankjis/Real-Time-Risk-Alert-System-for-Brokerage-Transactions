"""
Real-Time Risk Alert Dashboard
Interactive Streamlit dashboard for monitoring risk metrics and alerts
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
from database_config import get_db_connection

# Page configuration
st.set_page_config(
    page_title="Risk Alert Dashboard",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .alert-critical {
        background-color: #ff4444;
        color: white;
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
    }
    .alert-high {
        background-color: #ff8800;
        color: white;
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
    }
    .alert-medium {
        background-color: #ffbb33;
        color: white;
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
    }
    .stMetric {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_database():
    """Get database connection (cached)"""
    return get_db_connection()


def fetch_data(query, params=None):
    """Fetch data from database"""
    db = get_database()
    try:
        with db.get_cursor() as cursor:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            results = cursor.fetchall()
            
            # Convert to list of dicts for pandas
            if db.db_type == 'sqlite':
                return [dict(row) for row in results]
            else:
                return results
    except Exception as e:
        st.error(f"Database error: {e}")
        return []


def get_summary_metrics():
    """Get summary metrics for dashboard"""
    # Total transactions
    total_tx = fetch_data("SELECT COUNT(*) as count FROM transactions")
    total_transactions = total_tx[0]['count'] if total_tx else 0
    
    # Total exposure
    total_exp = fetch_data("SELECT SUM(total_exposure) as total FROM client_exposures")
    total_exposure = float(total_exp[0]['total']) if total_exp and total_exp[0]['total'] else 0
    
    # Active alerts
    active_alerts = fetch_data("SELECT COUNT(*) as count FROM alerts WHERE acknowledged = FALSE")
    alert_count = active_alerts[0]['count'] if active_alerts else 0
    
    # High risk clients
    high_risk = fetch_data("SELECT COUNT(*) as count FROM client_exposures WHERE risk_level IN ('HIGH', 'CRITICAL')")
    high_risk_count = high_risk[0]['count'] if high_risk else 0
    
    return {
        'total_transactions': total_transactions,
        'total_exposure': total_exposure,
        'active_alerts': alert_count,
        'high_risk_clients': high_risk_count
    }


def get_recent_alerts(limit=10):
    """Get recent alerts"""
    query = """
        SELECT * FROM alerts 
        ORDER BY timestamp DESC 
        LIMIT ?
    """ if get_database().db_type == 'sqlite' else """
        SELECT * FROM alerts 
        ORDER BY timestamp DESC 
        LIMIT %s
    """
    
    return fetch_data(query, (limit,))


def get_client_exposures():
    """Get client exposure data"""
    return fetch_data("""
        SELECT client_id, total_exposure, position_count, risk_level, last_updated
        FROM client_exposures
        WHERE total_exposure > 0
        ORDER BY total_exposure DESC
    """)


def get_symbol_exposures():
    """Get symbol exposure data"""
    return fetch_data("""
        SELECT symbol, total_exposure, transaction_count, risk_level, last_updated
        FROM symbol_exposures
        WHERE total_exposure > 0
        ORDER BY total_exposure DESC
    """)


def get_transaction_history(hours=1):
    """Get recent transaction history"""
    db = get_database()
    cutoff = datetime.now() - timedelta(hours=hours)
    
    if db.db_type == 'sqlite':
        query = """
            SELECT * FROM transactions 
            WHERE timestamp > ?
            ORDER BY timestamp DESC
            LIMIT 100
        """
    else:
        query = """
            SELECT * FROM transactions 
            WHERE timestamp > %s
            ORDER BY timestamp DESC
            LIMIT 100
        """
    
    return fetch_data(query, (cutoff,))


def get_alert_statistics():
    """Get alert statistics by type and severity"""
    return fetch_data("""
        SELECT 
            alert_type,
            severity,
            COUNT(*) as count
        FROM alerts
        GROUP BY alert_type, severity
        ORDER BY count DESC
    """)


def render_summary_metrics():
    """Render summary metrics at the top"""
    metrics = get_summary_metrics()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Transactions",
            value=f"{metrics['total_transactions']:,}",
            delta=None
        )
    
    with col2:
        st.metric(
            label="Total Exposure",
            value=f"${metrics['total_exposure']:,.0f}",
            delta=None
        )
    
    with col3:
        st.metric(
            label="Active Alerts",
            value=metrics['active_alerts'],
            delta=None,
            delta_color="inverse"
        )
    
    with col4:
        st.metric(
            label="High Risk Clients",
            value=metrics['high_risk_clients'],
            delta=None,
            delta_color="inverse"
        )


def render_alerts_section():
    """Render recent alerts section"""
    st.subheader("Recent Alerts")
    
    alerts = get_recent_alerts(20)
    
    if not alerts:
        st.info("No alerts generated yet")
        return
    
    # Create DataFrame
    df_alerts = pd.DataFrame(alerts)
    
    # Display alerts with color coding
    for _, alert in df_alerts.iterrows():
        severity_class = f"alert-{alert['severity'].lower()}"
        
        with st.container():
            col1, col2, col3 = st.columns([2, 3, 1])
            
            with col1:
                st.markdown(f"**{alert['alert_type']}**")
                st.caption(f"{alert['timestamp']}")
            
            with col2:
                st.write(alert['message'])
            
            with col3:
                if alert['severity'] == 'CRITICAL':
                    st.error(alert['severity'])
                elif alert['severity'] == 'HIGH':
                    st.warning(alert['severity'])
                else:
                    st.info(alert['severity'])
            
            st.divider()


def render_exposure_charts():
    """Render exposure visualization charts"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Client Exposures")
        client_data = get_client_exposures()
        
        if client_data:
            df_clients = pd.DataFrame(client_data)
            
            # Top 10 clients by exposure
            df_top_clients = df_clients.head(10)
            
            fig = px.bar(
                df_top_clients,
                x='client_id',
                y='total_exposure',
                color='risk_level',
                color_discrete_map={
                    'LOW': '#28a745',
                    'MEDIUM': '#ffc107',
                    'HIGH': '#fd7e14',
                    'CRITICAL': '#dc3545'
                },
                title="Top 10 Clients by Exposure",
                labels={'total_exposure': 'Exposure ($)', 'client_id': 'Client ID'}
            )
            fig.update_layout(showlegend=True, height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            # Display table
            st.dataframe(
                df_clients[['client_id', 'total_exposure', 'position_count', 'risk_level']],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No client exposure data available")
    
    with col2:
        st.subheader("Symbol Exposures")
        symbol_data = get_symbol_exposures()
        
        if symbol_data:
            df_symbols = pd.DataFrame(symbol_data)
            
            # Top 10 symbols by exposure
            df_top_symbols = df_symbols.head(10)
            
            fig = px.bar(
                df_top_symbols,
                x='symbol',
                y='total_exposure',
                color='risk_level',
                color_discrete_map={
                    'LOW': '#28a745',
                    'MEDIUM': '#ffc107',
                    'HIGH': '#fd7e14',
                    'CRITICAL': '#dc3545'
                },
                title="Top 10 Symbols by Exposure",
                labels={'total_exposure': 'Exposure ($)', 'symbol': 'Symbol'}
            )
            fig.update_layout(showlegend=True, height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            # Display table
            st.dataframe(
                df_symbols[['symbol', 'total_exposure', 'transaction_count', 'risk_level']],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No symbol exposure data available")


def render_transaction_timeline():
    """Render transaction timeline"""
    st.subheader("Transaction Timeline (Last Hour)")
    
    transactions = get_transaction_history(hours=1)
    
    if not transactions:
        st.info("No recent transactions")
        return
    
    df_tx = pd.DataFrame(transactions)
    
    # Convert timestamp to datetime if needed
    if 'timestamp' in df_tx.columns:
        df_tx['timestamp'] = pd.to_datetime(df_tx['timestamp'])
    
    # Group by minute and count
    df_tx['minute'] = df_tx['timestamp'].dt.floor('1min')
    tx_per_minute = df_tx.groupby('minute').size().reset_index(name='count')
    
    # Create line chart
    fig = px.line(
        tx_per_minute,
        x='minute',
        y='count',
        title="Transactions per Minute",
        labels={'count': 'Transaction Count', 'minute': 'Time'}
    )
    fig.update_traces(line_color='#0066cc', line_width=2)
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)
    
    # Recent transactions table
    st.subheader("Recent Transactions")
    display_cols = ['timestamp', 'client_id', 'symbol', 'transaction_type', 'quantity', 'price', 'total_value']
    st.dataframe(
        df_tx[display_cols].head(20),
        use_container_width=True,
        hide_index=True
    )


def render_alert_statistics():
    """Render alert statistics"""
    st.subheader("Alert Statistics")
    
    alert_stats = get_alert_statistics()
    
    if not alert_stats:
        st.info("No alert statistics available")
        return
    
    df_stats = pd.DataFrame(alert_stats)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Alerts by type
        fig = px.pie(
            df_stats,
            values='count',
            names='alert_type',
            title="Alerts by Type"
        )
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Alerts by severity
        severity_counts = df_stats.groupby('severity')['count'].sum().reset_index()
        
        fig = px.bar(
            severity_counts,
            x='severity',
            y='count',
            color='severity',
            color_discrete_map={
                'LOW': '#28a745',
                'MEDIUM': '#ffc107',
                'HIGH': '#fd7e14',
                'CRITICAL': '#dc3545'
            },
            title="Alerts by Severity"
        )
        fig.update_layout(showlegend=False, height=350)
        st.plotly_chart(fig, use_container_width=True)


def main():
    """Main dashboard function"""
    # Header
    st.title("🚨 Real-Time Risk Alert Dashboard")
    st.markdown("Monitor brokerage transaction risks in real-time")
    
    # Sidebar
    with st.sidebar:
        st.header("Dashboard Controls")
        
        # Auto-refresh toggle
        auto_refresh = st.checkbox("Auto-refresh", value=True)
        refresh_interval = st.slider("Refresh interval (seconds)", 5, 60, 10)
        
        st.divider()
        
        # Manual refresh button
        if st.button("Refresh Now", use_container_width=True):
            st.rerun()
        
        st.divider()
        
        # System status
        st.subheader("System Status")
        try:
            db = get_database()
            st.success("Database: Connected")
        except:
            st.error("Database: Disconnected")
        
        st.caption(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")
    
    # Main content
    render_summary_metrics()
    
    st.divider()
    
    # Create tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Overview",
        "🚨 Alerts",
        "📈 Exposures",
        "📉 Transactions"
    ])
    
    with tab1:
        st.header("System Overview")
        render_alert_statistics()
        st.divider()
        render_transaction_timeline()
    
    with tab2:
        render_alerts_section()
    
    with tab3:
        render_exposure_charts()
    
    with tab4:
        render_transaction_timeline()
    
    # Auto-refresh logic
    if auto_refresh:
        time.sleep(refresh_interval)
        st.rerun()


if __name__ == "__main__":
    main()
