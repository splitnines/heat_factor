import datetime as dt
import json
import re
import sys

from django.shortcuts import redirect, render
from django.http import HttpResponse

from .forms import GridIronUrlForm
from .grid_iron_calc import grid_iron_calc
from .models import Gridiron


def grid_iron_view(request):
    """Routes to site home page template.
    Arguments:
        request {object} -- HTTPRequest object
    Returns:
        [object] -- HTTPResponse object
    """
    if request.method == 'GET':
        forms = {
            'p_url': GridIronUrlForm(),
        }
        return render(request, 'grid_iron_calc.html', forms)
    else:
        return redirect('')
