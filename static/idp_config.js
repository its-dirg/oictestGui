
var app = angular.module('main', ['toaster'])

app.factory('providerConfigFactory', function ($http) {
    return {
        getProviderConfig: function () {
            return $http.get("/get_provider_config");
        },
        postProviderConfig: function (providerConfigSummaryDictionary) {
            return $http.post("/post_provider_config", {"provider_config_summary": providerConfigSummaryDictionary});
        }
    };
});

app.factory('requiredInformationConfigFactory', function ($http) {
    return {
        getRequiredInformationConfig: function () {
            return $http.get("/get_required_information_config");
        },
        postRequiredInformationConfig: function (requiredInformationConfigSummaryDictionary) {
            return $http.post("/post_required_information_config", {"provider_required_information_summary": requiredInformationConfigSummaryDictionary});
        }
    };
});

app.factory('interactionConfigFactory', function ($http) {
    return {
        getInteractionConfig: function () {
            return $http.get("/get_interaction_config");
        },
        postInteractionConfig: function (interactionList) {
            return $http.post("/post_interaction_config", {"interactionList": interactionList});
        }
    };
});

app.factory('uploadMetadataFactory', function ($http) {
    return {
        postMetadataFile: function (metadataFile) {
            return $http.post("/post_metadata_file", {"metadataFile": metadataFile});
        },
        postMetadataUrl: function (metadataUrl) {
            return $http.post("/post_metadata_url", {"metadataUrl": metadataUrl});
        }
    };
});

app.factory('configFileFactory', function ($http) {
    return {

        downloadConfigFile: function () {
            return $http.get("/download_config_file");
        },

        uploadConfigFile: function (configFileContent) {
            return $http.post("/upload_config_file", {"configFileContent": configFileContent});
        },

        sendCreateNewConfigFileRequest: function () {
            return $http.get("/create_new_config_file");
        },

        doesConfigFileExist: function () {
            return $http.get("/does_config_file_exist");
        }

    };
});

app.factory('advancedFieldsFactory', function ($http) {

    return {
        getAdvancedConfigFields: function () {
            return $http.get("/get_advanced_config_fields");
        }
    };
});

app.controller('IndexCtrl', function ($scope, providerConfigFactory, interactionConfigFactory, uploadMetadataFactory, configFileFactory, advancedFieldsFactory, toaster, requiredInformationConfigFactory) {

    $scope.providerConfigurations;
    $scope.convertedInteractionList;
    $scope.configFieldsKeyList;
    $scope.configFieldsViewList

    var staticProviderConfigFieldsTypeDictionary;
    var selectedStaticProviderConfigFields;

    var checkAttributeCheckboxedDownloadedFromServer = function (storedAttributes) {

        $('input:checkbox').each(function () {
            $(this).prop('checked', false);
            for (var i = 0; i < storedAttributes.length; i++) {
                if ($(this).val() == storedAttributes[i]) {
                    $(this).prop('checked', true);
                }
            }
        });

        selectedStaticProviderConfigFields = storedAttributes;
    }

    var calculateIndexOfElement = function (currentConfigFieldViewElement) {
        for (var i = 0; i < $scope.configFieldsViewList.length; i++) {
            if ($scope.configFieldsViewList[i] == currentConfigFieldViewElement) {
                return i;
            }
        }
    }

    var insertAttributeList = function(data, currnetStroredAttribute, currentConfigFieldViewElement) {
        configValueList = data['provider'][currnetStroredAttribute]

        currentConfigFieldViewElement['value'] = data['provider'][currnetStroredAttribute][0];

        var index = calculateIndexOfElement(currentConfigFieldViewElement);

        for (var i = 1; i < configValueList.length; i++) {

            //TODO Något skumt, när man har två ConfigFieldViewElement med samma id så får applikationen frispel. Hamnar i någon slags oändlig loop, verkar ha något med refferenser att göra?

            //alert(currentConfigFieldViewElement['id']);

            $scope.addElementToList(index, currentConfigFieldViewElement['id']+i, configValueList[i]);
        }
    }

    var getProviderConfigSuccessCallback = function (data, status, headers, config) {

        $scope.providerConfigurations = data;
        //alert("Basic config successfully LOADED")

        var storedAttributes = Object.keys(data['provider']).sort();

        generateProviderConfigInputeFields(storedAttributes);

        //Add the values to the list
        for (var j = 0; j < $scope.configFieldsViewList.length; j++){

            var currentConfigFieldViewElement = $scope.configFieldsViewList[j];

            for (var k = 0; k < storedAttributes.length; k++){
                var currnetStroredAttribute = storedAttributes[k];

                if (currentConfigFieldViewElement['id'] == currnetStroredAttribute){

                    var fieldType = staticProviderConfigFieldsTypeDictionary[currnetStroredAttribute];

                    if (isListField(fieldType)) {
                        insertAttributeList(data, currnetStroredAttribute, currentConfigFieldViewElement);
                    } else{
                        currentConfigFieldViewElement['value'] = data['provider'][currnetStroredAttribute];
                    }
                }
            }
        }

        checkAttributeCheckboxedDownloadedFromServer(storedAttributes);
    };

    var getAdvancedConfigSuccessCallback = function (data, status, headers, config) {
        staticProviderConfigFieldsTypeDictionary = data;
        $scope.configFieldsKeyList = Object.keys(data).sort();

        //Removing dynamic since it shouldn't be in the list over static provider fields
        var index = $scope.configFieldsKeyList.indexOf("dynamic");
        $scope.configFieldsKeyList.splice(index ,1);

        //$scope.$apply();
    };

    var postProviderConfigSuccessCallback = function (data, status, headers, config) {
        alert("Provider config successfully SAVED");
    };

    var postMetadataFileSuccessCallback = function (data, status, headers, config) {
        alert("Metadata file successfully SAVED");
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

    var postMetadataUrlSuccessCallback = function (data, status, headers, config) {
        alert("Metadata url successfully SAVED");
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

        //Since no info is stored on the server in the a session it's not necessary to show this info before now
        providerConfigFactory.getProviderConfig().success(getProviderConfigSuccessCallback).error(errorCallback);
        interactionConfigFactory.getInteractionConfig().success(getInteractionConfigSuccessCallback).error(errorCallback);
        requiredInformationConfigFactory.getRequiredInformationConfig().success(getRequiredInformationSuccessCallback).error(errorCallback);
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

    var getInteractionConfigSuccessCallback = function (data, status, headers, config) {

        $scope.convertedInteractionList = data;
        $scope.originalInteractionList = angular.copy(data);

        for (var i = 0; i < data.length; i++){
           $scope.convertedInteractionList[i]['entry']['pagetype'] = data[i]['entry']['page-type']
        }
        //alert("interaction successfully LOADED");
    };

    var postInteractionConfigSuccessCallback = function (data, status, headers, config) {
        alert("interaction successfully SAVED");
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

    var isListField = function(currentFieldType){
        if (currentFieldType == "SINGLE_OPTIONAL_STRING"){
            return false;
        }else if (currentFieldType == "SINGLE_REQUIRED_STRING"){
            return false;
        }else if (currentFieldType == "SINGLE_OPTIONAL_INT"){
            return false;
        }else{
            return true;
        }
    };

    var updateSelectedDropDownListValue = function(attributesToAdd) {
        //Sets the drop-down list to the appropriate value based on the textfields in the uploaded configuration file
        if (attributesToAdd.length > 0) {

            var isDynamicProvider = $.inArray('dynamic', attributesToAdd) > -1;

            if (isDynamicProvider) {
                $("#providerType").val("dynamic");
            }
            else {
                $("#providerType").val("static");
            }
        }
    }

    var generateProviderConfigInputeFields = function (configFieldsToAdd) {
        clearProviderConfigFieldsViewList();

        updateSelectedDropDownListValue(configFieldsToAdd);

        for (var i = 0; i < configFieldsToAdd.length; i++) {
            //alert(configFieldsToAdd[i] +" : "+ staticProviderConfigFieldsTypeDictionary[configFieldsToAdd[i]]);

            var currentFieldType = staticProviderConfigFieldsTypeDictionary[configFieldsToAdd[i]];

            if (isListField(currentFieldType)) {
                $scope.configFieldsViewList.push({"id": configFieldsToAdd[i], "label": configFieldsToAdd[i], "value": "", "isList": true});
            } else {
                $scope.configFieldsViewList.push({"id": configFieldsToAdd[i], "label": configFieldsToAdd[i], "value": "", "isList": false});
            }
        }
    }

    var clearProviderConfigFieldsViewList = function(){
        $scope.configFieldsViewList = [];
    }

    var resetProviderConfigBlock= function(){
        $scope.configFieldsViewList = [];
        $scope.isStaticProvider = false;
        $("#providerType").val("default");
    }

    $scope.summitAdvancedConfigFields = function () {

        selectedStaticProviderConfigFields = []

        $('input:checkbox:checked').each(function(i){
            selectedStaticProviderConfigFields.push($(this).val());
        });

        generateProviderConfigInputeFields(selectedStaticProviderConfigFields);

        $("#modalWindowAddConfigFields").modal('toggle');
    };

    $scope.addInteraction = function () {

        nextIndex = $scope.convertedInteractionList.length

        entry = {"id": nextIndex,
                 "entry": {
                            "matches": {
                                "url": "",
                                "title": "Empty"
                            },
                            "pagetype": "",
                            "control": {
                                "index": "0",
                                "type": "",
                                "set": {}
                            }
                        }
                }

        $scope.convertedInteractionList.push(entry);
        $scope.originalInteractionList.push(entry);
    };

    $scope.tryToRemoveInteraction = function (index) {
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
                        removeInteraction(index);
                    }
                }
            }
        });
    }

    var removeInteraction = function (index) {
        var interactionList = $scope.convertedInteractionList
        var indexToRemove;

        for (var i = 0; i < interactionList.length; i++){
            if (interactionList[i].id == index){
                indexToRemove = i;
                break;
            }
        }

        $scope.convertedInteractionList.splice(indexToRemove, 1);
        $scope.originalInteractionList.splice(indexToRemove, 1);
        //Manually updating the view since it's the code is executed in a callback function
        $scope.$apply();
    }

    var createStaticProviderSummaryDictionary = function (providerConfigSummaryDictionary) {
        for (var i = 0; i < selectedStaticProviderConfigFields.length; i++) {

            var currentConfigField = selectedStaticProviderConfigFields[i];
            var currentConfigFieldType = staticProviderConfigFieldsTypeDictionary[currentConfigField];

            if (isListField(currentConfigFieldType)) {
                providerConfigSummaryDictionary[currentConfigField] = [];
            } else {
                providerConfigSummaryDictionary[currentConfigField] = "";
            }

            $("." + selectedStaticProviderConfigFields[i]).each(function () {
                var currentFieldValue = $(this).val();

                if (isListField(currentConfigFieldType)) {
                    providerConfigSummaryDictionary[currentConfigField].push(currentFieldValue);
                } else {
                    providerConfigSummaryDictionary[currentConfigField] = currentFieldValue;
                }

            });
        }
        return providerConfigSummaryDictionary;
    }

    var postProviderConfig = function(){
        var providerConfigSummaryDictionary = {};

        if ($scope.isStaticProvider){
            providerConfigSummaryDictionary = createStaticProviderSummaryDictionary(providerConfigSummaryDictionary);
        }else{
            var dynamicTextFieldValue = $(".dynamic").first().val();
            providerConfigSummaryDictionary['dynamic'] = dynamicTextFieldValue;
        }

        providerConfigFactory.postProviderConfig(providerConfigSummaryDictionary).success(postProviderConfigSuccessCallback).error(errorCallback);
    }

    $scope.addElementToList = function(index, label){
        $scope.configFieldsViewList.splice(index+1 ,0, {"id": label, "label": "", "value": "", "isListElement": true});
    }

    $scope.addElementToList = function(index, label, value){
        $scope.configFieldsViewList.splice(index+1 ,0, {"id": label, "label": "", "value": value, "isListElement": true});
    }

    $scope.removeElementFromList = function(index){
        $scope.configFieldsViewList.splice(index ,1);
    }

    var postInteractionConfig = function(){

        $(".block").each(function() {

            var thisBlockId = $(this).attr('id');

            var newUrl = $(this).find("#url").val();
            var newTitle = $(this).find("#title").val();
            var newPageType = $(this).find("#pagetype").val();
            var newType = $(this).find("#type").val();
            var newIndex = $(this).find("#index").val();
            var newSet = $(this).find("#set").val();

            for (var i = 0; i < $scope.originalInteractionList.length; i++){
                if ($scope.originalInteractionList[i].id == thisBlockId){

                    $scope.originalInteractionList[i]['entry']['matches']['url'] = newUrl;
                    $scope.originalInteractionList[i]['entry']['matches']['title'] = newTitle;
                    $scope.originalInteractionList[i]['entry']['page-type'] = newPageType;
                    $scope.originalInteractionList[i]['entry']['control']['type'] = newType;
                    $scope.originalInteractionList[i]['entry']['control']['index'] = newIndex;
                    $scope.originalInteractionList[i]['entry']['control']['set'] = JSON.parse(newSet);

                    break;
                }
            }

        });

        interactionConfigFactory.postInteractionConfig($scope.originalInteractionList).success(postInteractionConfigSuccessCallback).error(errorCallback);

    }

    $scope.saveConfigurations = function(){
        //postInteractionConfig();
        //postProviderConfig();

        var selectedValue = $('#dynamicRegistration option:selected').val();
        var clientId = $('#requiredInformationClientIdTextField').val();
        var clientSecret = $('#requiredInformationClientSecretTextField').val();

        var requiredInformationSummary = {"supportsDynamciClientRegistration": selectedValue, "client_id": clientId, "client_secret": clientSecret}
        requiredInformationConfigFactory.postRequiredInformationConfig(requiredInformationSummary).success(postRequiredInformationSuccessCallback).error(errorCallback);
    }

    $scope.uploadMetadataFile = function(){
        var file = document.getElementById("metadataFile").files[0];

        if (file) {
            var reader = new FileReader();
            reader.readAsText(file, "UTF-8");
            reader.onload = function (evt) {

                uploadMetadataFactory.postMetadataFile(evt.target.result).success(postMetadataFileSuccessCallback).error(errorCallback);
                //Has to be done since this code is executed outside of
                $scope.$apply();

                //alert(evt.target.result);
            }
            reader.onerror = function (evt) {
                alert("error reading file");
            }
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
        alert("reloadConfigFile");
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
                        resetProviderConfigBlock();
                        configFileFactory.sendCreateNewConfigFileRequest().success(createNewConfigFileSuccessCallback).error(errorCallback);
                        $scope.$apply();
                    }
                }
            }
        });
    }

    $scope.isStaticProvider = false;
    $scope.supportsDynamicClientRegistration = true;

    $scope.updateProviderConfigurationBySelecedProviderType = function(){
        var selectedValue = $('#providerType option:selected').val();

        //Show dynamic input fields or add static input fields based on seleced value in drop down
        if (selectedValue == "static"){
            clearProviderConfigFieldsViewList();
            $scope.isStaticProvider = true;

        }else if (selectedValue == "dynamic"){
            generateProviderConfigInputeFields(['dynamic']);
            $scope.isStaticProvider = false;

        }else{
            generateProviderConfigInputeFields([]);
            $scope.isStaticProvider = false;
        }
    }

    $scope.updateRequiredDynamicClientRegistrationFields = function(){
        var selectedValue = $('#dynamicRegistration option:selected').val();

        $scope.supportsDynamicClientRegistration = selectedValue != "false";
    }

    $scope.uploadMetadataUrl = function(){
        var metadataUrl = $("#metadataUrl").val();

        uploadMetadataFactory.postMetadataUrl(metadataUrl).success(postMetadataUrlSuccessCallback).error(errorCallback);
    }

    //Execute when loading page
    advancedFieldsFactory.getAdvancedConfigFields().success(getAdvancedConfigSuccessCallback).error(errorCallback);

    $scope.containsRegistrationEndpointTextField = function(){
        return $.inArray('registration_endpoint', selectedStaticProviderConfigFields) > -1;
    }
});

//Loads the menu from a given template file and inserts it it to the <div menu> tag
app.directive('menu', function($http) {
    return {
        restrict: 'A',
        templateUrl: '/static/templateMenu.html'
    }
});