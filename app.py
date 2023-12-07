from flask import Flask, flash, redirect, render_template, request
from markupsafe import Markup
from dateutil.relativedelta import relativedelta
from helpers import apology
from io import BytesIO
from matplotlib.figure import Figure
from datetime import datetime
import base64
import os

# Configure application
app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    # Generate the figure **without using pyplot**.
    fig = Figure(figsize=[9.06, 3.14], facecolor="black", layout="constrained")
    ax = fig.subplots()
    ax.patch.set_facecolor('black')
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')
    ax.spines['bottom'].set_color('white')
    ax.spines['left'].set_color('white')

    fields = {
        'start': '', 
        'contribution': '',
        'value': '',
        'performance': '',
        'target': '',
    }

    if request.method == "POST":

        try:
            fields = {
                'start': datetime.strptime(request.form.get('start'), '%Y-%m'),
                'contribution': float(request.form.get('contribution')),
                'value': float(request.form.get('value')),
                'performance': float(request.form.get('performance')),
                'target': float(request.form.get('target')),
            }

            x = [fields['start']]
            y = [fields['value']]

            while y[-1] < fields['target']:
                x.append(x[-1] + relativedelta(months=1))
                y.append(y[-1] + fields['contribution'] + ((y[-1] + fields['contribution']) * fields['performance']/100/12))

            ax.plot(x, y, color="white")
            fields['start'] = datetime.strftime(fields['start'], '%Y-%m')
        except ValueError:
            return apology('invalid data')

    # Save it to a temporary buffer.
    buf = BytesIO()
    fig.savefig(buf, format="png")
    # Embed the result in the html output.
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    return render_template('index.html', data=Markup(f"<img src='data:image/png;base64,{data}' class='h-full rounded-2xl'/>"), fields=fields)
