from flask import current_app, url_for
from flask_script import Command

class ListRoutesCommand(Command):
    def run(self):
        list_routes()

def list_routes():
    import urllib
    output = []
    for rule in current_app.url_map.iter_rules():

        options = {}
        for arg in rule.arguments:
            options[arg] = "[{0}]".format(arg)

        methods = ','.join(rule.methods)
        url = url_for(rule.endpoint, **options)
        line = urllib.parse.unquote("{:50s} {:20s} {}".format(rule.endpoint, methods, url))
        output.append(line)

    for line in sorted(output):
        print(line)
