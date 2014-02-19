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

        <h2>IDP configuration:
            <button class="btn btn-primary btn-sm" ng-click="reloadConfigFile();">
                <span class="glyphicon glyphicon-refresh"></span>
            </button>
        </h2>

        <form>
            <div class="row">
                <div class="col-lg-2">
                    Create new config:
                </div>

                <div class="col-lg-10">
                    <button class="btn btn-primary btn-sm" ng-click="createNewConfigFile();">Create configurations</button>
                    <br>
                    <br>
                </div>
            </div>

             <div class="row">
                <div class="col-lg-2">
                    Upload config file:
                </div>

                <div class="col-lg-10">

                    <input type="file" name="file" id="targetFile">
                    <button class="btn btn-primary btn-sm" ng-click="uploadConfigFile();">Upload configurations</button>
                    <br>
                    <br>
                </div>
            </div>

             <div class="row">
                <div class="col-lg-2">
                    Download config file:
                </div>

                <div class="col-lg-10">
                    <button class="btn btn-primary btn-sm" ng-click="downloadConfigFile();">Download configurations</button>
                </div>
            </div>
        </form>

        <hr>

        <!-- HIDE EVERY THING UNDER THIS LINE UNTIL DATA IS STORED IN THE SESSION -->

<!-- ################################################################################################# -->

        <div ng-show="basicConfig" >
            <button class="btn btn-primary btn-sm" ng-click="showModalWindowAddConfigFields();">Add new config fields</button>
            <br>

             <form>
                <div class="row" ng-repeat="row in configFieldsViewList">
                    <div class="col-lg-2">
                        <span>{{row.label}}</span>
                    </div>

                    <div class="col-lg-9">
                        <input type="text" value="{{row.value}}" class="{{row.id}}">
                    </div>

                    <div class="col-lg-1">
                        <button ng-show="row.isList == true" class="btn btn-default btn-sm" ng-click="addElementToList($index, row.label);">+</button>
                        <button ng-show="row.isListElement == true" class="btn btn-danger btn-sm" ng-click="removeElementFromList($index);">X</button>
                    </div>

                </div>
            </form>

            <!--
            <form>
                <div class="row" ng-repeat="(key, data) in basicConfig">
                    <div class="col-lg-2" id="label">
                        {{key}}:
                    </div>

                    <div class="col-lg-10">
                        <input type="text" value="{{data}}" id="{{key}}">
                    </div>
                </div>
            </form>
            -->



            <button class="btn btn-primary btn-sm" ng-click="saveBasicConfig();">Save configurations</button>

            <hr>
<!-- ################################################################################################# -->

            Interaction: <button class="btn btn-default btn-sm" ng-click="addInteraction();">+</button>

            <div class="block" ng-repeat="entry in convertedInteractionList" id="{{entry.id}}">
                <form>

                    <div class="row" ng-repeat="(key, data) in entry.entry.matches">
                        <div class="col-lg-2">
                            {{key}}:
                        </div>

                        <div class="col-lg-10">
                            <input type="text" value="{{data}}" id="{{key}}">
                        </div>
                        <br>
                    </div>

                    <div class="row">
                        <div class="col-lg-2">
                            page-type:
                        </div>

                        <div class="col-lg-10">
                            <input type="text" value="{{entry.entry.pagetype}}" id="pagetype">
                        </div>
                        <br>
                    </div>

                    <div class="row" ng-repeat="(key, data) in entry.entry.control">
                        <div class="col-lg-2">
                            {{key}}:
                        </div>

                        <div class="col-lg-10">
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

            <!-- Modal window for error report-->
    <div class="modal fade" id="modalWindowAddConfigFields" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">
        <div class="modal-dialog">
            <div class="modal-content">
                <div id="infoText">
                    Mark the fields you want to show on the config page
                </div>


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

    <script type="text/javascript" src="/static/idp_config.js"></script>
    ${parent.footer()}
</%block>