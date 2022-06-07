from turtle import color
from dash import Dash, dash_table, dcc, html, Input, Output, callback
from numpy import empty, maximum, minimum
import pandas as pd
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from dash import  html
from dash.dash_table import DataTable, FormatTemplate
from dash.dash_table.Format import Sign
import plotly.express as px
import csv
import json
import pandas as pd
import qor_functions


percentage = FormatTemplate.percentage(2).sign(Sign.positive)
version1 = "10.5B"
version2 = "main" #00
minimum = -0.01
maximum = 0.01
designs=[]

table1 = qor_functions.change(qor_functions.change_to_table('qor1.txt'))
table2 = qor_functions.change(qor_functions.change_to_table('qor2.txt'))

completionRate1 = qor_functions.completion_rate(table1)
completionRate2 = qor_functions.completion_rate(table2)

koora = [{"name": ["", "Design-testname"], "id": "Design-testname"+ version1}]
youssef =qor_functions.getCsvData("merge_qor.txt")
youssef.insert(0, "status")

for i in youssef:
    if i == "status" or i =="hostname":
       koora.append({"name": [i, version1], "id": i+version1, "hideable": True})
       koora.append({"name": [i, version2], "id": i+version2, "hideable": True})
       #koora.append({"name": [i, "diff"], "id": i+"diff"})
    else:
       koora.append({"name": [i, version1], "id": i+version1, "hideable": True})
       koora.append({"name": [i, version2], "id": i+version2, "hideable": True})
       #koora.append({"name": [i, "diff"], "id": i+"diff"})
       koora.append(dict(id=i+"diff", name=[i, "diff"], type='numeric', format=percentage))

all_columns =qor_functions.get_all_columns(table1,table2,version1,version2)
diff_headers = qor_functions.get_diff_headers(table1,table2,version1,version2)
records = qor_functions.append_diff(table1,table2,version1,version2)


for dict1 in records:
    for key in dict1:
        if key =='Design-testname' + version1:
            designs.append(dict1[key])

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = dbc.Container([

      dcc.Markdown('# Table For Main Metrics', style={'textAlign':'center'}),

      dbc.Label("Show number of Testcases"),
       row_drop := dcc.Dropdown(value=5, clearable=False, style={'width':'20%'},
                             options=[1,3,4, 5,10,len(records)]),

                                              
                             
      dbc.Row([dbc.Label("Select Testcase"),
        dbc.Col([
            design_drop := dcc.Dropdown([x for x in sorted(pd.DataFrame(records)["Design-testname"+version1].unique())], multi= True,style={'width':'80%'})
        ])
        

    ], justify="between", className='mt-3 mb-4'), 

    switches := html.Div(
    [
        
        dbc.Checklist(
            options=[
                {"label": "PASS", "value": 1},
                {"label": "FAIL", "value": 2},
                
            ],
            value=[],
            id="switches-input",
            inline=True,
            switch=True,
        ),
    ]
),
                     
button_group := html.Div(
    [
        dbc.RadioItems(
            id="radios",
            className="btn-group",
            inputClassName="btn-check",
            labelClassName="btn btn-outline-primary",
            labelCheckedClassName="active",
            options=[
                {"label": "show [5,10] % degradation", "value": 1},
                {"label": "show > 10 % degradation", "value": 2},
                {"label": "show > 10 % improvement", "value": 3},
                {"label": "show [5,10] % improvement ", "value": 4},
                {"label": "reset ", "value": 5}
                
            ],
            value=0,
            
        )
        
    ],
    className="radio-group",
),
dbc.Label("Select stage"),
       row_stage := dcc.Dropdown(value="main metrics", clearable=False, style={'width':'32%'},
                             options=["main metrics","cpu stage"]),    

                          
            
    my_table :=  dash_table.DataTable(
    columns= koora,
    data=records,
    
    filter_action= "native",
    merge_duplicate_headers=True,
    page_action='native',     # all data is passed to the table up-front
    page_size=5,
    
    hidden_columns=[],
    tooltip_data=[
        {
            column: {'value': str(value), 'type': 'markdown'}
            for column, value in row.items()
        } for row in records
    ],
    
      style_data_conditional=([
        {
            'if': {
                'filter_query': '{{{}}} = {}'.format('status'+version1, 'FAIL'),
                'column_id': 'status'+version1
            },
            'backgroundColor': '#FF4136',
            'color': 'white',
            'fontWeight': 'bold'
        },
        {
            'if': {
                'filter_query': '{{{}}} = {}'.format('status'+version2, 'FAIL'),
                'column_id': 'status'+version2
            },
            'backgroundColor': '#FF4136',
            'color': 'white',
            'fontWeight': 'bold'
        },
        {
            'if': {
                'filter_query': '{{{}}} = {}'.format('status'+version2, 'PASS'),
                'column_id': 'status'+version2
            },
             'backgroundColor': '#3D9970',
            'color': 'white',
            'fontWeight': 'bold'
        },
          {
            'if': {
                'filter_query': '{{{}}} = {}'.format('status'+version1, 'PASS'),
                'column_id': 'status'+version1
            },
            'backgroundColor': '#3D9970',
            'color': 'white',
            'fontWeight': 'bold'
        },
        {
            'if':{
                'column_type': 'any'
            },
            'textAlign': 'left'
        }
    ] +
    [ {
                'if': {
                    'filter_query': '{{{}}} < {}'.format(col, -0.01),
                    'column_id': col
                },
                'backgroundColor': '#3D9970',
                'color': 'white'
            } for col in diff_headers 
            ] +
         [ {
                'if': {
                    'filter_query': '{{{}}} > {}'.format(col, 0.01),
                    'column_id': col
                },
                'backgroundColor': '#FF4136',
                'color': 'white'
            } for col in diff_headers 
            ]+
            
             [ {
                'if': {
                    'filter_query': ('{{{col}}} >= {min}' + (' && {{{col}}} <= {max}')).format(col = col,min = minimum,max =maximum),
                    'column_id': col
                },
                'backgroundColor': '#000000',
                'color': 'white'
            } for col in diff_headers 
            ]+
            [
                {
                    'if': {
                        'filter_query': '{{{}}} is blank'.format(col),
                        'column_id': col
                    },
                    'backgroundColor': '#F1F1F1',
                    'color': 'white'
                } for col in all_columns
            ]
    ),
     style_data={                # overflow cells' content into multiple lines
            'whiteSpace': 'normal',
            'height': 'auto'
        },
        
        style_table={'overflowX': 'scroll','overflowY': 'auto'},
        
        style_header={
        
    #     'color': 'black',
        'fontWeight': 'bold',
    #     'border': '1px solid black' 
     },
    # style_cell={ 'border': '1px solid black' }
        
),


dbc.Label("Completion rate " + version1),
progress1 := dbc.Progress(label= str(completionRate1)+"%", value=completionRate1,color="info",striped=True,animated=True,style={"height": "30px",'width':'32%'}),
dbc.Label("Completion rate " + version2),
progress2 := dbc.Progress(label= str(completionRate2)+"%", value=completionRate2,color="info",striped=True,animated=True,style={"height": "30px",'width':'32%'}),



])
@callback(
    [Output(my_table, 'data'),
    Output(my_table, 'page_size')],
    [Input(design_drop, 'value'),
    Input(row_drop, 'value'),Input("switches-input", 'value'),Input("radios", "value")]
    

    
)
def update_dropdown_options(design_v, row_v,s_v,n):
    dff = pd.DataFrame(records)
    string1 =""

    if design_v:
        dff = dff[dff["Design-testname"+ version1].isin(design_v)]

    if s_v == [2]:
        dff = dff[(dff["status"+version1]== 'FAIL') | (dff["status"+version2]== 'FAIL') ] 
    elif s_v == [1]:
        dff = dff[(dff["status"+version1]== 'PASS') | (dff["status"+version2]== 'PASS')  ]  
    if n == 1:
        dff = qor_functions.show_range(0.05,0.1,records,version1,version2)
        

    if n == 2:
        dff = qor_functions.show_degradation(0.1,records,version1,version2)
    if n ==3:
        dff = qor_functions.show_improvement(-0.1,records,version1,version2) 
    if n==4:
        dff = qor_functions.show_range(-0.1,-0.05,records,version1,version2)   
    if n==5:
        dff=dff          
          
    
    

    return dff.to_dict('records'), row_v


if __name__ == '__main__':
    app.run_server(debug=True, port=5050)          




