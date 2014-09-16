## index.html
<%inherit file="base.mako"/>

<%block name="script">
    <!-- Add more script imports here! -->
    <script src="/static/bootbox.min.js"></script>

</%block>

<%block name="css">
    <!-- Add more css imports here! -->
    <link rel="stylesheet" type="text/css" href="/static/test_op.css">
</%block>

<%block name="title">
    oictest application
</%block>

<%block name="header">
    ${parent.header()}
</%block>

<%block name="headline">
    <div menu></div>

    <!--
    <a href="#" data-placement="bottom" data-toggle="tooltip" class="tip-bottom" data-original-title="Tooltip on bottom">Tooltip on bottom</a>
    -->

    <div ng-controller="IndexCtrl">
</%block>


<%block name="body">

    <div ng-click="toggleInstructionVisibility();" ng-show="instructionVisible == true" id="instructions">
        <img src="static/pitures/arrowDown.png">
        Hide instructions
    </div>

    <div ng-click="toggleInstructionVisibility();" ng-show="instructionVisible == false" id="instructions">
        <img src="static/pitures/arrowRight.png">
        Show instructions
    </div>

    <!-- The information box -->
    <div class="informationBox" ng-show="instructionVisible == true">
        <div class="row" id="no-hover">

            <div class="col-xs-12 col-md-9">
                <p>
                In the table bellow all tests are presented. Test which depend on others are
                makred with a little black arrow. In order to see the subtests press the row containing an arrow.
                </p>
                <p>
                Tests could be executed at three levels. First of a single test could be executed or a test and
                it's subtests could be executed. In order to do this press the button "Run test" and then choose the appropriate alternative.
                Then last alternative is to execute all tests by pressing the button "Run all tests".
                </p>
                <p>
                The result of the tests are presented by color encoding the row containing the test and a written status.
                In order to get a more detailed version of the test result press the button "Show result". If you want
                even mote information press the "trace log" button at the end of the result. The result
                of the test could be exported to either excel or a text file, by pressing the button export and choose
                the appropriate alternative.
                </p>
                <p>
                If any questions about the test result occurs you could send an Error report to DIRG. The latest test
                result will attached to the error report.
                </p>
            </div>

            <div class="col-xs-12 col-md-3">
                <div class="colorExampleBox" id="totalStatusINFORMATION">
                    INFORMATION
                </div>

                <div class="colorExampleBox" id="totalStatusOK">
                    OK
                </div>

                <div class="colorExampleBox" id="totalStatusWARNING">
                    WARNING
                </div>

                <div class="colorExampleBox" id="totalStatusINTERACTION">
                    INTERACTION
                </div>

                <div class="colorExampleBox" id="totalStatusERROR">
                    ERROR
                </div>

                <div class="colorExampleBox" id="totalStatusCRITICAL">
                    CRITICAL
                </div>
          </div>
        </div>
    </div>

    <br>

    <!-- The headline of the test table -->
    <div class="col-sm-6" id="testHeadline">
        Test
        <button class="btn btn-primary btn-sm" ng-click="showModalWindowsErrorReport();">Send error report</button>
    </div>

    <div class="col-sm-2" id="testHeadline">
        Status
    </div>

    <!-- Export button -->
    <div class="col-sm-2" id="testHeadline">
        <div class="btn-group">
            <button type="button" class="btn btn-primary btn-sm dropdown-toggle" data-toggle="dropdown">
                Export
                <span class="caret"></span>
            </button>
            <ul class="dropdown-menu">
                <li ng-click="exportTestResultToTextFile();"><a>Export result to text file</a></li>
                <li ng-click="exportTestResultToExcel();"><a>Export result to excel file</a></li>
            </ul>
        </div>
    </div>

    <!-- Run all tests button-->
    <div class="col-sm-2" id="testHeadline">
        <button class="btn btn-primary" ng-click="runAllTest();">Run all tests</button>
    </div>

    <br>

    <!-- The code which generates the rows of the test table -->
    <div ng-repeat="data in currentFlattenedTree" class="row">

        <div ng-show="data.visible == true" id="testRow">

            <!-- Tree containging all the tests -->
            <div class="col-sm-6" id="totalStatus{{data.status}}" ng-click="toggleTestsVisibility(data.testid);">
                <div id="level{{data.level}}">

                    <span class="glyphicon glyphicon-info-sign" title="{{data.descr}}" id="infoIcon"
                          data-toggle="tooltip" data-placement="right" directive-callback="{{$last}}"></span>

                    <img src="static/pitures/arrowRight.png" ng-show="data.hasChildren == true">

                    <span ng-click="removeTestResult(data.testid);" rel="tooltip" title="{{data.descr}}">{{data.id}}</span>
                </div>
            </div>

            <!-- Status of a given test -->
            <div class="col-sm-2" id="totalStatus{{data.status}}">
                {{data.status}}
             </div>

            <!-- Show or hide result button -->
            <div class="col-sm-2" id="totalStatus{{data.status}}">
                <div class="btn btn-default btn-xs" ng-click="toggleResultVisibility(data.testid, {{$index}});" id="resultButton{{$index}}">Show result</div>
            </div>

            <!-- Run test buttons -->
            <div class="col-sm-2" id="totalStatus{{data.status}}">

                <div class="btn-group">
                    <button class="btn btn-primary btn-sm dropdown-toggle" data-toggle="dropdown" id="runButton">
                        Run test
                        <span class="caret"></span>
                    </button>
                    <ul class="dropdown-menu">
                        <li ng-click="runTestAndSubTests(data.testid);"><a>Run test and subtests</a></li>
                        <li ng-click="runOneTest(data.id, data.testid, TestRunningModesEnum.SINGLE_TEST);"><a>Run this test only</a></li>
                    </ul>
                </div>

            </div>

            <br>

            <!-- Result frame containing the result of a executed test -->
            <div class="resultFrame" ng-show="data.showResult == true">
                <b>Result:</b>
                <br>

                <div ng-repeat="test in data.result">Status: <b>{{test.status}}</b> : {{test.name}}{{test.message}} : {{test.id}}{{test.content}}</div>

                <button class="btn btn-default btn-xs" ng-click="toggleTraceLogVisibility(data.testid, {{$index}});" id="traceLogButton{{$index}}">Show trace log</button>

                <div ng-show="data.showTraceLog == true">
                    <b>Trace log:</b>
                    <br>

                    <div ng-repeat="trace in data.traceLog" ng-bind-html-unsafe="trace.traceMessage"></div>
                </div>
            </div>
        </div>
    </div>
</%block>

<%block name="footer">
    </div>

    <!-- Modal window containg iframe-->
    <div class="modal fade" id="modalWindowIframe" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">
        <div class="modal-dialog">
            <div class="modal-content" id="modalIframeContent">

            </div>
        </div>
    </div>

    <!-- Modal window for error report-->
    <div class="modal fade" id="modalWindowErrorReport" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">
        <div class="modal-dialog">
            <div class="modal-content" id="modalErrorReportContent">

                <form id="reportForm">
                    <span>If you have questions about the result of a test run you could sent a a question to us using the form below. In order for us to get a better understanding of your problem the result of the last test will be attached to the mail.</span>

                    <input type="email" class="form-control" placeholder="Your Email" id="reportEmail">
                    <textarea class="form-control" rows="3" placeholder="Text" id="reportMessage"></textarea>

                    <button class="btn btn-primary btn-sm" ng-click="sendReport();">Send report</button>
                </form>
            </div>
        </div>
    </div>

    <script type="text/javascript" src="/static/test_op.js"></script>

    ${parent.footer()}
</%block>