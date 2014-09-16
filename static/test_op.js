
var app = angular.module('main', ['toaster'])

//TODO kanske borde sätta ihop testFactory och runTestFactory.
app.factory('testFactory', function ($http) {
    return {
        getTests: function () {
            return $http.get("/list_tests");
        }
    };
});

app.factory('runTestFactory', function ($http) {
    return {
        getTestResult: function (testname, testUid) {
            return $http.get("/run_test", {params: { "testname": testname, "testid": testUid}});
        },
        getAllTestResult: function (testname) {
            return $http.get("/run_test", {params: { "testname": testname}});
        }
    };
});

app.factory('postResetInteractionFactory', function ($http) {
    return {
        postResetInteraction: function () {
            return $http.post("/reset_interaction");
        }
    };
});

app.factory('errorReportFactory', function ($http) {
    return {
        postErrorReport: function (reportEmail, reportMessage, testResults) {
            return $http.post("/post_error_report", {"reportEmail": reportEmail, "reportMessage": reportMessage, "testResults": testResults});
        }
    };
});

app.controller('IndexCtrl', function ($scope, testFactory, runTestFactory, postResetInteractionFactory, errorReportFactory, toaster) {
    $scope.testResult = "";
    $scope.currentFlattenedTree = "None";
    $scope.numberOfTestsRunning = 0;
    $scope.instructionVisible = false;
    var subTestList;
    var loginContainsUnsupportedFeatures;

    $scope.resultSummary = {'success': 0, 'failed': 0};

    $scope.TestRunningModesEnum = {
        SINGLE_TEST : "singleTest",
        MULTIPLE_TESTS : "multipleTests",
        ALL_TESTS : "allTests"
    }

    function getLoginContainsUnsupportedFeaturesSuccessCallback(data, status, headers, config) {
        loginContainsUnsupportedFeatures = data['loginContainsUnsupportedFeatures']
    }

    /**
     * Callback function which is invoked when the list containing all the tests has been downloaded successfully.
     */
    function getListSuccessCallback(data, status, headers, config) {
        $scope.bottomUpTree = data["bottomUpTree"];

        $scope.currentOriginalTree = $scope.bottomUpTree;
        $scope.currentFlattenedTree = buildFlatTree($scope.bottomUpTree);

        $scope.allTests = getAllTests($scope.currentFlattenedTree);

        $("[data-toggle='tooltip']").tooltip();
    }

    function getAllTests(flatTree){
        var allTestIds = []

        for (var i = 0; i < flatTree.length; i++){
            var testId = flatTree[i]['id'];
            if (allTestIds.indexOf(testId) == -1) {
                allTestIds.push(testId)
            }
        }
        return allTestIds
    }

    var isRunningAllTests = false;

    /**
     * Callback function which is invoked when the a test result is returned. Note that the results always are
     * connected ot single test
     */
     function getTestResultSuccessCallback (data, status, headers, config) {
        if (data['testid'] == null){
            isRunningAllTests = true;
            writeResultToTreeBasedOnId(data);
        }else{
            writeResultToTreeBasedOnTestUid(data);
        }

        $scope.numberOfTestsRunning--;

        if ($scope.numberOfTestsRunning <= 0){
            var resultString = "Successful tests: " + $scope.resultSummary.success + "\n" + " Failed tests: " + $scope.resultSummary.failed
            toaster.pop('note', "Result summary", resultString);
            resetFlags();
        }
    };

    function resetFlags(){
        $('button').prop('disabled', false);
        isRunningAllTests = false;
        hasShownWrongPasswordDialog = false;
        isShowingErrorMessage = false;
        //Reset test summary or else the result of multiply runs for the same test will be presented
        $scope.resultSummary = {'success': 0, 'failed': 0};
    }

    /**
     * Callback function called when the returned data isn't used
     */
    function emptySuccessCallback(data, status, headers, config) {};


    function getPostErrorReportSuccessCallback(data, status, headers, config) {
        alert("getPostErrorReportSuccessCallback");
    };

    var isShowingErrorMessage = false;

    /**
     * Shows error message dialog
     * @param data - The result returned from the server
     * @param status - The status on the response from the server
     * @param headers - The header on the response from the server
     * @param config - The configuration on the response from the server
     */
    var errorCallback = function (data, status, headers, config) {

        if (!isShowingErrorMessage){
            isShowingErrorMessage = true;

            bootbox.alert(data.ExceptionMessage, function() {
                resetFlags();
            });
        }
    };

    testFactory.getTests().success(getListSuccessCallback).error(errorCallback);

    /**
     *  Runs a test and it's sub tests
     *  @param testUid - Unique id which is used to identify a test even it occurs multiple time in the test table
     */
    $scope.runTestAndSubTests = function (testUid) {
        var test = findTestInTreeByTestUid($scope.bottomUpTree, testUid);

        if (test != null){
            var testsToRun = getTestAndSubTests(test);
            $scope.resetTests(testsToRun);

            //Uses runOneTest in order to gather all result summay code in one place
            for (var i = 0; i < testsToRun.length; i++){
                $scope.runOneTest(testsToRun[i].id, testsToRun[i].testid, $scope.TestRunningModesEnum.MULTIPLE_TESTS);
            }
            $scope.numberOfTestsRunning = testsToRun.length;
        }
    };

    /**
     *  Runs a single test and creates a summary of the test result. Used by the other "run...test" methods
     *  @param id - The id of the test which is presented in the test table in the first column
     *  @param testUid - Unique id which is used to identify a test even it occurs multiple time in the test table
     *  @param testRunningMode - Used to identify which method calling "runOneTest".
     */
    $scope.runOneTest = function (id, testUid, testRunningMode) {
        $('button').prop('disabled', true);

        if (testRunningMode == $scope.TestRunningModesEnum.SINGLE_TEST){
            $scope.numberOfTestsRunning = 1;
            runTestFactory.getTestResult(id, testUid).success(getTestResultSuccessCallback).error(errorCallback);

        }else if(testRunningMode == $scope.TestRunningModesEnum.ALL_TESTS){
            runTestFactory.getAllTestResult(id).success(getTestResultSuccessCallback).error(errorCallback);

        }else{
            runTestFactory.getTestResult(id, testUid).success(getTestResultSuccessCallback).error(errorCallback);
        }
    };

    /**
     *  Runs all tests in the test table
     */
    $scope.runAllTest = function () {
        var numberOfTests = $scope.allTests.length;
        $scope.resetAllResult();

        for (var i = 0; i < numberOfTests; i++){
            var id = $scope.allTests[i];
            $scope.runOneTest(id, null, $scope.TestRunningModesEnum.ALL_TESTS);
        }

        $scope.numberOfTestsRunning = numberOfTests;
    };

    /**
     *  Resets a test by removing it's result
     *  @param testUid - Unique id which is used to identify a test even it occurs multiple time in the test table
     */
    $scope.removeTestResult = function (testUid) {
        for (var i = 0; i < $scope.currentFlattenedTree.length; i++){
            if ($scope.currentFlattenedTree[i].testid == testUid){
                delete $scope.currentFlattenedTree[i].result;
            }
        }
    }

    /**
     *  Show or hides a test depending on if it's visible or not
     *  @param testUid - Unique id which is used to identify a test even it occurs multiple time in the test table
     */
    $scope.toggleTestsVisibility = function (testUid) {

        var test = findTestInTreeByTestUid($scope.currentOriginalTree, testUid);
        var children = test.children;

        if(children[0].visible == false){
            setVisibilityOfTestsChildrenInTree(children, true);
        }else if (children[0].visible == true){
            children = getTestAndSubTests(test);
            setVisibilityOfTestsChildrenInTree(children, false);
            test.visible = true;
        }
    }

    /**
     *  Show or hides the result of a test depending on if it's visible or not
     *  @param testUid - Unique id which is used to identify a test even it occurs multiple time in the test table
     *  @param testIndex - Index of the test in the test table
     */
    $scope.toggleResultVisibility = function (testUid, testIndex) {
        test = findTestInTreeByTestUid($scope.currentFlattenedTree, testUid);

        if (test.showResult)
            $("#resultButton" + testIndex).html('Show result');
        else
            $("#resultButton" + testIndex).html('Hide result');

        test.showResult = !test.showResult;
    }

    /**
     *  Show or hides the trace log of a test depending on if it's visible or not
     *  @param testUid - Unique id which is used to identify a test even it occurs multiple time in the test table
     *  @param testIndex - Index of the test in the test table
     */
    $scope.toggleTraceLogVisibility = function (testUid, testIndex) {
        test = findTestInTreeByTestUid($scope.currentFlattenedTree, testUid);

        if (test.showTraceLog)
            $("#traceLogButton" + testIndex).html('Show trace log');
        else
            $("#traceLogButton" + testIndex).html('Hide trace log');

        test.showTraceLog = !test.showTraceLog
    }

    /**
     *  Exports test result to excel and downloads it
     */
    $scope.exportTestResultToExcel = function () {
        var a = document.createElement('a');
        var data_type = 'data:application/vnd.ms-excel';

        var tbl = generateExportResultHtmlTable();
        var table_html = tbl.outerHTML.replace(/ /g, '%20');

        a.href = data_type + ', ' + table_html;
        a.download = 'exported_table' + '.xls';

        //Appending the element a to the body is only necessary for the download to work in firefox
        document.body.appendChild(a)
        a.click();
        document.body.removeChild(a)

        e.preventDefault();
    }

    /**
     *  Exports test result to a text file and downloads it
     */
    $scope.exportTestResultToTextFile = function () {

        var resultString  = JSON.stringify(exportResult)
        var a = document.createElement("a");

        a.download = "export.txt";
        a.href = "data:text/plain;base64," + btoa(resultString);

        //Appending the element a to the body is only necessary for the download to work in firefox
        document.body.appendChild(a)
        a.click();
        document.body.removeChild(a)

        e.preventDefault();
    }

    /**
     *  Resets to result of every test in the test table
     */
    $scope.resetAllResult = function () {
        var tree = $scope.currentFlattenedTree;

        for (var i = 0; i < tree.length; i++){
            tree[i].result = null;
            tree[i].status = null;
            tree[i].traceLog = null;
        }
    }

    /**
     *  Resets to result of a set of tests
     *  @param tests - A set of tests to reset
     */
    $scope.resetTests = function (tests) {
        for (var i = 0; i < tests.length; i++){
            tests[i].result = null;
            tests[i].status = null;
            tests[i].traceLog = null;
        }
    };

    /**
     * Toggles the visibility of the instructions
     */
    $scope.toggleInstructionVisibility = function () {
        $scope.instructionVisible = !$scope.instructionVisible;
    };

    var hasShownWrongPasswordDialog = false;

    function createWrongPasswordDialog() {
        bootbox.dialog({
            message: "Unknown user or wrong password. Do you want to reset interaction configurations?",
            title: "Error occured",
            buttons: {
                danger: {
                    label: "No",
                    className: "btn-default"
                },
                success: {
                    label: "Yes",
                    className: "btn-primary",
                    callback: function () {
                        postResetInteractionFactory.postResetInteraction().success(emptySuccessCallback()).error(errorCallback);
                    }
                }
            }
        });
    }

    /**
     * Handles if any errors status occurs
     */
    function handleError() {
        var lastElement = subTestList.length - 1;

        var errorMessage = subTestList[lastElement].message

        if (errorMessage.indexOf("Unknown user or wrong password") != -1) {
            if (!hasShownWrongPasswordDialog) {
                hasShownWrongPasswordDialog = true;
                createWrongPasswordDialog();
            }
        }
    }

    var exportResult = [];

    /**
     * Enter the result of a single test to the export result list.
     * @param id - The id of the test which is presented in the test table in the first column
     * @param result - Result for a single test
     * @param traceLog - Trace log for a single test
     */
    function enterTestResultToExportResult(id, result, traceLog){

        var resultClone = jQuery.extend(true, [], result);

        for (var i = 0; i < exportResult.length; i++){
            if (id == exportResult[i].id){
                exportResult.splice(i, 1);
            }
        }

        exportResult.push({"id": id,
                   "result": resultClone,
                   "traceLog": traceLog});

    }

    /**
     * Enter the result returned from the server to the test table
     * @param data - contains the result of the executed test
     * @param testIndex - The index of the test in the test table
     */
    function enterResultToTree(data, testIndex) {

        subTestList = jQuery.extend(true, [], data['result']['tests']);

        for (var j = 0; j < subTestList.length; j++) {
            var statusNumber = subTestList[j].status;
            subTestList[j].status = convertStatusToText(statusNumber);
        }

        $scope.currentFlattenedTree[testIndex].result = subTestList;


        var convertedTraceLog = data['traceLog'];
        convertedTraceLog = convertedTraceLog.replace(/\n/g, '<br />');
        $scope.currentFlattenedTree[testIndex].traceLog = [{"traceMessage" : convertedTraceLog}];

        enterTestResultToExportResult($scope.currentFlattenedTree[testIndex].id, data['result']['tests'], data['traceLog']);

        $scope.currentFlattenedTree[testIndex].status = convertStatusToText(data['result']['status']);

        statusNumber = data['result']['status'];

//        if (statusNumber == TEST_STATUS['INTERACTION'].value) {
//            handleInteraction(data);
//        }
        if (statusNumber == TEST_STATUS['ERROR'].value) {
            handleError();
        }
    }

    /**
     * Writes the test result to the tree based on the tests Uid. Called while running a single test or a test and
     * it's sub tests.
     * @param data - The object containing the result.
     */
    function writeResultToTreeBasedOnTestUid(data) {
        testid = data['testid'];

        for (var i = 0; i < $scope.currentFlattenedTree.length; i++) {
            if ($scope.currentFlattenedTree[i].testid == testid) {
                enterResultToTree(data, i);

                countSuccessAndFails(data['result']['status']);
            }
        }
    }

    var countedTestIds = []

    /**
     * Writes the test result to the tree based on the tests id (not uniqe for every test in the test table).
     * Called while running all tests
     * @param data - The object containing the result.
     */
    function writeResultToTreeBasedOnId(data) {
        id = data['result']['id'];

        for (var i = 0; i < $scope.currentFlattenedTree.length; i++) {
            if ($scope.currentFlattenedTree[i].id == id) {
                enterResultToTree(data, i);

                if ($.inArray(id, countedTestIds) == -1) {
                    countSuccessAndFails(data['result']['status']);
                    countedTestIds.push(id)
                }
            }
        }
    }

    /**
     * @param test - The test who's test and sub test should be returned
     * @returns {Array} Returns a test and it's sub tests
     */
    function getTestAndSubTests(test){
        var children = test.children;
        var testAndSubTestList = [];
        testAndSubTestList.push(test);

        for (var i = 0; i < children.length; i++){
            testAndSubTestList = testAndSubTestList.concat(getTestAndSubTests(children[i]));
        }
        return testAndSubTestList;
    }

    /**
     * Create a flat tree instead of a tree where all the sub tests are nested inside it's parent.
     * @param nestedTree - A nested tree which should be flattened
     * @returns {Array} Returns a flat representation of the incoming nested tree
     */
    function buildFlatTree(nestedTree){
        //TODO Blir väl inte platt på riktigt
        var flatTree = [];

        for (var i = 0; i < nestedTree.length; i++) {
            var element = nestedTree[i];

            flatTree.push(element);
            if (element.children.length > 0){
                flatTree = flatTree.concat(buildFlatTree(element.children));
            }
        }
        return flatTree;
    }

    /**
     * Finds a test in tree based on the tests Uid
     * @param tree - The tree in which to search for a given test.
     * @param targetTestUid - A tests unique id
     * @returns {*} Returns the test with the matching Uid. If no test is found null is returned
     */
    function findTestInTreeByTestUid(tree, targetTestUid) {
        var matchingTest = null;

        for (var i = 0; i < tree.length; i++){
            numberOfChildren = tree[i].children.length

            if (tree[i].testid == targetTestUid){
                matchingTest =  tree[i];
                break;
            }
            else if (matchingTest == null && numberOfChildren != 0){
                matchingTest =  findTestInTreeByTestUid(tree[i].children, targetTestUid);
            }

        }
        return matchingTest;
    }

    /**
     * Sets the visibility of the children
     * @param children - A list of children who's visibility should be changed
     * @param visible - A boolean which are the visibility
     */
    function setVisibilityOfTestsChildrenInTree(children, visible) {
        for(var j= 0; j < children.length; j++){
            for (var i = 0; i < $scope.currentFlattenedTree.length; i++){
                if (children[j].testid == $scope.currentFlattenedTree[i].testid){
                    $scope.currentFlattenedTree[i].visible = visible;
                }
            }
        }
    }

    /**
     * @returns {HTMLElement} Returns generated HTML table of the result
     */
    function generateExportResultHtmlTable() {
        var tbl = document.createElement("table");
        var row;
        var column1;
        var column2;
        var column3;
        var text1;
        var text2;
        var text3;

        var result;

        for (var i = 0; i < exportResult.length; i++){
            row = document.createElement("tr");
            column1 = document.createElement("td");
            column2 = document.createElement("td");
            column3 = document.createElement("td");

            text1 = document.createTextNode(exportResult[i].id);
            text2 = document.createTextNode(JSON.stringify(exportResult[i].result));
            text3 = document.createTextNode(exportResult[i].traceLog);

            tbl.appendChild(row);
            row.appendChild(column1);
            row.appendChild(column2);
            row.appendChild(column3);

            column1.appendChild(text1);
            column2.appendChild(text2);
            column3.appendChild(text3);
       }

        return tbl;
    }

    var TEST_STATUS  = {
        'INFORMATION':{value: 0, string:'INFORMATION'},
        'OK':{value: 1, string:'OK'},
        'WARNING':{value: 2, string:'WARNING'},
        'ERROR':{value: 3, string:'ERROR'},
        'CRITICAL':{value: 4, string:'CRITICAL'},
        'INTERACTION':{value: 5, string:'INTERACTION'},
        'EMPTY_STATUS':{value: 6, string:'EMPTY_STATUS'}
    };

    /**
     * Converts a status from number to a string
     * @param status - Status as number
     * @returns {string} Returns String representation of the status
     */
    function convertStatusToText(statusToConvert) {
        for (var status in TEST_STATUS){
            if (TEST_STATUS[status].value == statusToConvert){
                return TEST_STATUS[status].string;
            }
        }
    };

    /**
     * Counts the number of successfully and failed executed tests.
     * @param status - A numeric representation of a status
     */
    function countSuccessAndFails(status){
        if (status == 0 || status == 1){
            $scope.resultSummary.success++;
        }else{
            $scope.resultSummary.failed++;
        }
    }

    //TODO Remove this function (only used for test purpose)
    $scope.test = function () {
        alert("test");
    };

    /**
     * Shows modal window where the user can send a error report
     */
    $scope.showModalWindowsErrorReport = function () {
        $('#modalWindowErrorReport').modal('show');
        $('#reportForm')[0].reset();
    };

    /**
     * Submits the error report and hides the modal window
     */
    $scope.sendReport = function () {
        $('#modalWindowErrorReport').modal('hide');

        //Get data from text fields and send it to the server the get the file reuse exporty txt file
        var email = $('#reportEmail').val();
        var message = $('#reportMessage').val();

        testResults = JSON.stringify(exportResult);

        errorReportFactory.postErrorReport(email, message, testResults).success(getPostErrorReportSuccessCallback).error(errorCallback);
    };

});

//Loads the menu from a given template file and inserts it it to the <div menu> tag
app.directive('menu', function($http) {
    return {
        restrict: 'A',
        templateUrl: '/static/templateMenu.html'
    }
});

/**
 * Activates the tooltip
 */
app.directive('directiveCallback', function(){
    return function(scope, element, attrs){
        attrs.$observe('directiveCallback',function(){
            if (attrs.directiveCallback == "true"){
                $("[data-toggle='tooltip']").tooltip();
            }
        });
    }
})


