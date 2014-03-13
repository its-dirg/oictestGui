# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 9
_modified_time = 1394722355.431786
_enable_loop = True
_template_filename = 'mako/htdocs/idp_config.mako'
_template_uri = 'idp_config.mako'
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
        

        # SOURCE LINE 297
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
        __M_writer(u'\n\n    <div id="content">\n\n        <h2>\n            OC configuration:\n            <button class="btn btn-default btn-sm" ng-click="reloadConfigFile();">\n                <span class="glyphicon glyphicon-refresh"></span>\n            </button>\n        </h2>\n\n        <div class="row">\n            <div class="col-sm-4">\n                <button class="btn btn-primary btn-sm" ng-click="createNewConfigFile();">\n                    <span class="glyphicon glyphicon-file"></span>\n                    Create new configurations\n                </button>\n            </div>\n\n            <div class="col-sm-4">\n                <button class="btn btn-primary btn-sm" ng-click="showModalUploadConfigWindow();">\n                    <span class="glyphicon glyphicon-open"></span>\n                    Upload configurations\n                </button>\n            </div>\n\n         <div class="col-sm-4">\n                <button class="btn btn-primary btn-sm" ng-click="downloadConfigFile();">\n                    <span class="glyphicon glyphicon-download-alt"></span>\n                    Download configurations\n                </button>\n            </div>\n        </div>\n\n        <hr>\n\n        <!-- HIDE EVERY THING UNDER THIS LINE UNTIL DATA IS STORED IN THE SESSION -->\n\n<!-- ################################################################################################# -->\n            <h3>\n                Provider configuration:\n            </h3>\n\n            <span>\n                How does the application fetch information from the server?\n            </span>\n\n            <select ng-model="opConfig.fetchInfoFromServerDropDown.value"\n                    ng-options="v.type as v.name for v in opConfig.fetchInfoFromServerDropDown.values"\n                    ng-change="switchBetweenProviderConfigElement();">\n            </select>\n\n            <br>\n\n            <button class="btn btn-default btn-sm"\n                    ng-click="showModalWindowAddConfigFields();"\n                    ng-show="opConfig.fetchStaticInfoFromServer.showInputFields == true">\n                Add new provider config fields\n            </button>\n\n            <div class="row" ng-show="opConfig.fetchDynamicInfoFromServer.showInputFields == true">\n                <div class="col-sm-4">\n                    <span>{{opConfig.fetchDynamicInfoFromServer.inputFields.label}}</span>\n                </div>\n\n                <div class="col-sm-8">\n                    <form>\n                    <input type="text" value="{{opConfig.fetchDynamicInfoFromServer.inputFields.value}}">\n                    </form>\n                </div>\n            </div>\n\n            <div ng-show="opConfig.fetchStaticInfoFromServer.showInputFields == true">\n                <div class="row"\n                     ng-repeat="inputField in opConfig.fetchStaticInfoFromServer.inputFields"\n                     ng-show="inputField.show == true">\n\n                    <div class="col-sm-4">\n                        <span>{{inputField.label}}</span>\n                    </div>\n\n                    <div class="col-sm-7">\n                        <form>\n                        <input type="text" ng-model="inputField.value">\n                        </form>\n                    </div>\n\n                    <div class="col-sm-1">\n                        <button ng-show="inputField.isList == true" class="btn btn-default btn-sm" ng-click="addElementToList($index, row.label);">+</button>\n                        <button ng-show="inputField.isListElement == true" class="btn btn-danger btn-sm" ng-click="removeElementFromList($index);">X</button>\n                    </div>\n                </div>\n            </div>\n\n            <hr>\n\n')
        # SOURCE LINE 272
        __M_writer(u'\n\n            <button class="btn btn-primary btn-sm" ng-click="saveConfigurations();">Save configurations</button>\n        </div>\n    </div>\n\n    <div class="modal fade" id="modalWindowAddConfigFields" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">\n        <div class="modal-dialog">\n            <div class="modal-content">\n                Mark the fields you want to show on the config page\n\n                <div id="advancedFieldTable">\n                    <table class="table table-striped">\n                        <tr ng-repeat="inputField in opConfig.fetchStaticInfoFromServer.inputFields">\n                            <td><input type="checkbox" ng-model="inputField.show"></td>\n                            <td>{{inputField.label}}</td>\n                        <tr>\n                    </table>\n                </div>\n\n                <button class="btn btn-primary btn-sm" ng-click="summitAdvancedConfigFields();">Update fields</button>\n            </div>\n        </div>\n    </div>\n\n')
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
        __M_writer(u'\n    oictest application\n')
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
        # SOURCE LINE 299
        __M_writer(u'\n    </div>\n\n\n    <div class="modal fade" id="modalWindowUploadConfigurationFile" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">\n        <div class="modal-dialog">\n            <div class="modal-content">\n                <input type="file" name="file" id="targetFile">\n                <button class="btn btn-primary btn-sm" ng-click="uploadConfigFile();">Upload configurations</button>\n            </div>\n        </div>\n    </div>\n\n    <script type="text/javascript" src="/static/idp_config.js"></script>\n    ')
        # SOURCE LINE 313
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
        __M_writer(u'\n    <!-- Add more css imports here! -->\n    <link rel="stylesheet" type="text/css" href="/static/idp_config.css">\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


