from flask import Blueprint, render_template

def info():
    return render_template('info.html')

class Info(Blueprint):
    def __init__(self, name='info', import_name=__name__, *args, **kwargs):
        Blueprint.__init__(self, name, import_name, template_folder='templates', *args, **kwargs)
        self.add_url_rule('/info', 'info', info, methods=['GET'])

    def register(self, app, options, first_registration=False):
        try:
            Blueprint.register(self, app, options, first_registration)
        except:
            app.logger.error("init info on register is failed")