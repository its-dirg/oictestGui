# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 9
_modified_time = 1387548934.547166
_enable_loop = True
_template_filename = 'mako/htdocs/op_config.mako'
_template_uri = 'op_config.mako'
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
        

        # SOURCE LINE 7
        __M_writer(u'\n\n')
        if 'parent' not in context._data or not hasattr(context._data['parent'], 'css'):
            context['self'].css(**pageargs)
        

        # SOURCE LINE 12
        __M_writer(u'\n\n')
        if 'parent' not in context._data or not hasattr(context._data['parent'], 'title'):
            context['self'].title(**pageargs)
        

        # SOURCE LINE 16
        __M_writer(u'\n\n')
        if 'parent' not in context._data or not hasattr(context._data['parent'], 'header'):
            context['self'].header(**pageargs)
        

        # SOURCE LINE 20
        __M_writer(u'\n\n')
        if 'parent' not in context._data or not hasattr(context._data['parent'], 'headline'):
            context['self'].headline(**pageargs)
        

        # SOURCE LINE 26
        __M_writer(u'\n\n\n')
        if 'parent' not in context._data or not hasattr(context._data['parent'], 'body'):
            context['self'].body(**pageargs)
        

        # SOURCE LINE 180
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
        # SOURCE LINE 29
        __M_writer(u'\n\n    <div id="content">\n\n        <h2>IDP configuration:\n            <button class="btn btn-primary btn-sm" ng-click="reloadConfigFile();">\n                <span class="glyphicon glyphicon-refresh"></span>\n            </button>\n        </h2>\n\n        <form>\n            <div class="row">\n                <div class="col-lg-2">\n                    Create new config:\n                </div>\n\n                <div class="col-lg-10">\n                    <button class="btn btn-primary btn-sm" ng-click="sendCreateNewConfigFileRequest();">Create configurations</button>\n                    <br>\n                    <br>\n                </div>\n            </div>\n\n             <div class="row">\n                <div class="col-lg-2">\n                    Upload config file:\n                </div>\n\n                <div class="col-lg-10">\n\n                    <input type="file" name="file" id="targetFile">\n                    <button class="btn btn-primary btn-sm" ng-click="requestUploadConfigFile();">Upload configurations</button>\n                    <br>\n                    <br>\n                </div>\n            </div>\n\n             <div class="row">\n                <div class="col-lg-2">\n                    Download config file:\n                </div>\n\n                <div class="col-lg-10">\n                    <button class="btn btn-primary btn-sm" ng-click="requestDownloadConfigFile();">Download configurations</button>\n                </div>\n            </div>\n        </form>\n\n        <hr>\n\n        <!-- HIDE EVERY THING UNDER THIS LINE UNTIL DATA IS STORED IN THE SESSION -->\n\n<!-- ################################################################################################# -->\n        <div ng-show="providerConfigurations">\n            <form>\n                <div class="row">\n                    <div class="col-lg-2">\n                        Upload metadata file:\n                    </div>\n\n                    <div class="col-lg-10">\n                        <input type="file" name="file" id="metadataFile">\n                        <button class="btn btn-primary btn-sm" ng-click="uploadMetadataFile();">Upload</button>\n                        <br>\n                        <br>\n                    </div>\n                </div>\n\n                <div class="row">\n                    <div class="col-lg-2" id="label">\n                        Upload metadata by url:\n                    </div>\n\n                    <div class="col-lg-10">\n                        <input type="text" value="https://localhost:4545/temp_get_metadata" id="metadataUrl">\n                        <button class="btn btn-primary btn-sm" ng-click="uploadMetadataUrl();">Upload</button>\n                        <br>\n                        <br>\n                    </div>\n                </div>\n\n                <hr>\n<!-- ################################################################################################# -->\n\n                <div class="row" ng-repeat="(key, data) in providerConfigurations">\n                    <div class="col-lg-2" id="label">\n                        {{key}}:\n                    </div>\n\n                    <div class="col-lg-10">\n                        <input type="text" value="{{data}}" id="{{key}}">\n                    </div>\n                </div>\n            </form>\n\n            <button class="btn btn-primary btn-sm" ng-click="saveBasicConfig();">Save configurations</button>\n\n            <hr>\n<!-- ################################################################################################# -->\n\n            Interaction: <button class="btn btn-default btn-sm" ng-click="addInteraction();">+</button>\n\n            <div class="block" ng-repeat="entry in convertedInteractionList" id="{{entry.id}}">\n                <form>\n                    id:{{entry.id}}\n\n                    <div class="row" ng-repeat="(key, data) in entry.entry.matches">\n                        <div class="col-lg-2">\n                            {{key}}:\n                        </div>\n\n                        <div class="col-lg-10">\n                            <input type="text" value="{{data}}" id="{{key}}">\n                        </div>\n                        <br>\n                    </div>\n\n                    <div class="row">\n                        <div class="col-lg-2">\n                            page-type:\n                        </div>\n\n                        <div class="col-lg-10">\n                            <input type="text" value="{{entry.entry.pagetype}}" id="pagetype">\n                        </div>\n                        <br>\n                    </div>\n\n                    <div class="row" ng-repeat="(key, data) in entry.entry.control">\n                        <div class="col-lg-2">\n                            {{key}}:\n                        </div>\n\n                        <div class="col-lg-10">\n                            <input type="text" value="{{data}}" id="{{key}}">\n                        </div>\n                        <br>\n                    </div>\n\n                </form>\n\n                <div class="close">\n                    <button class="btn btn-danger btn-sm" ng-click="createConfirmRemoveInteractionBlockDialog(entry.id);">X</button>\n                </div>\n            </div>\n\n            <br>\n\n            <button class="btn btn-primary btn-sm" ng-click="postInteractionConfig();">Save configurations</button>\n        </div>\n    </div>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_title(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        def title():
            return render_title(context)
        __M_writer = context.writer()
        # SOURCE LINE 14
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
        # SOURCE LINE 22
        __M_writer(u'\n    <div ng-controller="IndexCtrl">\n\n    <script language="JavaScript" type="text/javascript" src="/static/menu.js"></script>\n')
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
        __M_writer(u'\n    <!-- Add more script imports here! -->\n    <script src="/static/bootbox.min.js" xmlns="http://www.w3.org/1999/html"></script>\n')
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
        # SOURCE LINE 18
        __M_writer(u'\n    ')
        # SOURCE LINE 19
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
        # SOURCE LINE 182
        __M_writer(u'\n    </div>\n\n    <script type="text/javascript" src="/static/op_config.js"></script>\n\n    ')
        # SOURCE LINE 187
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
        # SOURCE LINE 9
        __M_writer(u'\n    <!-- Add more css imports here! -->\n    <link rel="stylesheet" type="text/css" href="/static/op_config.css">\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


