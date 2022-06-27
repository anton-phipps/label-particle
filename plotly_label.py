import plotly.express as px
import dash
from dash import dcc
from dash import html
from dash import callback_context
from dash.dependencies import Input, Output, State
from skimage import data
import json

import pandas as pd
import numpy as np
import tifffile as ti
import os
from stat import S_IREAD

# Image files must be placed in this directory to create
# a list of the image files
files = os.listdir("./images/")
# create a dataframe for the x and y positions of particles
df = pd.DataFrame(columns=['x', 'y'])
# an array to hold images
image = []
# itterate through the files
for f in files:
    # isolate only the .tif files
    if ".tif" in f:
        # make sure you know which file is associated with which index
        print(f'{len(image)}:\t{f}')
        image.append(ti.imread('./images/' + f))

# This is the file number in the array
group_no = '1'
# This is the frame number of the tiff file
im_no = '31'

# The image to display based off of the choices
img = image[int(group_no)][int(im_no)]
# The save name for the file
print(group_no + '-'+ im_no + '.csv')

#fig = px.imshow(image[0], animation_frame=0, binary_string=True, width=1392, height=1040)

# Create the figure for display
fig = px.imshow(img, binary_string=True, )

# Add annotations to mark particles
fig.update_layout(
    dragmode="drawrect",
    newshape=dict(line_color='red', line_width=2), 
    width = int(1392 * 2), height = int(1040 * 2))
config = {
    "modeBarButtonsToAdd": [
        "drawrect",
        "eraseshape",
    ]
}

# Build App
app = dash.Dash(__name__)
app.layout = html.Div(
    [
        html.H4(
            "Drag and draw rectangle annotations around the particles to record position\nEnter a filename and click Save CSV button to export a file."
        ),
        dcc.Graph(id="graph-pic", figure=fig, config=config),
        html.Div(dcc.Input(id='file-name', type='text', value=group_no + '-'+ im_no + '.csv')),
        html.Button('Save csv', id='save-csv', n_clicks=0),
        dcc.Markdown("Center of Line (x, y)"),
        html.Pre(id="annotations-data-pre"),
    ]
)

@app.callback(
    Output("annotations-data-pre", "children"),
    [Input("graph-pic", "relayoutData"),
    Input("save-csv", "n_clicks"),
    ],
    State('file-name', 'value'),
    prevent_initial_call=True,
)
def on_new_annotation(relayout_data, n_clicks, value):
    if "shapes" in relayout_data:
        shape_array = []
        for s in relayout_data["shapes"]:
            x, y = int((s["x0"] + s["x1"]) / 2), int((s["y0"] + s["y1"]) / 2)
            shape_array.append([x, y])
        df = pd.DataFrame(columns=['x', 'y'], data = shape_array)
        changed_id = [p['prop_id'] for p in callback_context.triggered][0]
        print("change id: ", changed_id)
        print("value: ", value)
        if 'save-csv' in changed_id:
            update_output(df, value)
            return dash.no_update
        # Display the number of prarticles identified
        out_text = 'Diatom Count: ' + str(len(shape_array)) +'\n\nx,y\n'
        # Create the on site array
        for s in shape_array:
            out_text = out_text + str(s[0]) + ',' + str(s[1]) + '\n'
        # Display all particle positions on screen
        return str(out_text)
        #return json.dumps(relayout_data["shapes"], indent=2)
    else:
        return dash.no_update

# Save the file to CSV
# There is a default name, however this can be changed
def update_output(df_out, fileName):
    if fileName != None:
        print(f"Saving File '{fileName}'")
        df_out.to_csv(fileName, index=False)
    return

# if the python command calls this file specifically, then run the app
if __name__ == "__main__":
    app.run_server()