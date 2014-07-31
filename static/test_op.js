
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
        getTestResult: function (testname, testid) {
            return $http.get("/run_test", {params: { "testname": testname, "testid": testid}});
        },
        getAllTestResult: function (testname) {
            return $http.get("/run_test", {params: { "testname": testname}});
        }
    };
});

app.factory('postBasicInteractionDataFactory', function ($http) {
    return {
        postBasicInteractionData: function (title, redirectUri, pageType, controlType) {
            return $http.post("/post_basic_interaction_data", {"title": title, "redirectUri": redirectUri, "pageType": pageType, "controlType": controlType});
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

app.factory('notificationFactory', function () {

    return {
        success: function () {
            //alert('success');
            //toastr.success("Success");
        },
        error: function (text) {
            //alert(text);
            //toastr.error(text, "Error!");
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

app.controller('IndexCtrl', function ($scope, testFactory, notificationFactory, runTestFactory, postBasicInteractionDataFactory, postResetInteractionFactory, errorReportFactory, toaster) {
    $scope.testResult = "";
    $scope.currentFlattenedTree = "None";
    $scope.numberOfTestsRunning = 0;
    var addedIds = [];
    var subTestList;

    $scope.resultSummary = {'success': 0, 'failed': 0};

    /**
     * Callback function which is invoked when the list containing all the tests has been downloaded successfully.
     */
    function getListSuccessCallback(data, status, headers, config) {
        $scope.bottomUpTree = data["bottomUpTree"];

        $scope.currentOriginalTree = $scope.bottomUpTree;
        $scope.currentFlattenedTree = buildFlatTree($scope.bottomUpTree);

        $("[data-toggle='tooltip']").tooltip();
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
            writeResultToTreeBasedOnTestid(data);
        }

        $scope.numberOfTestsRunning--;

        if ($scope.numberOfTestsRunning <= 0){
            resetFlags();

            var resultString = "Successful tests: " + $scope.resultSummary.success + "\n" + " Failed tests: " + $scope.resultSummary.failed
            toaster.pop('note', "Result summary", resultString);
            addedIds = []
        }
    };

    function resetFlags(){
        $('button').prop('disabled', false);
        isRunningAllTests = false;
        hasShownInteractionConfigDialog = false;
        hasShownWrongPasswordDialog = false;
        isShowingErrorMessage = false;
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
     * Callback which is invoked when any rest request doesn't get an correct response
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

    $scope.runMultipleTest = function (id, testid) {

        var test = findTestInTreeByTestid($scope.bottomUpTree, testid);

        /*  If the current tree layout is a topdown tree the tree has to be converted since the "top
            down" and "bottom up" doesn't contain the same testID numbers */
        if (test == null){
            convertedTestsToRun = convertFromBottomUpToTopDownNodes(id);

            for (var i = 0; i < convertedTestsToRun.length; i++){
                runTestFactory.getTestResult(convertedTestsToRun[i].id, convertedTestsToRun[i].testid).success(getTestResultSuccessCallback).error(errorCallback);
            }
        }else{
            var testsToRun = getTestAndSubTests(test);
            $scope.resetNodes(testsToRun);

            //Uses runOneTest in order to gather all result summay code in one place
            for (var i = 0; i < testsToRun.length; i++){
                $scope.runOneTest(testsToRun[i].id, testsToRun[i].testid), "multipleTest";
            }
        }

        $scope.numberOfTestsRunning = testsToRun.length;
    };

    $scope.runOneTest = function (id, testid, numberOfTest) {
        //Reset test summary or else the result of multiply runs for the same test will be presented
        $scope.resultSummary = {'success': 0, 'failed': 0};
        $('button').prop('disabled', true);

        if (numberOfTest == "singleTest"){
            $scope.numberOfTestsRunning = 1;
            runTestFactory.getTestResult(id, testid).success(getTestResultSuccessCallback).error(errorCallback);

        }else if(numberOfTest == "allTest"){
            runTestFactory.getAllTestResult(id).success(getTestResultSuccessCallback).error(errorCallback);

        }else{
            runTestFactory.getTestResult(id, testid).success(getTestResultSuccessCallback).error(errorCallback);
        }
    };

    $scope.runAllTest = function () {
        var treeSize = $scope.currentFlattenedTree.length;
        var executedIdList = []
        $scope.resetAll();

        for (var i = 0; i < treeSize; i++){
            var id = $scope.currentFlattenedTree[i].id;
            var testid = $scope.currentFlattenedTree[i].testid;
            $scope.runOneTest(id, testid, "allTest");
        }

        $scope.numberOfTestsRunning = treeSize;
    };

    $scope.removeTestResult = function (testid) {
        for (var i = 0; i < $scope.currentFlattenedTree.length; i++){
            if ($scope.currentFlattenedTree[i].testid == testid){
                delete $scope.currentFlattenedTree[i].result;
            }
        }
    }

    $scope.showOrHideTests = function (testid) {

        var test = findTestInTreeByTestid($scope.currentOriginalTree, testid);
        var children = test.children;

        if(children[0].visible == false){
            showChildrenInTree(children, true);
        }else if (children[0].visible == true){
            children = getTestAndSubTests(test);
            showChildrenInTree(children, false);
            test.visible = true;
        }
    }

    $scope.showOrHideResult = function (testid, testIndex) {
        test = findTestInTreeByTestid($scope.currentFlattenedTree, testid);

        if (test.showResult == true){
            test.showResult = false;
            $("#resultButton" + testIndex).html('Show result');
        }else{
            test.showResult = true;
            $("#resultButton" + testIndex).html('Hide result');
        }
    }

    $scope.showOrHideTraceLog = function (testid, testIndex) {
        test = findTestInTreeByTestid($scope.currentFlattenedTree, testid);

        if (test.showTraceLog == true){
            test.showTraceLog = false;
            $("#traceLogButton" + testIndex).html('Show trace log');
        }else{
            test.showTraceLog = true;
            $("#traceLogButton" + testIndex).html('Hide trace log');
        }
    }

    $scope.exportTestResultToExcel = function () {
        var a = document.createElement('a');
        var data_type = 'data:application/vnd.ms-excel';

        var tbl = generateExportResultTable();
        var table_html = tbl.outerHTML.replace(/ /g, '%20');

        a.href = data_type + ', ' + table_html;
        a.download = 'exported_table' + '.xls';

        //Appending the element a to the body is only necessary for the download to work in firefox
        document.body.appendChild(a)
        a.click();
        document.body.removeChild(a)

        e.preventDefault();
    }

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

    $scope.resetAll = function () {
        var tree = $scope.currentFlattenedTree;

        for (var i = 0; i < tree.length; i++){
            tree[i].result = null;
            tree[i].status = null;
            tree[i].traceLog = null;
        }
    }

    $scope.resetNodes = function (nodes) {
        for (var i = 0; i < nodes.length; i++){
            nodes[i].result = null;
            nodes[i].status = null;
        }
    }

    $scope.instructionVisible = false;

    $scope.toggleInstructionVisibility = function () {
        if ($scope.instructionVisible == true){
            $scope.instructionVisible = false;
        }else{
            $scope.instructionVisible = true;
        }
    }

    var latestExecutedTestid;

    function setupLoginPage(data) {
        var loginPage = document.createElement('html');
        loginPage.innerHTML = data['result']['htmlbody'];
        var formtag = loginPage.getElementsByTagName('form')[0];

        usernameNameTag = document.createElement('input');
        usernameNameTag.setAttribute('name', 'usernameNameTag');
        usernameNameTag.setAttribute('type', 'hidden');
        usernameNameTag.setAttribute('value', data['usernameName']);

        passwordNameTag = document.createElement('input');
        passwordNameTag.setAttribute('name', 'passwordNameTag');
        passwordNameTag.setAttribute('type', 'hidden');
        passwordNameTag.setAttribute('value', data['passwordName']);

        formtag.appendChild(usernameNameTag);
        formtag.appendChild(passwordNameTag);

        formtag.setAttribute('action', '/post_final_interaction_data');
        return loginPage;
    }

    var createIframeAndShowInModelWindow = function(data) {

        var subTestList = data['result']['tests'];
        var lastElementIndex = subTestList.length -1;

        $('#modalWindowIframe').modal('show');
        $('#modalIframeContent').empty();

        //Resets the foundInteractionStatus to false if the user exit the log in window
        $('#modalWindowIframe').on('hidden.bs.modal', function (e) {
            foundInteractionStatus = false;
        });

        var loginPage = setupLoginPage(data);

        //Create a iframe and present the login screen inside the iframe
        var iframe = document.createElement('iframe');
        iframe.setAttribute('width', '100%');
        iframe.setAttribute('height', '750px');

        $('#modalIframeContent').append("<h1>Information</h1><span>In order to use this application you need to log in to the IDP. Information, like username and password, will be stored on the server which means that you only have to do this once  </span>");
        $('#modalIframeContent').append(iframe);

        iframe.contentWindow.document.open();
        iframe.contentWindow.document.write(loginPage.innerHTML);
        iframe.contentWindow.document.close();

    }

    var foundInteractionStatus = false;
    var hasShownInteractionConfigDialog = false;

    function createInteractionConfigDialog(data) {
        bootbox.dialog({
            message: "The server are missing some interaction configurations. Do you want the system to try insert the interaction configuration?",
            title: "Interaction information required",
            buttons: {
                danger: {
                    label: "No",
                    className: "btn-default"
                },
                success: {
                    label: "Yes",
                    className: "btn-primary",
                    callback: function () {
                        createIframeAndShowInModelWindow(data);
                    }
                }
            }
        });
    }

    var handleInteraction = function (data) {
        if (foundInteractionStatus == false) {
            foundInteractionStatus = true;

            if (isRunningAllTests){
                var test = findTestInTreeByID($scope.currentFlattenedTree, data['result']['id']);
            }else{
                var test = findTestInTreeByTestid($scope.currentFlattenedTree, data['testid']);
            }

            var subResults = test['result'];

            for (var i = 0; i < subResults.length; i++) {
                if (subResults[i]['status'] == "INTERACTION") {
                    var htmlString = subResults[i]['message'];

                    var unFormatedUrl = subResults[i]['url']
                    var url= unFormatedUrl.substr(0, unFormatedUrl.indexOf('?'));

                    break;
                }
            }

            var htmlElement = document.createElement('html');
            htmlElement.innerHTML = htmlString;

            var title = htmlElement.getElementsByTagName('title')[0].innerHTML;

            //TODO I don't know how to identify the property
            var pageType = "login";

            var formTags = htmlElement.getElementsByTagName('form');
            if (formTags.length > 0){
                var controlType = "form"
            }

            postBasicInteractionDataFactory.postBasicInteractionData(title, url, pageType, controlType).success(emptySuccessCallback).error(errorCallback);

            if (!hasShownInteractionConfigDialog){

                hasShownInteractionConfigDialog = true;
                createInteractionConfigDialog(data);
            }
        }
    }

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

    function handleError() {
        var lastElement = subTestList.length - 1;

        var errorMessage = subTestList[lastElement].message

        if (errorMessage.indexOf("Unknown user or wrong password") != -1) {

            if (!hasShownWrongPasswordDialog) {
                hasShownWrongPasswordDialog = true;
                createWrongPasswordDialog();
                //alert("Unknown user or wrong password. Do you want to reset interaction configurations?");

            }
        }
    }

    var exportResult = []

    function enterExportData(id, result, traceLog){

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

    function enterResultToTree(data, i) {

        subTestList = jQuery.extend(true, [], data['result']['tests']);

        for (var j = 0; j < subTestList.length; j++) {
            var statusNumber = subTestList[j].status;
            subTestList[j].status = convertStatusToText(statusNumber);
        }

        $scope.currentFlattenedTree[i].result = subTestList;


        var convertedTraceLog = data['traceLog'];
        convertedTraceLog = convertedTraceLog.replace(/\n/g, '<br />');
        $scope.currentFlattenedTree[i].traceLog = [{"traceMessage" : convertedTraceLog}];

        enterExportData($scope.currentFlattenedTree[i].id, data['result']['tests'], data['traceLog']);

        $scope.currentFlattenedTree[i].status = convertStatusToText(data['result']['status']);
        countSuccessAndFails(data['result']['status']);


        statusNumber = data['result']['status'];

        if (statusNumber == 5) {
            handleInteraction(data);
        }
        else if (statusNumber == 3) {
            handleError();
        }
    }

    window.postBack = function(){
        //A bug appers when interactions without login screen
        setTimeout(function() {
            $('#modalWindowIframe').modal('hide');
            foundInteractionStatus = false;
            var infoString = "The interaction data was successfully stored on the server. Please rerun the tests, it's possible that more interaction data has to be collected and stored on the server"

            //toaster.pop('success', "Log in", infoString);
            bootbox.alert(infoString);
        }, 200);
    }

    function writeResultToTreeBasedOnTestid(data) {
        testid = data['testid'];

        for (var i = 0; i < $scope.currentFlattenedTree.length; i++) {
            if ($scope.currentFlattenedTree[i].testid == testid) {
                enterResultToTree(data, i);
            }
        }
    }

    function writeResultToTreeBasedOnId(data) {
        id = data['result']['id'];

        for (var i = 0; i < $scope.currentFlattenedTree.length; i++) {
            if ($scope.currentFlattenedTree[i].id == id) {
                if ($.inArray(id, addedIds) == -1){
                    enterResultToTree(data, i);
                }
            }
        }
        addedIds.push(id);
    }

    function convertFromBottomUpToTopDownNodes(id){
        var test = findTestInTreeByID($scope.bottomUpTree, id);
        var testsToRun = getTestAndSubTests(test);
        var convertedTestsToRun = [];

        for (var j = 0; j < testsToRun.length; j++){
            convertedTest = findTestInTreeByID($scope.topDownTree, testsToRun[j].id);
            convertedTestsToRun.push(convertedTest);
        }
        return convertedTestsToRun;
    }

    function getTestAndSubTests(test){
        var children = test.children;
        var subChildrenList = [];
        subChildrenList.push(test);

        for (var i = 0; i < children.length; i++){
            subChildrenList = subChildrenList.concat(getTestAndSubTests(children[i]));
        }
        return subChildrenList;
    }

    function buildFlatTree(newTree){
        //Sort currentFlattenedTree elements by name or test result

        var flatTree = [];

        for (var i = 0; i < newTree.length; i++) {
            var element = newTree[i];

            flatTree.push(element);
            if (element.children.length > 0){
                flatTree = flatTree.concat(buildFlatTree(element.children));
            }
        }
        return flatTree;
    }

    function findTestInTreeByTestid(tree, targetTestid) {
        var matchingTest = null;

        for (var i = 0; i < tree.length; i++){
            numberOfChildren = tree[i].children.length

            if (tree[i].testid == targetTestid){
                matchingTest =  tree[i];
                break;
            }
            else if (matchingTest == null && numberOfChildren != 0){
                matchingTest =  findTestInTreeByTestid(tree[i].children, targetTestid);
            }

        }
        return matchingTest;
    }

    function findTestInTreeByID(tree, targetID) {
        var matchingTest = null;

        for (var i = 0; i < tree.length; i++){
            numberOfChildren = tree[i].children.length


            if (tree[i].id == targetID){
                matchingTest =  tree[i];
                break;
            }
            else if (matchingTest == null && numberOfChildren != 0){
                matchingTest =  findTestInTreeByID(tree[i].children, targetID);
            }

        }
        return matchingTest;
    }

    function showChildrenInTree(children, visible) {
        for(var j= 0; j < children.length; j++){
            for (var i = 0; i < $scope.currentFlattenedTree.length; i++){
                if (children[j].testid == $scope.currentFlattenedTree[i].testid){
                    $scope.currentFlattenedTree[i].visible = visible;
                }
            }
        }
    }

    function generateExportResultTable() {
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

    function convertStatusToText(status) {
        if (status == 0){
            return "INFORMATION";
        }else if (status == 1){
            return "OK";
        }else if (status == 2){
            return "WARNING";
        }else if (status == 3){
            return "ERROR";
        }else if (status == 4){
            return "CRITICAL";
        }else if (status == 5){
            return "INTERACTION";
        }
    };

    function countSuccessAndFails(status){
        if (status == 0 || status == 1){
            $scope.resultSummary.success++;
        }else{
            $scope.resultSummary.failed++;
        }
    }

    $scope.test = function () {
        alert("test");
    };

    $scope.showModalWindowsErrorReport = function () {

        $('#modalWindowErrorReport').modal('show');
        $('#reportForm')[0].reset();

    };

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

app.directive('directiveCallback', function(){
    return function(scope, element, attrs){
        attrs.$observe('directiveCallback',function(){
            if (attrs.directiveCallback == "true"){
                $("[data-toggle='tooltip']").tooltip();
            }
        });
    }
})


