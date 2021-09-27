from flask import Blueprint, render_template, current_app, __version__ as flaskversion
import importlib


__version__ = '0.1.0'


def info():
    blueprints = {}
    for b in current_app.blueprints:
        modul = importlib.import_module(current_app.blueprints[b].__class__.__module__)
        blueprints[current_app.blueprints[b].__class__.__name__] = {'name': current_app.blueprints[b].__class__.__name__, 'version': modul.__version__}
    return render_template('info.html', version=current_app.config.get("VERSION", "0.0.0"), flaskversion=flaskversion, blueprints=[blueprints[b] for b in blueprints])


class Info(Blueprint):
    def __init__(self, name='info', import_name=__name__, *args, **kwargs):
        Blueprint.__init__(self, name, import_name, template_folder='templates', *args, **kwargs)
        self.add_url_rule('/info', 'info', info, methods=['GET'])

    def register(self, app, options):
        try:
            Blueprint.register(self, app, options)
        except:
            app.logger.error("init info on register is failed")