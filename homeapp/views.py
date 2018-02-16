# -*- coding: utf-8 -*-
from django.http import JsonResponse
from django.views.generic import TemplateView

from ecgprocessing import processing_utils
from ecgprocessing.ECGSignal import ECGSignal
from homeapp.mixins import AjaxableResponseMixin

import plotly.offline as opy
import plotly.graph_objs as go

from ssnecg import SSNECG


def singleton(class_):
  instances = {}
  def getinstance(*args, **kwargs):
    if class_ not in instances:
        instances[class_] = class_(*args, **kwargs)
    return instances[class_]
  return getinstance

@singleton
class SSNECGHandler(object):
  e = None

  def getSSNECG(self):
      if not self.e:
          self.e = SSNECG()
          self.e.load('40-20-2.150000.h5')
      return self.e


class Home(object):
    class IndexView(TemplateView):
        template_name = "index.html"

        def get_context_data(self, **kwargs):
            ctx = super(Home.IndexView, self).get_context_data()
            ctx['landing'] = True
            return ctx

    class AppView(TemplateView):
        template_name = "ecg.html"

        def get_context_data(self, **kwargs):
            ctx = super(Home.AppView, self).get_context_data()
            return ctx

    class ECGChartAjaxView(AjaxableResponseMixin, TemplateView):
        template_name = 'ecg_chart_partial.html'
        sample_no = 0
        signal = None
        before = True
        compressed = True
        decompressed = True


        def get_context_data(self, **kwargs):
            ctx = super(Home.ECGChartAjaxView, self).get_context_data()
            if not self.sample_no:
                self.sample_no = 0
            self.signal = ECGSignal(self.sample_no)
            ctx['sample_no'] = self.sample_no + 1
            ctx['heart_rate_avg'] = self.signal.heart_rate_avg
            ctx['rpeaks'] = self.signal.rpeaks

            handler = SSNECGHandler()
            self.e = handler.getSSNECG()
            s = self.e.get_signal(self.sample_no)
            c = self.e.compress(self.sample_no)
            d = self.e.decompress(c)
            diff = d - s

            if self.before:
                ctx['signal'] = self.get_graph(s, "Before compression")
            if self.compressed:
                ctx['compressed_signal'] = self.get_graph(c, "After compression")
            if self.decompressed:
                ctx['decompressed_signal'] = self.get_graph(d, "After decompression")
            if self.difference:
                ctx['difference'] = self.get_graph(diff, "Signal difference")

            decompressed_params  = processing_utils.get_data_biosppy(d)
            decompressed_heart_rate = decompressed_params['heart_rate']
            decompressed_rpeaks = decompressed_params['rpeaks']
            ctx['decompressed_heart_rate_avg'] = sum(decompressed_heart_rate) / float(len(decompressed_heart_rate))
            ctx['decompressed_rpeaks'] = decompressed_rpeaks
            ctx['mean_square_error_signal'] = (diff ** 2).mean()
            if len(decompressed_rpeaks) == len(self.signal.rpeaks):
                ctx['mean_square_error_rpeaks'] = ((decompressed_rpeaks - self.signal.rpeaks) ** 2).mean()

            return ctx

        def get_graph(self, signal, title):
            y = signal
            trace1 = go.Scatter(y=y, marker={'color': '#13b02b', 'symbol': 104,
                                                  'size': "10"},
                                mode="lines", name='Signal')

            data = go.Data([trace1])
            layout = go.Layout(
                height=400,
                font=dict(
                    family='Balto, monospace',
                    size=18,
                    color='#9f9f9f'
                ),
                xaxis=dict(
                    title=title,
                    titlefont=dict(
                        family='Balto, monospace',
                        size=15,
                        color='#9f9f9f'
                    ),
                    autorange=True,
                    showgrid=False,
                    zeroline=False,
                    showline=False,
                    autotick=True,
                    ticks='',
                    showticklabels=False
                ),
                yaxis=dict(
                    title='Value',
                    titlefont=dict(
                        family='Balto, monospace',
                        size=15,
                        color='#9f9f9f'
                    ),
                    autorange=True,
                    # showgrid=False,
                    zeroline=False,
                    showline=False,
                    autotick=True,
                    # ticks='',
                    # showticklabels=False
                ),
                plot_bgcolor='rgba(255,255,255, 0.0)',paper_bgcolor='rgba(0,0,0, 0.2)')
            figure = go.Figure(data=data, layout=layout)
            div = opy.plot(figure, auto_open=False, output_type='div')
            return div

        def post_ajax(self, request, **kwargs):
            self.sample_no = int(self.request.POST.get('sample_no', None)) - 1
            before = self.request.POST.get('before', 'false')
            compressed = self.request.POST.get('compressed', 'false')
            decompressed = self.request.POST.get('decompressed', 'false')
            difference = self.request.POST.get('difference', 'false')

            self.before = before == 'true'
            self.compressed = compressed == 'true'
            self.decompressed = decompressed == 'true'
            self.difference = difference == 'true'

            if 0 <= self.sample_no < 305:
                result = super(Home.ECGChartAjaxView, self).get(request)
                return result
            else:
                return JsonResponse(data={'error': True, 'message': 'Sample number must be between 1 and 305'})





