import pandas as pd
from dash import html
import dash_ag_grid as dag
from datetime import datetime

def read_dividend_csv(file_path):
    try:
        df = pd.read_csv(file_path)
        return df
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return pd.DataFrame()  # Return an empty DataFrame if file not found

def sort_and_filter_by_date(df, date_column):
    # Convert the date column to datetime
    df[date_column] = pd.to_datetime(df[date_column])

    # Filter out dates before today's date (optional)
    today = datetime.now().date()
    df = df[df[date_column] >= pd.Timestamp(today)]

    # Sort by date in ascending order
    df = df.sort_values(by=date_column, ascending=True)

    # Format the date column to display only the date part
    df[date_column] = df[date_column].dt.strftime('%Y-%m-%d')

    return df

def create_dividend_table(df, title):
    # Define a mapping of old column names to new names
    column_rename_mapping = {
        'ticker': 'Ticker',
        'ex_dividend_date': 'Ex Date',
        'pay_date': 'Pay Date',
        'cash_amount': 'Amount',
    }

    filterParams = {
        "buttons": ['apply', 'reset'],
        "closeOnApply": True,
    }

    # Rename the columns if the DataFrame is not empty
    if not df.empty:
        df = df.rename(columns=column_rename_mapping)

    # Generate a unique id for the grid
    grid_id = f"grid-{title.replace(' ', '-').lower()}"

    # Define the column definitions for AG Grid
    column_defs = []
    for col in df.columns:
        col_def = {'headerName': col, 'field': col, 'flex': 1}
        
        # Apply specific style for 'Amount' column
        if col == 'Amount':
            col_def['cellStyle'] = {'color': '#CCF381'}  # Change 'blue' to your desired color
        
        column_defs.append(col_def)

    # Sort and filter the DataFrame by 'Ex Date' if it's not empty
    if not df.empty:
        df = sort_and_filter_by_date(df, 'Ex Date')

    if df.empty:
        return html.Div([html.H4(title), html.P("No data available.")], style={'height': '50vh'})
    else:
        return html.Div([
            html.H4(title),
            dag.AgGrid(
                id=grid_id,  # Add the unique id here
                rowData=df.to_dict('records'),
                dashGridOptions={
                    'defaultColDef': {
                        'sortable': True,
                        'filter': True,
                        'resizable': True,
                        'filterParams': filterParams,
                    },
                    'columnDefs': column_defs,
                },
                style={
                    'height': '45vh',
                },
            )
        ], style={'height': '50vh'})

def create_earnings_table(df, title):
    # Define a mapping of old column names to new names
    column_rename_mapping = {
        'symbol': 'Ticker',
        'reportDate': 'Report Date',
    }

    filterParams = {
        "buttons": ['apply', 'reset'],
        "closeOnApply": True,
    }
    # Rename the columns if the DataFrame is not empty
    if not df.empty:
        df = df.rename(columns=column_rename_mapping)

    # Generate a unique id for the grid
    grid_id = f"grid-{title.replace(' ', '-').lower()}"

    # Define the column definitions for AG Grid
    column_defs = [{'headerName': col, 'field': col, 'flex': 1} for col in df.columns]

    # Sort and filter the DataFrame by 'Report Date' if it's not empty
    if not df.empty:
        df = sort_and_filter_by_date(df, 'Report Date')

    if df.empty:
        return html.Div([html.H4(title), html.P("No data available.")], style={'height': '50vh'})
    else:
        return html.Div([
            html.H4(title),
            dag.AgGrid(
                id=grid_id,
                rowData=df.to_dict('records'),
                dashGridOptions={
                    'defaultColDef': {
                        'sortable': True,
                        'filter': True,
                        'resizable': True,
                        'filterParams': filterParams,
                    },
                    'columnDefs': column_defs,
                },
                style={
                    'height': '45vh',
                },
            )
        ], style={'height': '50vh'})

def generate_table_page_2(height='30vh'):

    # Load the dividend data
    dividends_this_week = read_dividend_csv('files/dividends_grouped_This Week.csv')
    dividends_next_week = read_dividend_csv('files/dividends_grouped_Next Week.csv')
    dividends_next_month = read_dividend_csv('files/dividends_grouped_Next Month.csv')
    earnings_data = pd.read_csv('files/earnings.csv')

    filterParams = {
        "buttons": ['apply', 'reset'],
        "closeOnApply": True,
    }

    defaultColDef = {
        "resizable": True,
        "initialWidth": 200,
        "wrapHeaderText": True,
        "autoHeaderHeight": True,
        "sortable": True,
        "filter": "agMultiColumnFilter",
        "filterParams": filterParams,
        "enableRowGroup": False,
        "enableValue": False,
        "enablePivot": False,
    }

    # Load additional CSV data for page 2
    data_frame_page_2 = pd.read_csv('files/output.csv')
    columnDefs_page_2 = [{'headerName': col, 'field': col} for col in data_frame_page_2.columns]

    # Create the earnings table
    earnings_table = create_earnings_table(earnings_data, "Earnings Calendar")

    table_page_2 = dag.AgGrid(
        id='table-page-2',
        columnDefs=columnDefs_page_2,
        rowData=data_frame_page_2.to_dict('records'),
        style={"height": height, "width": "100%"},
        columnSize="responsiveSizeToFit",
        defaultColDef=defaultColDef,  # Assuming you've defined this earlier
        dashGridOptions={
            "autopaginationAutofPageSize": True,
            "animateRows": True,
            "rowSelection": "single",
            "enableCellTextSelection": True,
            "ensureDomOrder": True,
        },
    )

    # Container for the dividend tables
    content = html.Div([
        html.Div(create_dividend_table(dividends_this_week, "Dividends This Week"), style={'flex': 1}),
        html.Div(create_dividend_table(dividends_next_week, "Dividends Next Week"), style={'flex': 1}),
        html.Div(create_dividend_table(dividends_next_month, "Dividends Next Month"), style={'flex': 1}),
        html.Div(earnings_table, style={'flex': 1, 'flexBasis': '15%', 'maxWidth': '15%'})  # Adjusted size of earnings table
    ], style={'display': 'flex', 'flexDirection': 'row', 'justifyContent': 'space-between', 'marginTop': '20px'})

    # Load additional CSV data for page 2
    data_frame_page_2 = pd.read_csv('files/output.csv')

    # Specify columns to exclude
    columns_to_exclude = ['ASSET TYPE', 'CAPITAL GAINS', 'INV GRADE', 'ADV30']  # Columns to hide
    numeric_columns = {'YTW', 'DAYS TO CALL', 'DAYS TO MATUR', 'SHARES OUTS', 'NOM YIELD', 'DAYS TO FLOAT/RESET'}  # Numeric columns

    # Modify column definitions
    columnDefs_page_2 = [
        {'headerName': col, 'field': col, 'type': 'numericColumn' if col in numeric_columns else None}
        for col in data_frame_page_2.columns if col not in columns_to_exclude
    ]

    table_page_2 = dag.AgGrid(
        id='table-page-2',
        columnDefs=columnDefs_page_2,
        rowData=data_frame_page_2.to_dict('records'),
        style={"height": '30vh', "width": "100%"},
        columnSize="responsiveSizeToFit",
        defaultColDef=defaultColDef,
        dashGridOptions={
            "autopaginationAutofPageSize": True,
            "animateRows": True,
            "rowSelection": "single",
            "enableCellTextSelection": True,
            "ensureDomOrder": True,
        },
    )

    # Assemble the page layout
    return html.Div([
        table_page_2,
        content
    ])
