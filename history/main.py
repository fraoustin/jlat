from flask import Blueprint, render_template, current_app

def history():
    return render_template('history.html')

class History(Blueprint):
    def __init__(self, name='history', import_name=__name__, archives="./archives", *args, **kwargs):
        Blueprint.__init__(self, name, import_name, template_folder='templates', *args, **kwargs)
        self.add_url_rule('/history', 'history', history, methods=['GET'])

    def register(self, app, options, first_registration=False):
        try:
            Blueprint.register(self, app, options, first_registration)
        except:
            app.logger.error("init history on register is failed")