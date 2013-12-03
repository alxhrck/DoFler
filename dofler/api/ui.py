from bottle import Bottle, request, response, redirect, static_file, error
from sqlalchemy.sql import func, label
from bottle.ext import sqlalchemy
from jinja2 import Environment, FileSystemLoader
from ConfigParser import ConfigParser
from dofler import config
from dofler import common
from dofler.common import auth, auth_login, setting
from dofler.models import *
from dofler.db import engine, Base, SettingSession
from dofler import monitor

env = Environment(
    lstrip_blocks=True,
    trim_blocks=True,
    loader=FileSystemLoader('/usr/share/dofler/templates')
)
app = Bottle()
plugin = sqlalchemy.Plugin(
    engine,Base.metadata, keyword='db', create=True, 
    commit=True, use_kwargs=False
)
app.install(plugin)


def update_settings(settings):
    '''
    Settings Updater 
    '''
    s = SettingSession()
    for item in settings:
        if item == 'database':
            config.update(settings[item])
        else:
            settingobj = setting(item)
            if item == 'server_password':
                if settings[item] != '1234567890':
                    settingobj.value = settings[item]
            else:
                settingobj.value = settings[item]
            s.merge(settingobj)
    s.commit()
    s.close()
    common.log_to_console()
    common.log_to_file()
    monitor.autostart()


@app.get('/')
def main_page(db):
    '''
    Main View
    '''
    return env.get_template('main.html').render(
        auth=auth(request), 
        web_images=setting('web_images').boolvalue,
        web_accounts=setting('web_accounts').boolvalue,
        web_stats=setting('web_stats').boolvalue,
        web_image_delay=setting('web_image_delay').intvalue,
        web_account_delay=setting('web_account_delay').intvalue,
        web_stat_delay=setting('web_stat_delay').intvalue,
        web_image_max=setting('web_image_max').intvalue,
        web_account_max=setting('web_account_max').intvalue,
        web_stat_max=setting('web_stat_max').intvalue,
        web_display_settings=setting('web_display_settings').boolvalue
    )


@app.get('/static/<path:path>')
def static_files(path):
    return static_file(path, root='/usr/share/dofler/static')


@app.get('/settings')
def settings_page(db):
    '''
    Settings Page
    '''
    return env.get_template('settings_base.html').render(
        auth=auth(request))


@app.get('/settings/login')
@app.post('/settings/login')
def login(db):
    '''
    Authentication Page
    '''
    note=None
    error=None
    logged_in=False
    if request.method == 'POST':
        if auth_login(request):
            response.set_cookie('user', 
                request.forms.get('username'), 
                secret=setting('cookie_key').value
            )
            response.add_header('Authentication', 'SUCCESS')
            note='Login Successful'
            logged_in=True
        else:
            error='Authentication Failed'
    return env.get_template('settings_base.html').render(
        auth=logged_in,
        note=note,
        error=error
    )


@app.get('/settings/users')
@app.post('/settings/users')
def user_settings(db):
    '''
    User Management Page
    '''
    if auth(request) and request.method == 'POST':
        username = request.forms.get('username')
        password = request.forms.get('password')
        action = request.forms.get('action')
        if action == 'Create':
            db.add(User(username, password))
        if action == 'Update':
            user = db.query(User).filter_by(name=username).one()
            user.update(password)
            db.merge(user)
        if action == 'Remove' and username != 'admin':
            user = db.query(User).filter_by(name=username).one()
            db.delete(user)
    return env.get_template('settings_users.html',
        auth=auth(request),
        users=db.query(User).all()
    )


@app.get('/settings/api')
@app.post('/settings/api')
def api_settings(db):
    '''
    API Settings Page 
    '''
    if auth(request) and request.method == 'POST':
        settings = {}
        for item in request.forms:
            settings[item] = request.forms[item]
        update_settings(settings)
    return env.get_template('settings_api.html',
        auth=auth(request),
        api_debug=setting('api_debug').intvalue,
        api_port=setting('api_port').value,
        api_host=setting('api_host').value,
        api_app_server=setting('api_app_server').value,
        cookie_key=setting('cookie_key').value,
        database=config.config.get('Database', 'db')
    )


@app.get('/settings/server')
@app.post('/settings/server')
def api_settings(db):
    '''
    Server Settings Page 
    '''
    if auth(request) and request.method == 'POST':
        settings = {}
        for item in request.forms:
            settings[item] = request.forms[item]
        update_settings(settings)
    return env.get_template('settings_server.html',
        auth=auth(request),
        server_host=setting('server_host').value,
        server_port=setting('server_port').value,
        server_ssl=setting('server_ssl').intvalue,
        server_anonymize=setting('server_anonymize').intvalue,
        server_username=setting('server_username').value
    )


@app.get('/settings/logging')
@app.post('/settings/logging')
def api_settings(db):
    '''
    Logging Settings Page 
    '''
    if auth(request) and request.method == 'POST':
        settings = {}
        for item in request.forms:
            settings[item] = request.forms[item]
        update_settings(settings)
    return env.get_template('settings_logging.html',
        auth=auth(request),
        log_console=setting('log_console').intvalue,
        log_console_level=setting('log_console_level').value,
        log_file=setting('log_file').intvalue,
        log_file_level=setting('log_file_level').value,
        log_file_path=setting('log_file_path').value
    )


@app.get('/settings/webui')
@app.post('/settings/webui')
def api_settings(db):
    '''
    WebUI Settings Page 
    '''
    if auth(request) and request.method == 'POST':
        settings = {}
        for item in request.forms:
            settings[item] = request.forms[item]
        update_settings(settings)
    return env.get_template('settings_webui.html',
        auth=auth(request),
        web_images=setting('web_images').boolvalue,
        web_accounts=setting('web_accounts').boolvalue,
        web_stats=setting('web_stats').intvalue,
        web_image_delay=setting('web_image_delay').value,
        web_account_delay=setting('web_account_delay').value,
        web_stat_delay=setting('web_stat_delay').value,
        web_stat_max=setting('web_stat_max').intvalue,
        web_display_settings=setting('web_display_settings').boolvalue
    )


@app.get('/settings/services')
@app.post('/settings/services')
def services_settings(db):
    '''
    Services Status Page 
    '''
    if auth(request) and request.method == 'POST':
        parser = request.forms.get('parser')
        action = request.forms.get('action')
        if action == 'Stop':
            monitor.stop(parser)
        if action == 'Start':
            monitor.start(parser)
        if action == 'Restart':
            monitor.stop(parser)
            monitor.start(parser)
    return env.get_template('settings_services.html',
        auth=auth(request),
        parsers=monitor.parser_status()
    )


@app.get('/settings/parsers')
@app.post('/settings/parsers')
def parsers_settings(db):
    '''
    Parser Configuration Settings Page
    '''
    if auth(request) and request.method == 'POST':
        settings = {}
        for item in request.forms:
            settings[item] = request.forms[item]
        update_settings(settings)
    plist = monitor.parser_status()
    parsers = {}
    for item in plist:
        parsers[item]['enabled'] = setting('%s_enabled' % item)
        parsers[item]['command'] = setting('%s_command' % item)
    return env.get_template('settings_parsers.html',
        auth=auth(request),
        parsers=parsers,
        autostart=setting('autostart'),
        listen_interface=setting('listen_interface')
    )