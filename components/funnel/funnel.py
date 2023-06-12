import dash_html_components as html
import dash_core_components as dcc

def create_funnel():
  data = [
    {"stage": "Лидов", "value": 1000},
    {"stage": "Первый контакт", "value": 800},
    {"stage": "Подборки недвижимости", "value": 600},
    {"stage": "Встреч", "value": 400},
    {"stage": "Показов", "value": 200},
    {"stage": "Подписаний договоров", "value": 56},
  ]
  layout = html.Div([
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
          "title": "Воронка продаж",
          "margin": {"l": 50, "r": 50, "t": 100, "b": 100}
        }
      }
    )
  ])  
  return layout