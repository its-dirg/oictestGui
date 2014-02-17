# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 9
_modified_time = 1392299614.709035
_enable_loop = True
_template_filename = 'mako/htdocs/home.mako'
_template_uri = 'home.mako'
_source_encoding = 'utf-8'
_exports = [u'body', u'title', u'headline', u'script', u'header', u'footer', u'css']


def _mako_get_namespace(context, name):
    try:
        return context.namespaces[(__name__, name)]
    except KeyError:
        _mako_generate_namespaces(context)
        return context.namespaces[(__name__, name)]
def _mako_generate_namespaces(context):
    pass
def _mako_inherit(template, context):
    _mako_generate_namespaces(context)
    return runtime._inherit_from(context, u'base.mako', _template_uri)
def render_body(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        def body():
            return render_body(context._locals(__M_locals))
        parent = context.get('parent', UNDEFINED)
        def title():
            return render_title(context._locals(__M_locals))
        def headline():
            return render_headline(context._locals(__M_locals))
        def script():
            return render_script(context._locals(__M_locals))
        def header():
            return render_header(context._locals(__M_locals))
        def footer():
            return render_footer(context._locals(__M_locals))
        def css():
            return render_css(context._locals(__M_locals))
        __M_writer = context.writer()
        # SOURCE LINE 2
        __M_writer(u'\n\n')
        if 'parent' not in context._data or not hasattr(context._data['parent'], 'script'):
            context['self'].script(**pageargs)
        

        # SOURCE LINE 6
        __M_writer(u'\n\n')
        if 'parent' not in context._data or not hasattr(context._data['parent'], 'css'):
            context['self'].css(**pageargs)
        

        # SOURCE LINE 10
        __M_writer(u'\n\n')
        if 'parent' not in context._data or not hasattr(context._data['parent'], 'title'):
            context['self'].title(**pageargs)
        

        # SOURCE LINE 14
        __M_writer(u'\n\n')
        if 'parent' not in context._data or not hasattr(context._data['parent'], 'header'):
            context['self'].header(**pageargs)
        

        # SOURCE LINE 18
        __M_writer(u'\n\n')
        if 'parent' not in context._data or not hasattr(context._data['parent'], 'headline'):
            context['self'].headline(**pageargs)
        

        # SOURCE LINE 24
        __M_writer(u'\n\n\n')
        if 'parent' not in context._data or not hasattr(context._data['parent'], 'body'):
            context['self'].body(**pageargs)
        

        # SOURCE LINE 37
        __M_writer(u'\n\n')
        if 'parent' not in context._data or not hasattr(context._data['parent'], 'footer'):
            context['self'].footer(**pageargs)
        

        return ''
    finally:
        context.caller_stack._pop_frame()


def render_body(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        def body():
            return render_body(context)
        __M_writer = context.writer()
        # SOURCE LINE 27
        __M_writer(u'\n\n    <h2>Home page</h2>\n    <span style="font-size:17px">\n        SAML2test is a tests tool that will allow an independent validation\n        of a specific instance of a SAML2 entity. It will test not only if the\n        instance works according to the SAML2 standard but also if it complies\n        with a specific profile of SAML2.\n    </span>\n\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_title(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        def title():
            return render_title(context)
        __M_writer = context.writer()
        # SOURCE LINE 12
        __M_writer(u'\n    Saml2test application\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_headline(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        def headline():
            return render_headline(context)
        __M_writer = context.writer()
        # SOURCE LINE 20
        __M_writer(u'\n    <div menu></div>\n\n    <div ng-controller="IndexCtrl">\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_script(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        def script():
            return render_script(context)
        __M_writer = context.writer()
        # SOURCE LINE 4
        __M_writer(u'\n    <!-- Add more script imports here! -->\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_header(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        def header():
            return render_header(context)
        parent = context.get('parent', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 16
        __M_writer(u'\n    ')
        # SOURCE LINE 17
        __M_writer(unicode(parent.header()))
        __M_writer(u'\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_footer(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        parent = context.get('parent', UNDEFINED)
        def footer():
            return render_footer(context)
        __M_writer = context.writer()
        # SOURCE LINE 39
        __M_writer(u'\n    </div>\n\n    <script type="text/javascript" src="/static/home.js"></script>\n    ')
        # SOURCE LINE 43
        __M_writer(unicode(parent.footer()))
        __M_writer(u'\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_css(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        def css():
            return render_css(context)
        __M_writer = context.writer()
        # SOURCE LINE 8
        __M_writer(u'\n    <!-- Add more css imports here! -->\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


