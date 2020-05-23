from flask import Blueprint, render_template, current_app

def register():
    return render_template('register.html')

class Register(Blueprint):
    def __init__(self, name='register', import_name=__name__, *args, **kwargs):
        Blueprint.__init__(self, name, import_name, template_folder='templates', *args, **kwargs)
        self.add_url_rule('/register', 'register', register, methods=['GET'])

    def register(self, app, options, first_registration=False):
        try:
            Blueprint.register(self, app, options, first_registration)
        except:
            app.logger.error("init register on register is failed")