
var app = angular.module('main', ['toaster'])

app.factory('opConfigurationFactory', function ($http) {
    return {
        getOpConfig: function () {
            return $http.get("/get_op_config");
        },

        postOpConfig: function (opConfigurations) {
            return $http.post("/post_op_config", {"opConfigurations": opConfigurations});
        },

        requestDownloadConfigFile: function () {
            return $http.get("/download_config_file");
        },

        requestUploadConfigFile: function (configFileContent) {
            return $http.post("/upload_config_file", {"configFileContent": configFileContent});
        },

        createNewConfigFile: function () {
            return $http.get("/create_new_config_file");
        },

        doesConfigFileExist: function () {
            return $http.get("/does_config_file_exist");
        },

        verifyConfigFile: function () {
            return $http.get("/verify_config_file");
        }
    };
});

app.factory('verifyConfigFactory', function ($http) {
    return {
        verifyConfig: function () {
            return $http.get("/run_test", {params: { "testname": 'oic-verify'}});
        }
    };
});

app.factory('postBasicInteractionDataFactory', function ($http) {
    return {
        postBasicInteractionData: function (title, redirectUri, pageType, controlType, loginForm) {
            return $http.post("/post_basic_interaction_data", {"title": title, "redirectUri": redirectUri, "pageType": pageType, "controlType": controlType, "loginForm": loginForm});
        }
    };
});

app.factory('cooikeFactory', function ($http) {
    return {
        validateCookies: function (cookies) {
            return $http.post("/validate_cookies", {"cookies": cookies});
        }
    }
});

app.controller('IndexCtrl', function ($scope, toaster, opConfigurationFactory, verifyConfigFactory, postBasicInteractionDataFactory, cooikeFactory) {
    $scope.opConfig;

    var TEST_STATUS  = {
        'INFORMATION':{value: 0, string:'INFORMATION'},
        'OK':{value: 1, string:'OK'},
        'WARNING':{value: 2, string:'WARNING'},
        'ERROR':{value: 3, string:'ERROR'},
        'CRITICAL':{value: 4, string:'CRITICAL'},
        'INTERACTION':{value: 5, string:'INTERACTION'},
        'EMPTY_STATUS':{value: 6, string:'EMPTY_STATUS'}
    };

    function verifyConfigErrorCallback(data, status, headers, config){

        enableGUI();
        $('#modalWindowInteraction').modal('show');
        $('#modalWindowHTMLContent').append(data.ExceptionMessage);

        if (data.HTML != null){
            var loginPage = document.createElement('html');
            loginPage.innerHTML = data['HTML'];

            //Create a iframe and present the login screen inside the iframe
            var iframe = document.createElement('iframe');
            iframe.setAttribute('width', '100%');
            iframe.setAttribute('height', '750px');

            $('#modalWindowHTMLContent').append(iframe);

            iframe.contentWindow.document.open();
            iframe.contentWindow.document.write(loginPage.innerHTML);
            iframe.contentWindow.document.close();
        }
    }

    /**
     * Is responsible for verifying that the configuration contains enough login information to be able to run tests which
     * requires interactions or cookies
     */
    $scope.runVerifyConfig = function () {
        $('button').prop('disabled', true);
        verifyConfigFactory.verifyConfig().success(getVerifyConfigSuccessCallback).error(verifyConfigErrorCallback);
    };

    function enableGUI(){
        $('button').prop('disabled', false);
    }

    /**
     * Confirms that the configuration will be able to run tests which requires logging in
     * @param data - The result returned from the server
     * @param status - The status on the response from the server
     * @param headers - The header on the response from the server
     * @param config - The configuration on the response from the server
     */
    function getVerifyConfigSuccessCallback(data, status, headers, config) {

        statusNumber = data['result']['status'];

        if (statusNumber == TEST_STATUS['INTERACTION'].value) {
            handleInteraction(data);
        }else{
           bootbox.alert("Your configurations are verified you should now be able to run the tests requiring a user to be logged in");
        }

        enableGUI();
    }

    /**
     * Postback function called when an interaction successfully has been stored on the server
     */
    window.postBack = function(){
        setTimeout(function() {
            $('#modalWindowInteraction').modal('hide');
            foundInteractionStatus = false;
            requestLatestConfigFileFromServer();
            $scope.runVerifyConfig();
            $scope.$apply();
        }, 200);
    }

    var foundInteractionStatus = false;

    /**
     * Handles an interaction status
     * @param data - Response returned from the server
     */
    function handleInteraction(data) {
        if (!foundInteractionStatus) {
            foundInteractionStatus = true;

            var subResults = data['result']['tests'];

            for (var i = 0; i < subResults.length; i++) {
                if (subResults[i]['status'] == TEST_STATUS['INTERACTION'].value) {
                    var htmlString = subResults[i]['message'];

                    var unFormatedUrl = subResults[i]['url']
                    var url = unFormatedUrl.substr(0, unFormatedUrl.indexOf('?'));

                    break;
                }
            }

            var htmlElement = document.createElement('html');
            htmlElement.innerHTML = htmlString;

            var title = htmlElement.getElementsByTagName('title')[0].innerHTML;

            //TODO I don't know how to identify the property
            var pageType = "login";

            var formTags = htmlElement.getElementsByTagName('form');
            if (formTags.length > 0) {
                var controlType = "form"
            }

            postBasicInteractionDataFactory.postBasicInteractionData(title, url, pageType, controlType, data).success(postBasicInteractionSuccessCallback).error(errorCallback);
        }
    }

    /**
     * Confirms that the basic interaction information has successfully has been stored on the server
     * @param data - The result returned from the server
     * @param status - The status on the response from the server
     * @param headers - The header on the response from the server
     * @param config - The configuration on the response from the server
     */
    function postBasicInteractionSuccessCallback(data, status, headers, config) {
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
    };

    /**
     * Creates an iframe and shows to modal window containing the login screen
     * @param data - Result sent from the server
     */
    function createIframeAndShowInModelWindow(data) {
        var subTestList = data['result']['tests'];
        var lastElementIndex = subTestList.length -1;

        $('#modalWindowInteraction').modal('show');
        $('#modalWindowHTMLContent').empty();

        //Resets the foundInteractionStatus to false if the user exit the log in window
        $('#modalWindowInteraction').on('hidden.bs.modal', function (e) {
            foundInteractionStatus = false;
        });

        var loginPage = setupLoginPage(data);

        //Create a iframe and present the login screen inside the iframe
        var iframe = document.createElement('iframe');
        iframe.setAttribute('width', '100%');
        iframe.setAttribute('height', '750px');

        $('#modalWindowHTMLContent').append("<h1>Information</h1><span>In order to use this application you need to log in to the OP. Information, like username and password, will be stored on the server which means that you only have to do this once  </span>");
        $('#modalWindowHTMLContent').append(iframe);

        iframe.contentWindow.document.open();
        iframe.contentWindow.document.write(loginPage.innerHTML);
        iframe.contentWindow.document.close();
    };

    /**
     * Setup the login page by adding two hidden input fields and sets a submit action on the login form
     * @param data - Data returned from the server containing the login page
     * @returns {HTMLElement} login page
     */
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

    /**
     * Shows the appropriate input fields depending on which value which has been selected in the
     * "fetchInfoFromServerDropDown" drop down menu
     */
    $scope.switchBetweenProviderConfigElement = function(){

        if ($scope.opConfig.fetchInfoFromServerDropDown.value == "static"){
            $scope.opConfig.fetchStaticInfoFromServer.showInputFields = true;
            $scope.opConfig.fetchDynamicInfoFromServer.showInputField = false;
        }
        if ($scope.opConfig.fetchInfoFromServerDropDown.value == "dynamic"){
            $scope.opConfig.fetchDynamicInfoFromServer.showInputField = true;
            $scope.opConfig.fetchStaticInfoFromServer.showInputFields = false;
        }
    };

    $scope.toggleNetscapeCookieExample = function(){
        $("#modalWindowNetscapeCookieExample").modal('toggle');
    };

    /**
     * Confirms that the configuration will be able to run tests which requires logging in
     * @param data - The result returned from the server
     * @param status - The status on the response from the server
     * @param headers - The header on the response from the server
     * @param config - The configuration on the response from the server
     */
    function validateCookieSuccessCallback(data, status, headers, config) {
        opConfigurationFactory.postOpConfig($scope.opConfig).success(postOpConfigurationsSuccessCallback).error(errorCallback);
    }

    /**
     * Sets the configuration returned from the server
     * @param data - The result returned from the server
     * @param status - The status on the response from the server
     * @param headers - The header on the response from the server
     * @param config - The configuration on the response from the server
     */
    function getOpConfigurationSuccessCallback(data, status, headers, config) {
        $scope.opConfig = data;
    }

    /**
     * Confirms that the configuration successfully has been stored on the server
     * @param data - The result returned from the server
     * @param status - The status on the response from the server
     * @param headers - The header on the response from the server
     * @param config - The configuration on the response from the server
     */
    function postOpConfigurationsSuccessCallback(data, status, headers, config) {
        showVerifyConfigDialog();
    }

    function showVerifyConfigDialog(){
        bootbox.dialog({
            message: "Your configuration was successfully stored on the server. <br><br> Some tests requires the " +
                "user to be logged in, this could be done by either using interactions or cookies. " +
                "Do you want to verify that you could run this kinds of tests?",
            title: "Verify configuration",
            buttons: {
                danger: {
                    label: "No",
                    className: "btn-default"
                },
                success: {
                    label: "Yes",
                    className: "btn-primary",
                    callback: function () {
                        $scope.runVerifyConfig();
                        $scope.$apply();
                    }
                }
            }
        });
    }

    /**
     * Confirms that the configuration successfully has been retried from the server. Then is downloaded to the
     * clients computer.
     * @param data - The result returned from the server
     * @param status - The status on the response from the server
     * @param headers - The header on the response from the server
     * @param config - The configuration on the response from the server
     */
    function downloadConfigFileSuccessCallback(data, status, headers, config) {
        configDict = JSON.stringify(data["configDict"])
        var a = document.createElement("a");
        a.download = "config.json";
        a.href = "data:text/plain;base64," + btoa(configDict);

        //Appending the element a to the body is only necessary for the download to work in firefox
        document.body.appendChild(a)
        a.click();
        document.body.removeChild(a)
    }

    /**
     * Requests latest config from the server.
     */
    function requestLatestConfigFileFromServer(){
        opConfigurationFactory.getOpConfig().success(getOpConfigurationSuccessCallback).error(errorCallback);
    }

    /**
     * Confirms that the configuration successfully has been uploaded on the server
     * @param data - The result returned from the server
     * @param status - The status on the response from the server
     * @param headers - The header on the response from the server
     * @param config - The configuration on the response from the server
     */
    function uploadConfigFileSuccessCallback(data, status, headers, config) {
        $("#modalWindowUploadConfigurationFile").modal('toggle');
        requestLatestConfigFileFromServer();
        showVerifyConfigDialog();
    }

    /**
     * Confirms that a new configuration successfully has been stored on the server
     * @param data - The result returned from the server
     * @param status - The status on the response from the server
     * @param headers - The header on the response from the server
     * @param config - The configuration on the response from the server
     */
    function createNewConfigFileSuccessCallback(data, status, headers, config) {
        requestLatestConfigFileFromServer();
    }

    /**
     * Show a "No configuration is available" error dialog
     */
    function showNoConfigAvailable(){
        bootbox.alert("No configurations available. Either the session may have timed out or no configuration has be created or uploaded to the server.");
    }

    /**
     * Confirms that a there exists a configuration file on the server
     * @param data - The result returned from the server
     * @param status - The status on the response from the server
     * @param headers - The header on the response from the server
     * @param config - The configuration on the response from the server
     */
    function reloadDoesConfigFileExistSuccessCallback(data, status, headers, config) {
        var doesConfigFileExist = data['doesConfigFileExist'];

        if (doesConfigFileExist == true){
            requestLatestConfigFileFromServer();
        }
    }

    /**
     * Confirms that a there exists a configuration file on the server. If configuration file exist then it's downloaded
     * @param data - The result returned from the server
     * @param status - The status on the response from the server
     * @param headers - The header on the response from the server
     * @param config - The configuration on the response from the server
     */
    function downloadDoesConfigFileExistSuccessCallback(data, status, headers, config) {
        var doesConfigFileExist = data['doesConfigFileExist'];

        if (doesConfigFileExist == true){
            opConfigurationFactory.requestDownloadConfigFile().success(downloadConfigFileSuccessCallback).error(errorCallback);
        }else{
            showNoConfigAvailable();
        }

    }

    /**
     * Shows error message dialog
     * @param data - The result returned from the server
     * @param status - The status on the response from the server
     * @param headers - The header on the response from the server
     * @param config - The configuration on the response from the server
     */
    function errorCallback(data, status, headers, config) {
        bootbox.alert(data.ExceptionMessage);

        enableGUI();
    }

    /**
     * Shows a confirmation dialog for creating a new configuration
     */
    $scope.showModalWindowAddConfigFields = function(){
        $("#modalWindowAddConfigFields").modal('toggle');
    };

    /**
     * Shows a modal dialog for uploading new configuration.
     */
    $scope.showModalUploadConfigWindow = function(){
        $("#modalWindowUploadConfigurationFile").modal('toggle');
    };

    //TODO remove function (only used for test purposes)
    $scope.test = function () {
        alert("test");
    };

    /**
     * Adding a new interaction block
     */
    $scope.addInteractionBlock = function () {

        var numberOfBlocks = $scope.opConfig.interactionsBlocks.length

        var newInteractionBlock = {"id": numberOfBlocks, "inputFields": [
                        {"label": "title", "textFieldContent": ""},
                        {"label": "url", "textFieldContent": ""},
                        {"label": "pageType", "textFieldContent": ""},
                        {"label": "index", "textFieldContent": ""},
                        {"label": "set", "textFieldContent": ""},
                        {"label": "type", "textFieldContent": ""}
                    ]}

        $scope.opConfig.interactionsBlocks.push(newInteractionBlock);
    };

    /**
     * Creates a "confirm that you want to remove this interaction block" dialog
     * @param interactionBlockId - The id of interaction block
     */
    $scope.createConfirmRemoveInteractionBlockDialog = function (interactionBlockId) {
        bootbox.dialog({
            message: "Du you really want to remove this interaction?",
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
                        removeInteractionBlock(interactionBlockId);
                        //Manually updating the view since it's the code is executed in a callback function
                        $scope.$apply();
                    }
                }
            }
        });
    }

    /**
     * Removes the interaction block
     * @param interactionBlockId - The id of interaction block
     */
    function removeInteractionBlock(interactionBlockId) {
        var interactionList = $scope.opConfig.interactionsBlocks
        var indexToRemove;

        for (var i = 0; i < interactionList.length; i++){
            if (interactionList[i].id == interactionBlockId){
                indexToRemove = i;
                break;
            }
        }

        $scope.opConfig.interactionsBlocks.splice(indexToRemove, 1);
    }

    /**
     * Add new list item to a static input field.
     * @param staticInputFieldIndex - Index of a static input field
     */
    $scope.addElementToList = function(staticInputFieldIndex){
        var currentInputField = $scope.opConfig.fetchStaticInfoFromServer.inputFields[staticInputFieldIndex];
        var newConfigTextField = {"index": currentInputField.values.length, "textFieldContent": ""};
        $scope.opConfig.fetchStaticInfoFromServer.inputFields[staticInputFieldIndex].values.splice(currentInputField.values.length ,0, newConfigTextField);
    };


    /**
     * Removes list item from a static input field.
     * @param staticInputFieldIndex - Index of a static input field
     * @param valueListIndex - Index of list item to remove
     */
    $scope.removeElementFromList = function(staticProviderIndex, valueListIndex){
        var valueList = $scope.opConfig.fetchStaticInfoFromServer.inputFields[staticProviderIndex].values
        valueList.splice(valueListIndex, 1);
    };


    /**
     * Checks if the user har entered the required client id and client secret
     * @returns {boolean} - Returns true if client id and client secret input fields are not empty else false
     */
    function hasEnteredClientIdAndClientSecret(){
        clientId = $scope.opConfig['supportsStaticClientRegistrationTextFields'][0]['textFieldContent']
        clientSecret = $scope.opConfig['supportsStaticClientRegistrationTextFields'][1]['textFieldContent']

        if (clientId == "")
            return false;

        else if (clientSecret == "")
            return false;

        return true
    }

    /**
     * Checks if the user has entered all the required information.
     * @returns {boolean} - Returns true if required input fields are not empty else false
     */
    function hasEnteredRequeredInformation(){
        if ($scope.opConfig['dynamicClientRegistrationDropDown']['value'] == "no"){
            return hasEnteredClientIdAndClientSecret();
        }

        return true;
    }

    /**
     * Sends the configuration file to the server
     */
    $scope.saveConfigurations = function(){

        if (hasEnteredRequeredInformation()){
            opConfigurationFactory.postOpConfig($scope.opConfig).success(postOpConfigurationsSuccessCallback).error(errorCallback);
        }else{
            alert("Please enter all the required information")
        }
    };

    $scope.saveConfigurations = function(){
        var cookies = $scope.opConfig['loginCookies']

        if (cookies != "") {
            /* Checks if the entered cookies follows the netscape format */
            cooikeFactory.validateCookies(cookies).success(validateCookieSuccessCallback).error(errorCallback);
        }else{
            opConfigurationFactory.postOpConfig($scope.opConfig).success(postOpConfigurationsSuccessCallback).error(errorCallback);
        }
    };

    function showCookieErrorDialog(data, status, headers, config) {
        $("#modalWindowCookieError").modal('toggle');
        $scope.cookieErrorMessage = data.ExceptionMessage;
    }

    /**
     * Tries to download the configuration file from the server
     */
    $scope.requestDownloadConfigFile = function(){
        opConfigurationFactory.doesConfigFileExist().success(downloadDoesConfigFileExistSuccessCallback).error(errorCallback);
    };

    /**
     * Tries to upload the configuration file to the server.
     */
    $scope.requestUploadConfigFile = function(){
        var file = document.getElementById("targetFile").files[0];

        if (file) {
            var reader = new FileReader();
            reader.readAsText(file, "UTF-8");
            reader.onload = function (evt) {
                opConfigurationFactory.requestUploadConfigFile(evt.target.result).success(uploadConfigFileSuccessCallback).error(errorCallback);
                $scope.$apply();
            };
            reader.onerror = function (evt) {
                alert("error reading file");
            }
        }
    };

    opConfigurationFactory.doesConfigFileExist().success(reloadDoesConfigFileExistSuccessCallback).error(errorCallback);

    /**
     * Show a "confirm that you want to create a new configuration file" dialog
     */
    $scope.createNewConfigFile = function () {
        bootbox.dialog({
            message: "All your existing configurations which is not downloaded will be overwritten. Are you sure you want to create a new configuration?",
            title: "Create new file",
            buttons: {
                danger: {
                    label: "No",
                    className: "btn-default"
                },
                success: {
                    label: "Yes",
                    className: "btn-primary",
                    callback: function () {
                        //TODO reset data structure
                        opConfigurationFactory.createNewConfigFile().success(createNewConfigFileSuccessCallback).error(errorCallback);
                        $scope.$apply();
                    }
                }
            }
        });
    }
});

//Loads the menu from a given template file and inserts it it to the <div menu> tag
app.directive('menu', function($http) {
    return {
        restrict: 'A',
        templateUrl: '/static/templateMenu.html'
    }
});