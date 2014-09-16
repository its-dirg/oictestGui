## index.html
<%inherit file="base.mako"/>

<%block name="script">
    <!-- Add more script imports here! -->
    <script src="/static/bootbox.min.js" xmlns="http://www.w3.org/1999/html"></script>
</%block>

<%block name="css">
    <!-- Add more css imports here! -->
    <link rel="stylesheet" type="text/css" href="/static/op_config.css">
</%block>

<%block name="title">
    oictest application
</%block>

<%block name="header">
    ${parent.header()}
</%block>

<%block name="headline">
    <div menu></div>

    <div ng-controller="IndexCtrl">
</%block>


<%block name="body">

    <div id="content">

        <h2>
            OP configuration:
        </h2>

        <div class="row">
            <div class="col-sm-4">
                <button class="btn btn-primary btn-sm" ng-click="createNewConfigFile();">
                    <span class="glyphicon glyphicon-file"></span>
                    Create new configurations
                </button>
            </div>

            <div class="col-sm-4">
                <button class="btn btn-primary btn-sm" ng-click="showModalUploadConfigWindow();">
                    <span class="glyphicon glyphicon-open"></span>
                    Upload configurations
                </button>
            </div>

            <div class="col-sm-4">
                <button class="btn btn-primary btn-sm" ng-click="requestDownloadConfigFile();">
                    <span class="glyphicon glyphicon-download-alt"></span>
                    Download configurations
                </button>
            </div>
        </div>

        <hr>

        <!-- HIDE EVERY THING UNDER THIS LINE UNTIL DATA IS STORED IN THE SESSION -->

        <!-- ################################################################################################# -->
        <div ng-show="opConfig">
            <h3>
                Provider configuration:
            </h3>

            <span>
                {{opConfig.fetchInfoFromServerDropDown.name}}
            </span>

            <select ng-model="opConfig.fetchInfoFromServerDropDown.value"
                    ng-options="v.type as v.name for v in opConfig.fetchInfoFromServerDropDown.values"
                    ng-change="switchBetweenProviderConfigElement();">
            </select>

            <br>

            <button class="btn btn-default btn-sm"
                    ng-click="showModalWindowAddConfigFields();"
                    ng-show="opConfig.fetchStaticInfoFromServer.showInputFields == true">
                Add new provider config fields
            </button>

            <div class="row" ng-show="opConfig.fetchDynamicInfoFromServer.showInputField == true">
                <div class="col-sm-5">
                    <span>{{opConfig.fetchDynamicInfoFromServer.inputField.label}}</span>
                </div>

                <div class="col-sm-7">
                    <form>
                        <input type="text" ng-model="opConfig.fetchDynamicInfoFromServer.inputField.value">
                    </form>
                </div>
            </div>

            <div ng-show="opConfig.fetchStaticInfoFromServer.showInputFields == true">
                <div class="row"
                     ng-repeat="inputField in opConfig.fetchStaticInfoFromServer.inputFields"
                     ng-show="inputField.show == true">

                    <div class="col-sm-6">
                        <span>{{inputField.label}}</span>
                    </div>

                    <div class="col-sm-6">
                        <form ng-repeat="valueStruct in inputField.values">
                            <div class="input-group">
                                <input type="text" ng-model="valueStruct.textFieldContent" class="form-control">
                               <span class="input-group-btn">
                                    <button ng-show="valueStruct.index > 0" class="btn btn-danger btn-sm"
                                            ng-click="removeElementFromList($parent.$index, $index);">
                                        X
                                    </button>
                                    <button ng-show="inputField.isList == true && valueStruct.index == 0"
                                            class="btn btn-default btn-sm"
                                            ng-click="addElementToList($index);">
                                        +
                                    </button>
                                </span>
                                <span class="input-group-addon" ng-show="inputField.isList == false"></span>
                            </div>
                        </form>
                    </div>
                </div>
            </div>

            <hr>

            <!-- ################################################################################################# -->
            <div ng-show="opConfig.fetchInfoFromServerDropDown.value != ''">
                <h3>
                    Required information:
                </h3>

                <div class="row">
                    <div class="col-sm-12">
                        <span>
                            {{opConfig.dynamicClientRegistrationDropDown.label}}
                        </span>

                        <select ng-model="opConfig.dynamicClientRegistrationDropDown.value"
                                ng-options="v.type as v.name for v in opConfig.dynamicClientRegistrationDropDown.values">
                        </select>
                    </div>
                </div>

                <div ng-show="opConfig.dynamicClientRegistrationDropDown.value == 'no'">
                    <div class="row" ng-repeat="textField in opConfig.supportsStaticClientRegistrationTextFields">
                        <div class="col-sm-4">
                            {{textField.label}}
                        </div>
                        <div class="col-sm-8">
                            <form>
                                <input type="text" ng-model="textField.textFieldContent">
                            </form>
                        </div>
                    </div>
                </div>

                <div class="row">
                    <div class="col-sm-12">
                        <span>
                            {{opConfig.unsupportedLoginFeatures.label}}
                        </span>

                        <select ng-model="opConfig.unsupportedLoginFeatures.value"
                                ng-options="v.type as v.name for v in opConfig.unsupportedLoginFeatures.values">
                        </select>
                    </div>
                </div>

                <hr>

                <!-- ################################################################################################# -->

                <h3>
                    Interaction:
                    <button class="btn btn-default btn-sm" ng-click="addInteractionBlock();">+</button>
                </h3>

                <div class="block" ng-repeat="block in opConfig.interactionsBlocks">
                    <div class="row" ng-repeat="textField in block.inputFields">
                        <div class="col-sm-2">
                            {{textField.label}}:
                        </div>

                        <div class="col-sm-10">
                            <form>
                                <input type="text" ng-model="textField.textFieldContent">
                            </form>
                        </div>
                        <br>
                    </div>

                    <div class="close">
                        <button class="btn btn-danger btn-sm" ng-click="createConfirmRemoveInteractionBlockDialog(block.id);">X
                        </button>
                    </div>
                </div>

                <br>

                <button class="btn btn-primary btn-sm" ng-click="saveConfigurations();">Save configurations</button>
            </div>
        </div>
    </div>
</div>

<div class="modal fade" id="modalWindowAddConfigFields" tabindex="-1" role="dialog" aria-labelledby="myModalLabel"
     aria-hidden="true">
    <div class="modal-dialog">
        <div class="modal-content">
            Mark the fields you want to show on the config page

            <div id="advancedFieldTable">
                <table class="table table-striped">
                    <tr ng-repeat="inputField in opConfig.fetchStaticInfoFromServer.inputFields">
                        <td><input type="checkbox" ng-model="inputField.show"></td>
                        <td>{{inputField.label}}</td>
                    <tr>
                </table>
            </div>
        </div>
    </div>
</div>

<div class="modal fade" id="modalWindowUploadConfigurationFile" tabindex="-1" role="dialog"
     aria-labelledby="myModalLabel" aria-hidden="true">
    <div class="modal-dialog">
        <div class="modal-content">
            <input type="file" name="file" id="targetFile">
            <button class="btn btn-primary btn-sm" ng-click="requestUploadConfigFile();">Upload configurations</button>
        </div>
    </div>
</div>

<!-- Modal window containg iframe-->
<div class="modal fade" id="modalWindowInteraction" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">
    <div class="modal-dialog">
        <div class="modal-content" id="modalWindowInteractionContent">

        </div>
    </div>
</div>

<div class="modal fade" id="modalWindowUploadCookies" tabindex="-1" role="dialog"
     aria-labelledby="myModalLabel" aria-hidden="true">
    <div class="modal-dialog large">
        <div class="modal-content">
            <div class="modal-header">
                <button type="button" class="close" data-dismiss="modal" aria-hidden="true" ng-click="closeUploadCookies()">&times;</button>
                <h4 class="modal-title">Upload cookies</h4>
            </div>
            <div class="modal-body">

                Enter cookies in Netscapt format:
                <textarea class="form-control" rows="10" wrap="off" id="cookieInputTextbox" style="margin-bottom: 5px"></textarea>

                <button class="btn btn-primary btn-sm" ng-click="requestUploadCookies();">
                    <span class="glyphicon glyphicon-open"></span>
                    Upload cookies
                </button>

                <div class="highlight">
                    <h4>Example of a valid cookie in Netscape format:</h4>
                    <br>
                    <table class="table">
                        <tr>
                            <th>Domain</th>
                            <th>Domain starts with .</th>
                            <th>Path</th>
                            <th>Secure</th>
                            <th>Expiring time</th>
                            <th>Cookie name</th>
                            <th>Cookie value</th>
                        </tr>
                        <tr>
                            <td>.example.com</td>
                            <td>TRUE</td>
                            <td>/</td>
                            <td>FALSE</td>
                            <td>1472215093</td>
                            <td>pyoidc</td>
                            <td>GDA8Yh7A6HCkR40RGDA8Yh740R</td>
                        </tr>
                    </table>

                    <b>Note: All values has to separated by tab, the expiring time has to be an integer and if no
                       expiring time exists the cookie would not be stored</b>
                </div>
            </div>
        </div>
    </div>
</div>

</%block>

<%block name="footer">
    </div>

    <script>
        $(document).delegate('#cookieInputTextbox', 'keydown', function(e) {
            var keyCode = e.keyCode || e.which;

            if (keyCode == 9) {
                e.preventDefault();
                var start = $(this).get(0).selectionStart;
                var end = $(this).get(0).selectionEnd;

                // set textarea value to: text before caret + tab + text after caret
                $(this).val($(this).val().substring(0, start)
                        + "\t"
                        + $(this).val().substring(end));

                // put caret at right position again
                $(this).get(0).selectionStart =
                        $(this).get(0).selectionEnd = start + 1;
            }
        });
    </script>

    <script type="text/javascript" src="/static/op_config.js"></script>
    ${parent.footer()}
</%block>