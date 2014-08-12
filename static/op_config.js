
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
        }
    };
});

app.controller('IndexCtrl', function ($scope, toaster, opConfigurationFactory) {
    $scope.opConfig;

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
        alert("Op Configurations successfully SAVED");
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
        alert("Target json successfully UPLOADED");
        $("#modalWindowUploadConfigurationFile").modal('toggle');
        requestLatestConfigFileFromServer();
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
        clientId = $scope.opConfig['requiredInfoTextFields'][0]['textFieldContent']
        clientSecret = $scope.opConfig['requiredInfoTextFields'][1]['textFieldContent']

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
        if ($scope.opConfig['requiredInfoDropDown']['value'] == "no"){
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