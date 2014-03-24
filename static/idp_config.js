
var app = angular.module('main', ['toaster'])

app.factory('configFileFactory', function ($http) {
    return {

        downloadConfigFile: function () {
            return $http.get("/download_config_file");
        },

        uploadConfigFile: function (configFileContent) {
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

app.factory('opConfigurationFactory', function ($http) {
    return {
        getOpConfig: function () {
            return $http.get("/get_op_config");
        }
    };
});

app.controller('IndexCtrl', function ($scope, configFileFactory, toaster, opConfigurationFactory) {
    $scope.opConfig;

    $scope.switchBetweenProviderConfigElement = function(){

        if ($scope.opConfig.fetchInfoFromServerDropDown.value == "static"){
            $scope.opConfig.fetchStaticInfoFromServer.showInputFields = true;
            $scope.opConfig.fetchDynamicInfoFromServer.showInputField = false;
        }
        if ($scope.opConfig.fetchInfoFromServerDropDown.value == "dynamic"){
            $scope.opConfig.fetchDynamicInfoFromServer.showInputField = true;
            $scope.opConfig.fetchStaticInfoFromServer.showInputFields = false;
        }
    }

    var getOpConfigurationSuccessCallback = function (data, status, headers, config) {
        $scope.opConfig = data;
    };

    var postRequiredInformationSuccessCallback = function (data, status, headers, config) {
        alert("Required information successfully SAVED");
    };

    var getRequiredInformationSuccessCallback = function (data, status, headers, config) {
        var selectedValue = data['supportsDynamciClientRegistration'];
        var client_id = data['client_id'];
        var client_secret = data['client_secret'];

        $("#dynamicRegistration").val(selectedValue);
        $('#requiredInformationClientIdTextField').val(client_id);
        $('#requiredInformationClientSecretTextField').val(client_secret);

        $scope.supportsDynamicClientRegistration = selectedValue != "false";
    };

    var downloadConfigFileSuccessCallback = function (data, status, headers, config) {
        configDict = JSON.stringify(data["configDict"])
        var a = document.createElement("a");
        a.download = "config.json";
        a.href = "data:text/plain;base64," + btoa(configDict);

        //Appending the element a to the body is only necessary for the download to work in firefox
        document.body.appendChild(a)
        a.click();
        document.body.removeChild(a)

        //e.preventDefault();
        //alert("Target json successfully DOWNLOADED");
    };

    var reloadConfigFileSuccessCallback = function (data, status, headers, config) {
        alert("Target json successfully REFRESHED");
    };

    var updateConfigFields = function(){
        opConfigurationFactory.getOpConfig().success(getOpConfigurationSuccessCallback).error(errorCallback);
    }

    var uploadConfigFileSuccessCallback = function (data, status, headers, config) {
        alert("Target json successfully UPLOADED");
        $("#modalWindowUploadConfigurationFile").modal('toggle');
        updateConfigFields();
    };

    var createNewConfigFileSuccessCallback = function (data, status, headers, config) {
        //alert("New Target json successfully CREATED");

        updateConfigFields();
        //$scope.$apply();

    };

    var showNoConfigAvailable = function(){
        bootbox.alert("No configurations available. Either the session may have timed out or no configuration has be created or uploaded to the server.");
    }

    var reloadDoesConfigFileExistSuccessCallback = function (data, status, headers, config) {
        var doesConfigFileExist = data['doesConfigFileExist'];

        if (doesConfigFileExist == true){
            updateConfigFields();
        }else{
            showNoConfigAvailable();
        }

    };

    var downloadDoesConfigFileExistSuccessCallback = function (data, status, headers, config) {
        var doesConfigFileExist = data['doesConfigFileExist'];

        if (doesConfigFileExist == true){
            configFileFactory.downloadConfigFile().success(downloadConfigFileSuccessCallback).error(errorCallback);
        }else{
            showNoConfigAvailable();
        }

    };

    var errorCallback = function (data, status, headers, config) {
        bootbox.alert(data.ExceptionMessage);
    };

    $scope.showModalWindowAddConfigFields = function(){
        $("#modalWindowAddConfigFields").modal('toggle');
    }

    $scope.showModalUploadConfigWindow = function(){
        $("#modalWindowUploadConfigurationFile").modal('toggle');
    }

    $scope.test = function () {
        alert("test");
    };

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

    $scope.tryToRemoveInteractionBlock = function (blockId) {
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
                        removeInteractionBlock(blockId);
                        //Manually updating the view since it's the code is executed in a callback function
                        $scope.$apply();
                    }
                }
            }
        });
    }

    var removeInteractionBlock = function (blockId) {
        var interactionList = $scope.opConfig.interactionsBlocks
        var indexToRemove;

        for (var i = 0; i < interactionList.length; i++){
            if (interactionList[i].id == blockId){
                indexToRemove = i;
                break;
            }
        }

        $scope.opConfig.interactionsBlocks.splice(indexToRemove, 1);
    }

    $scope.addElementToList = function(index, label){
        var currentInputField = $scope.opConfig.fetchStaticInfoFromServer.inputFields[index];
        var newConfigTextField = {"index": currentInputField.values.length, "textFieldContent": ""};
        $scope.opConfig.fetchStaticInfoFromServer.inputFields[index].values.splice(currentInputField.values.length ,0, newConfigTextField);
    }

    $scope.removeElementFromList = function(staticProviderConfigFieldIndex, valueListIndex){
        var valueList = $scope.opConfig.fetchStaticInfoFromServer.inputFields[staticProviderConfigFieldIndex].values
        valueList.splice(valueListIndex, 1);
    }

    var hasEnteredRequeredInformation = function(){
        var selectedProviderType = $('#providerType option:selected').val();
        var selectedDynamicRegistration = $('#dynamicRegistration option:selected').val();

        if(selectedProviderType == "default" || selectedDynamicRegistration == "default"){
            return false;
        }
        else if(selectedDynamicRegistration == "false"){

            var clientId = $('#requiredInformationClientIdTextField').val();
            var clientSecret = $('#requiredInformationClientSecretTextField').val();

            if (clientId == "" || clientSecret == ""){
                return false;
            }
        }
        return true;
    }

    $scope.saveConfigurations = function(){

        if (hasEnteredRequeredInformation()){
            postInteractionConfig();
            postProviderConfig();

            var selectedValue = $('#dynamicRegistration option:selected').val();
            var clientId = $('#requiredInformationClientIdTextField').val();
            var clientSecret = $('#requiredInformationClientSecretTextField').val();

            var requiredInformationSummary = {"supportsDynamciClientRegistration": selectedValue, "client_id": clientId, "client_secret": clientSecret}
            requiredInformationConfigFactory.postRequiredInformationConfig(requiredInformationSummary).success(postRequiredInformationSuccessCallback).error(errorCallback);

        }else{
            alert("Please enter all the required information")
        }
    }

    $scope.downloadConfigFile = function(){
        configFileFactory.doesConfigFileExist().success(downloadDoesConfigFileExistSuccessCallback).error(errorCallback);
    }

    $scope.uploadConfigFile = function(){
        var file = document.getElementById("targetFile").files[0];

        if (file) {
            var reader = new FileReader();
            reader.readAsText(file, "UTF-8");
            reader.onload = function (evt) {
                configFileFactory.uploadConfigFile(evt.target.result).success(uploadConfigFileSuccessCallback).error(errorCallback);
                $scope.$apply();
            }
            reader.onerror = function (evt) {
                alert("error reading file");
            }
        }
    }

    $scope.reloadConfigFile = function(){
        configFileFactory.doesConfigFileExist().success(reloadDoesConfigFileExistSuccessCallback).error(errorCallback);
    }

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
                        configFileFactory.createNewConfigFile().success(createNewConfigFileSuccessCallback).error(errorCallback);
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