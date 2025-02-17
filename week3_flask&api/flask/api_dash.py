from dash import Dash, html, dcc
from dash.dependencies import Input, Output, State
from flask import Flask, jsonify
from text_analysis import text_analysis
import visdcc
import requests
import pandas as pd

def dash_app(server):       
    app = Dash(__name__, server=server, url_base_pathname='/dash_app/')    # url: http://127.0.0.1:8000/dash_app

    # HTML
    app.layout = html.Div([
        html.Div([

            # 篩選器，使用者可選取範圍
            dcc.RangeSlider(
                id='correlation-range-slider',
                min=0,
                max=1,
                step=0.01,
                value=[0, 1],
                marks={i / 10: str(i / 10) for i in range(11)},
                tooltip={"placement": "bottom", "always_visible": True}
            ),
           html.Button('繪製網路圖', id='update-button', n_clicks=0, style={
                'backgroundColor': 'lightblue',
                'color': 'white',
                'fontSize': '18px',
                'padding': '13px 27px',
                'border': 'none',
                'borderRadius': '5px',
                'cursor': 'pointer',
                'marginTop': '50px'
            })
        ], style={'width': '20%', 'display': 'inline-block', 'padding': '20px'}),

        html.Div([
            # 網路圖物件
            visdcc.Network(id='net',
                           options=dict(height='800px', width='100%')),
        ], style={'width': '75%', 'display': 'inline-block', 'vertical-align': 'top'}),

        html.Div(id='nodes-count', style={'padding': '10px', 'fontSize': '18px'}),
        html.Div(id='edges-count', style={'padding': '10px', 'fontSize': '18px'})
    ])

    # 即時更新邊和節點數
    @app.callback(
        [Output('nodes-count', 'children'),
         Output('edges-count', 'children')],
        [Input('correlation-range-slider', 'value')]
    )
    def update_counts(correlation_range):
        response = requests.get('http://localhost:8000/correlation')
        data = response.json()

        # 取得所選範圍的 MAX & min
        min_corr, max_corr = correlation_range

        # 初始化節點和邊的list
        nodes = []
        edges = []

        # 處理關聯性矩陣的資料
        for item in data:
            item1 = item['item1']
            item2 = item['item2']
            correlation = item['correlation']

            # 篩選範圍
            # 無論關係為正負向，僅看關聯的強度，所以取絕對值
            if min_corr <= abs(correlation) <= max_corr:
                # 加入 nodes
                if item1 not in [node['id'] for node in nodes]:
                    nodes.append({'id': item1, 'label': item1})
                if item2 not in [node['id'] for node in nodes]:
                    nodes.append({'id': item2, 'label': item2})

                # 加入 edges
                edges.append({'from': item1, 'to': item2, 'value': abs(correlation)})

        # 更新數量
        num_nodes = len(nodes)
        num_edges = len(edges)

        return f'該範圍所有的節點（nodes）數: {num_nodes}', f'該範圍所有的邊（edges）數: {num_edges}'

    # 更新網路圖
    @app.callback(
        Output('net', 'data'),
        [Input('update-button', 'n_clicks')],
        [State('correlation-range-slider', 'value')]
    )
    def update_network(n_clicks, correlation_range):
        if n_clicks > 0:
            response = requests.get('http://localhost:8000/correlation')
            data = response.json()

            # 取得範圍的最小值和最大值
            min_corr, max_corr = correlation_range

            # 初始化節點和邊的列表
            nodes = []
            edges = []

            # 處理關聯性矩陣
            for item in data:
                item1 = item['item1']
                item2 = item['item2']
                correlation = item['correlation']

                # 篩選範圍
                if min_corr <= abs(correlation) <= max_corr:
                    # 加入 nodes
                    if item1 not in [node['id'] for node in nodes]:
                        nodes.append({'id': item1, 'label': item1})
                    if item2 not in [node['id'] for node in nodes]:
                        nodes.append({'id': item2, 'label': item2})

                    # 加入 edges
                    edges.append({'from': item1, 'to': item2, 'value': abs(correlation)})

            # visdcc 網路圖的資料
            graph_data = {'nodes': nodes, 'edges': edges}

            return graph_data


        # 使用者尚未點擊按鈕，返回空數據
        return {'nodes': [], 'edges': []}

    return app






# # 傳入 flask伺服器
# def dash_app(server):
#     # 建立路徑
#     app = Dash(__name__, server=server, url_base_pathname='/dash_app/')  # url: http://127.0.0.1:8000/dash_app

#     # HTML
#     app.layout = html.Div([
#         html.Div([
#             dcc.RangeSlider(
#                 id='correlation-range-slider',
#                 min=0,
#                 max=1,
#                 step=0.01,
#                 value=[0, 1],
#                 marks={i / 10: str(i / 10) for i in range(11)},
#                 tooltip={"placement": "bottom", "always_visible": True}
#             ),
#             html.Button('繪製網路圖', id='update-button', n_clicks=0, style={
#                 'backgroundColor': 'lightblue',
#                 'color': 'white',
#                 'fontSize': '18px',
#                 'padding': '13px 27px',
#                 'border': 'none',
#                 'borderRadius': '5px',
#                 'cursor': 'pointer',
#                 'marginTop': '50px'
#             })
#         ], style={'width': '20%', 'display': 'inline-block', 'padding': '20px'}),

#         html.Div([
#             visdcc.Network(id='net',
#                            options=dict(height='600px', width='100%')),
#         ], style={'width': '75%', 'display': 'inline-block', 'vertical-align': 'top'}),

#         html.Div(id='nodes-count', style={'padding': '10px', 'fontSize': '18px'}),
#         html.Div(id='edges-count', style={'padding': '10px', 'fontSize': '18px'})
#     ])




#     @app.callback(
#         [Output('net', 'data'),
#          Output('nodes-count', 'children'),
#          Output('edges-count', 'children')],
#         [Input('update-button', 'n_clicks')],
#         [State('correlation-range-slider', 'value')]
#     )
#     def update_network(n_clicks, correlation_range):
#         if n_clicks > 0:
#             try:
#                 # 獲取關聯性數據
#                 response = requests.get('http://localhost:8000/correlation')
#                 response.raise_for_status()  # 確保請求成功
#                 data = response.json()

#                 # 取得範圍的最小值和最大值
#                 min_corr, max_corr = correlation_range

#                 # 初始化節點和邊的列表
#                 nodes = []
#                 edges = []

#                 # 處理關聯性數據
#                 for item in data:
#                     item1 = item['item1']
#                     item2 = item['item2']
#                     correlation = item['correlation']

#                     # 篩選符合範圍的邊
#                     if min_corr <= abs(correlation) <= max_corr:
#                         # 添加節點
#                         if item1 not in [node['id'] for node in nodes]:
#                             nodes.append({'id': item1, 'label': item1})
#                         if item2 not in [node['id'] for node in nodes]:
#                             nodes.append({'id': item2, 'label': item2})

#                         # 添加邊
#                         edges.append({'from': item1, 'to': item2, 'value': abs(correlation)})

#                 # 準備 visdcc 網路圖的數據
#                 graph_data = {'nodes': nodes, 'edges': edges}

#                 # 更新節點和邊的數量
#                 num_nodes = len(nodes)
#                 num_edges = len(edges)

#                 return graph_data, f'Number of nodes: {num_nodes}', f'Number of edges: {num_edges}'

#             except Exception as e:
#                 print(f"Error: {e}")
#                 return {'nodes': [], 'edges': []}, 'Number of nodes: 0', 'Number of edges: 0'

#         # 如果按鈕未被點擊，返回空數據
#         return {'nodes': [], 'edges': []}, 'Number of nodes: 0', 'Number of edges: 0'

#     return app



# 創建Flask server
# server = Flask(__name__)
# app = Dash(__name__, server=server, url_base_pathname='/dash_app/')

# app.layout = html.Div([
#       visdcc.Network(id = 'net',
#                      selection = {'nodes':[], 'edges':[]},
#                      options = dict(height= '600px', width= '100%')),
#       html.Div(id = 'nodes'),
#       html.Div(id = 'edges')
# ])
      
# @app.callback(
#     Output('nodes', 'children'),
#     [Input('net', 'selection')])
# def myfun(x): 
#     s = 'Selected nodes : '
#     if len(x['nodes']) > 0 : s += str(x['nodes'][0])
#     return s

# @app.callback(
#     Output('edges', 'children'),
#     [Input('net', 'selection')])
# def myfun(x): 
#     s = 'Selected edges : '
#     if len(x['edges']) > 0 : s = [s] + [html.Div(i) for i in x['edges']]
#     return s


# @server.route('/correlation')
# def get_correlation():
#     analysis = text_analysis()
#     corr = analysis.get_correlation()
#     return jsonify(corr.to_dict(orient='records'))

# if __name__ == '__main__':
#     app.run_server(debug=True)