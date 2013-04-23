# -*- coding: utf-8 -*-

# Copyright (c) 2012 Eren Güven
#
# Licensed under the Apache License, Version 2.0 (the "License")
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from tprocessmixin import ProcessMixin

try:
    from tcelerymixin import CeleryMixin
except ImportError: # celery not installed, redefine dummy CeleryMixin
    msg = 'celery not installed. CeleryMixin disabled.'
    class CeleryMixin(object):
        def __init__(self):
            """Raise `NotImplementedError`"""
            raise NotImplementedError(msg)

__all__ = ['CeleryMixin','ProcessMixin']
