"""Plotly testing."""
# pylint: disable=redefined-outer-name,unused-argument,invalid-name

import os
from os import environ as env
import subprocess
import time

import pytest
from plotly import graph_objs as go

from bowtie import App
from bowtie.control import Nouislider, Button
from bowtie.visual import Plotly
from bowtie.tests.utils import reset_uuid


reset_uuid()

viz = Plotly()
ctrl = Nouislider()
ctrl_range = Nouislider(start=(20, 200))
ctrl2 = Button()


def callback(*args):
    """dummy function"""
    chart = go.Figure()
    chart.add_trace(go.Scatter(x=[1, 2, 3, 4], y=[4, 1, 3, 7]))
    chart.layout.title = 'hello world'
    viz.do_all(chart.to_dict())


@pytest.fixture
def plotly(build_path, monkeypatch):
    """Create plotly app."""
    monkeypatch.setattr(App, '_sourcefile', lambda self: 'bowtie.tests.test_plotly')

    app = App()
    app.add(viz)
    app.add_sidebar(ctrl)
    app.add_sidebar(ctrl_range)
    app.add_sidebar(ctrl2)
    app.subscribe(callback, ctrl.on_change)
    app.subscribe(callback, ctrl2.on_click)
    # pylint: disable=protected-access
    app._build()

    env['PYTHONPATH'] = '{}:{}'.format(os.getcwd(), os.environ.get('PYTHONPATH', ''))
    server = subprocess.Popen(os.path.join(build_path, 'src/server.py'), env=env)

    time.sleep(5)
    yield
    server.kill()


def test_plotly(plotly, chrome_driver):
    """Test plotly component."""
    chrome_driver.get('http://localhost:9991')
    chrome_driver.implicitly_wait(5)

    assert chrome_driver.title == 'Bowtie App'

    button = chrome_driver.find_element_by_class_name('ant-btn')
    points = chrome_driver.find_elements_by_class_name('point')
    assert not points

    button.click()

    points = chrome_driver.find_elements_by_class_name('point')

    logs = chrome_driver.get_log('browser')
    for log in logs:
        if log['level'] == 'SEVERE':
            raise Exception(log['message'])

    assert len(points) == 4
