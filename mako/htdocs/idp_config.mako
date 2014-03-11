## index.html
<%inherit file="base.mako"/>

<%block name="script">
    <!-- Add more script imports here! -->
    <script src="/static/bootbox.min.js" xmlns="http://www.w3.org/1999/html"></script>
</%block>

<%block name="css">
    <!-- Add more css imports here! -->
    <link rel="stylesheet" type="text/css" href="/static/idp_config.css">
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
            OC configuration:
            <button class="btn btn-primary btn-sm" ng-click="reloadConfigFile();">
                <span class="glyphicon glyphicon-refresh"></span>
            </button>
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
                <button class="btn btn-primary btn-sm" ng-click="downloadConfigFile();">
                    <span class="glyphicon glyphicon-download-alt"></span>
                    Download configurations
                </button>
            </div>
        </div>

        <hr>

        <!-- HIDE EVERY THING UNDER THIS LINE UNTIL DATA IS STORED IN THE SESSION -->

<!-- ################################################################################################# -->

        <div ng-show="basicConfig" >

            <h3>
                Provider configuration:
            </h3>

            <select id="providerType">
                <option value="default" ng-click="updateProviderConfigurationBySelecedProviderType()">- Select provider type -</option>
                <option value="static" ng-click="updateProviderConfigurationBySelecedProviderType()">Static provider</option>
                <option value="dynamic" ng-click="updateProviderConfigurationBySelecedProviderType()">Dynamic provider</option>
            </select>
            <br>

            <button class="btn btn-default btn-sm" ng-click="showModalWindowAddConfigFields();" ng-show="isStaticProvider == true">Add new provider config fields</button>

            <div class="row" ng-repeat="row in configFieldsViewList">
                <div class="col-sm-4">
                    <span>{{row.label}}</span>
                </div>

                <div class="col-sm-7">
                    <form>
                    <input type="text" value="{{row.value}}" class="{{row.id}}">
                    </form>
                </div>

                <div class="col-sm-1">
                    <button ng-show="row.isList == true" class="btn btn-default btn-sm" ng-click="addElementToList($index, row.label);">+</button>
                    <button ng-show="row.isListElement == true" class="btn btn-danger btn-sm" ng-click="removeElementFromList($index);">X</button>
                </div>

            </div>

            <br>
            <button class="btn btn-primary btn-sm" ng-click="postBasicConfig();">Save configurations</button>

            <hr>

<!-- ################################################################################################# -->
            <h3>
                Required information:
            </h3>

            <div class="row">
                <div class="col-sm-4">
                    Do you application support dynamic client registration?
                </div>
                <div class="col-sm-8">
                    <select id="dynamicRegistration">'
                        <option value="default">-</option>
                        <option value="yes" ng-click="updateRequiredDynamicClientRegistrationFields()">Yes</option>
                        <option value="no" ng-click="updateRequiredDynamicClientRegistrationFields()">No</option>
                    </select>



     <%doc>               <select ng-model="color" ng-options="c.option for c in supportsDynamicClientRegistrationOptions">
                        <option value="">-</option>
                    </select></%doc>
                </div>
            </div>

            <div ng-show="supportsDynamicClientRegistration == false" >
                <div class="row">
                    <div class="col-sm-4">
                        Client_id:
                    </div>
                    <div class="col-sm-8">
                        <input type="text">
                    </div>
                </div>

                <div class="row">
                    <div class="col-sm-4">
                        Client_secret:
                    </div>
                    <div class="col-sm-8">
                        <input type="text">
                    </div>
                </div>
            </div>
            <hr>

<!-- ################################################################################################# -->

            <h3>
                Interaction:
                <button class="btn btn-default btn-sm" ng-click="addInteraction();">+</button>
            </h3>

            <div class="block" ng-repeat="entry in convertedInteractionList" id="{{entry.id}}">
                <form>

                    <div class="row" ng-repeat="(key, data) in entry.entry.matches">
                        <div class="col-sm-2">
                            {{key}}:
                        </div>

                        <div class="col-sm-10">
                            <input type="text" value="{{data}}" id="{{key}}">
                        </div>
                        <br>
                    </div>

                    <div class="row">
                        <div class="col-sm-2">
                            page-type:
                        </div>

                        <div class="col-sm-10">
                            <input type="text" value="{{entry.entry.pagetype}}" id="pagetype">
                        </div>
                        <br>
                    </div>

                    <div class="row" ng-repeat="(key, data) in entry.entry.control">
                        <div class="col-sm-2">
                            {{key}}:
                        </div>

                        <div class="col-sm-10">
                            <input type="text" value="{{data}}" id="{{key}}">
                        </div>
                        <br>
                    </div>

                </form>

                <div class="close">
                    <button class="btn btn-danger btn-sm" ng-click="tryToRemoveInteraction(entry.id);">X</button>
                </div>
            </div>

            <br>

            <button class="btn btn-primary btn-sm" ng-click="saveInteractionConfig();">Save configurations</button>
        </div>
    </div>
</%block>

<%block name="footer">
    </div>
    <div class="modal fade" id="modalWindowAddConfigFields" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">
        <div class="modal-dialog">
            <div class="modal-content">
                Mark the fields you want to show on the config page

                <div id="advancedFieldTable">
                    <table class="table table-striped">
                        <tr ng-repeat="fieldName in configFieldsKeyList">
                            <td><input type="checkbox" value="{{fieldName}}"></td>
                            <td>{{fieldName}}</td>
                        <tr>
                    </table>
                </div>

                <button class="btn btn-primary btn-sm" ng-click="summitAdvancedConfigFields();">Update fields</button>
            </div>
        </div>
    </div>

    <div class="modal fade" id="modalWindowUploadConfigurationFile" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">
        <div class="modal-dialog">
            <div class="modal-content">
                <input type="file" name="file" id="targetFile">
                <button class="btn btn-primary btn-sm" ng-click="uploadConfigFile();">Upload configurations</button>
            </div>
        </div>
    </div>

    <script type="text/javascript" src="/static/idp_config.js"></script>
    ${parent.footer()}
</%block>