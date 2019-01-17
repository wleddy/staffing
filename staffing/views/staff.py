from flask import request, session, g, redirect, url_for, abort, \
     render_template, flash, Blueprint
from shotglass2.users.admin import login_required, table_access_required
from shotglass2.takeabeltof.utils import render_markdown_for, printException
from shotglass2.takeabeltof.date_utils import datetime_as_string

mod = Blueprint('staffing',__name__, template_folder='templates/staffing', url_prefix='')


def setExits():
    g.homeURL = url_for('.home')
    g.aboutURL = url_for('www.about')
    g.contactURL = url_for('www.contact')
    g.title = 'Home'

@mod.route('/index.html')
@mod.route('/index.htm')
@mod.route('/')
def home():
    setExits()
    g.title = 'Home'
    g.suppress_page_header = True
    rendered_html = render_markdown_for('index.md',mod)

    return render_template('index.html',rendered_html=rendered_html,)

