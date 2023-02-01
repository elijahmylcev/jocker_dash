import dash_html_components as html
import dash_core_components as dcc

def create_funnel():
  data = [{"stage": "Visitors", "value": 1000},
        {"stage": "Leads", "value": 800},
        {"stage": "Qualified Leads", "value": 600},
        {"stage": "Opportunities", "value": 400},
        {"stage": "Customers", "value": 200}]
  layout = html.Div([
    html.H1("Sales Funnel"),
    dcc.Graph(
      id="funnel",
      figure={
        "data": [
          {
            "type": "funnel",
            "y": [d["stage"] for d in data],
            "x": [d["value"] for d in data]
          }
        ],
        "layout": {
          "title": "Sales Funnel",
          "margin": {"l": 50, "r": 50, "t": 100, "b": 100}
        }
      }
    )
  ])  
  return layout