#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import logging
from routes import route_list


def handle_404(request, response, exception):
    logging.exception(exception)
    response.write(
        'You have landed in this page because you have ' +
        'tried to lookup a link that does not exist.' +
        '<html><a href="http://blogvint.appspot.com/">' +
        'Go Back to Blog 0440</a></html>')
    response.set_status(404)


def handle_500(request, response, exception):
    logging.exception(exception)
    response.write('A server error occurred!')
    response.set_status(500)

app = webapp2.WSGIApplication(route_list, debug=True)

app.error_handlers[404] = handle_404
app.error_handlers[500] = handle_500
