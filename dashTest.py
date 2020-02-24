import dash
import dash_core_components as dcc
import dash_html_components as html

from flask import Flask, Response
import cv2

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# ADD CAMERA
class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)

    def __del__(self):
        self.video.release()

    def get_frame(self):
        success, image = self.video.read()
        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()


def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

server = Flask(__name__)
app = dash.Dash(__name__, external_stylesheets=external_stylesheets,server=server)

@server.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

markdown_text = '''
# Mousai Neurotechnologies
### Mneme: A Python Module for Integrated Decoding and I/O Modeling of the Nervous System
Written by [Garrett Flynn](http://garrettflynn.com/) at the University of Southern California.
02/21/20
'''

app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    # Markdown
    dcc.Markdown(children=markdown_text,style={
            'textAlign': 'center',
            'color': colors['text']
        }),

    # Text Input
    html.Label('Text Input'),
    dcc.Input(value='Your User ID', type='text'),

    # Dropdown
    dcc.Dropdown(
        options=[
            {'label': 'OpenBCI', 'value': 'OPENBCI'},
            {'label': u'Blackrock', 'value': 'RAM'},
            {'label': 'Synthetic', 'value': 'SYNTHETIC'}
        ],
        value='SYNTHETIC'
    ),

    html.Img(src="/video_feed",style={'height':'10%', 'width':'50%'}),

    dcc.Graph(
        id='voltage-graph',
        figure={
            'data': [
                {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
                {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': u'Montréal'},
            ],
            'layout': {
                'plot_bgcolor': colors['background'],
                'paper_bgcolor': colors['background'],
                'font': {
                    'color': colors['text']
                }
            }
        }
    ),

    # Slider
    html.Label('Slider'),
    dcc.Slider(id='voltage-slider',
        min=0,
        max=9,
        marks={i: 'Label {}'.format(i) if i == 1 else str(i) for i in range(1, 6)},
        value=5,
    ),

    # # Checklist
    # html.Label('Checkboxes'),
    # dcc.Checklist(
    #     options=[
    #         {'label': 'New York City', 'value': 'NYC'},
    #         {'label': u'Montréal', 'value': 'MTL'},
    #         {'label': 'San Francisco', 'value': 'SF'}
    #     ],
    #     value=['MTL', 'SF']
    # ),

    # # Exclusive Items
    # html.Label('Radio Items'),
    # dcc.RadioItems(
    #     options=[
    #         {'label': 'New York City', 'value': 'NYC'},
    #         {'label': u'Montréal', 'value': 'MTL'},
    #         {'label': 'San Francisco', 'value': 'SF'}
    #     ],
    #     value='MTL'
    # ),

    # # Multiselect Dropdown
    # html.Label('Multi-Select Dropdown'),
    # dcc.Dropdown(
    #     options=[
    #         {'label': 'New York City', 'value': 'NYC'},
    #         {'label': u'Montréal', 'value': 'MTL'},
    #         {'label': 'San Francisco', 'value': 'SF'}
    #     ],
    #     value=['MTL', 'SF'],
    #     multi=True
    # )
])

if __name__ == '__main__':
    app.run_server(debug=True)