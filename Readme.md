         ______ _____   _______ _______ _______
        |   __ \     |_|   |   |     __|   |   |
        |    __/       |   |   |__     |       |
        |___|  |_______|_______|_______|___|___|

# Introduction

_Plush_ is a micro web framework for Python, inspired by the current generation
framework super stars like *Sinatra*, *Express* and *Flask*. It builds on top
of the excelent *Tornado* web server, making _Plush_ light, fast and fully
asynchronous.

# Features

* Pythonic DSL-like interface
* Asynchronous code execution
* Easily configurable

# Example

    from plush import Plush

    app = Plush(__name__)

    @app.get(r'/')
    def index(request):
        request.send('Hello World!')

    app.run()

That's it. By default it will run a webserver on the _8088_ port.

# Documentation

Watch the wiki for updates.

# License

Copyright 2011 Genadi Samokovarov

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
