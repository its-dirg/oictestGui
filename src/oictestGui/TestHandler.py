# -*- coding: utf-8 -*-
from __builtin__ import input
import cgi
import cookielib
from cookielib import LoadError
import copy

import json
import os
import subprocess
from cStringIO import StringIO
import threading
from oic.utils.http_util import Response, ServiceError

import uuid
import ast
import tempfile
import urllib2

import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from oic.oic.message import ProviderConfigurationResponse

from oic.oauth2.message import REQUIRED_LIST_OF_SP_SEP_STRINGS
from oic.oauth2.message import OPTIONAL_LIST_OF_STRINGS
from oic.oauth2.message import OPTIONAL_LIST_OF_SP_SEP_STRINGS
from oic.oauth2.message import REQUIRED_LIST_OF_STRINGS

from bs4 import BeautifulSoup
import sys
from oictest import start_key_server
from oictestGui.my_mozilla_cookie_jar import MyMozillaCookieJar

__author__ = 'haho0032'

class Test:
    #Only used to check to check for new config files this which does nothing useful at the moment
    #CONFIG_FILE_PATH = 'saml2test/configFiles/'
    CONFIG_FILE_KEY = "target"
    COOKIE_FILE_KEY = "cookies"

    def __init__(self, environ=None, start_response=None, session=None, logger=None, lookup=None, config=None, parameters=None, cache=None):
        """
        Constructor for the class.
        :param environ:        WSGI enviroment
        :param start_response: WSGI start_respose
        :param session:        Beaker session
        :param logger:         Class to perform logging.
        """

        #Sets the parameters to a default value in order to make i more testable
        self.environ = environ
        self.start_response = start_response
        self.session = session
        self.logger = logger
        self.lookup = lookup
        self.config = config
        self.parameters = parameters
        self.urls = {
            #Calles made from test OP page
            "test_op" : "test_op.mako",
            "list_tests" : None,
            "run_test" : None,
            "post_final_interaction_data" : None,
            "post_basic_interaction_data" : None,
            "reset_interaction" : None,
            "post_error_report": None,

            #Calles made from Configure OP page
            "op_config" : "op_config.mako",
            "download_config_file" : None,
            "upload_config_file" : None,
            "create_new_config_file": None,
            "does_config_file_exist": None,
            "get_op_config": None,
            "post_op_config": None,
            "validate_cookies": None,

            "" : "op_config.mako",
            "info" : "info.mako",
        }
        self.cache = cache

        self.key_provider = start_key_server(self.config.STATIC_PROVIDER_URL, self.config.STATIC_PROVIDER_SCRIPT_DIR)


    def verify(self, path):
        for url, file in self.urls.iteritems():
            if path == url:
                return True

    def handle(self, path):
        """
        Handles the incoming rest requests
        :param path: The path to the file or function requested by the client
        :return A response which could be encode as Json for example
        """
        if path == "test_op":
            return self.handleShowPage(self.urls[path])
        elif path == "list_tests":
            return self.handleListTests()
        elif path == "run_test":
            return self.handleRunTest()
        elif path == "post_final_interaction_data":
            return self.handlePostFinalInteractionData()
        elif path == "post_basic_interaction_data":
            return self.handlePostBasicInteractionData()
        elif path == "reset_interaction":
            return self.handleResetInteraction()
        elif path == "post_error_report":
            return self.handlePostErrorReport()

        #Calles from config_idp
        elif path == "op_config":
            return self.handleShowPage(self.urls[path])
        elif path == "download_config_file":
            return self.handleDownloadConfigFile()
        elif path == "upload_config_file":
            return self.handleUploadConfigFile()
        elif path == "create_new_config_file":
            return self.handleCreateNewConfigFile()
        elif path == "does_config_file_exist":
            return self.handleDoesConfigFileExist()
        elif path == "get_op_config":
            return self.handleGetConfigGuiStructure()
        elif path == "post_op_config":
            return self.handlePostOpConfigurations()
        elif path == "validate_cookies":
            return self.handleValidateCookies()

        elif path == "":
            return self.handleShowPage(self.urls[path])
        elif path == "info":
            return self.handleShowPage(self.urls[path])

    def convertRequiredInfoFromOpConfigToConfigFile(self, configGuiStructure, configFileDict):
        """
        Converts required information in the web interface to the
        a configuration dictionary which follows the "Configuration file structure", see setup.rst
        :param configGuiStructure: Data structure used to hold and show configuration information in the Gui
        :param configFileDict: configuration dictionary which follows the "Configuration file structure"
        :return Configuration dictionary updated with the new required information
        """
        support_dynamic_client_registration = configGuiStructure['dynamicClientRegistrationDropDown']['value'] == 'yes'

        configFileDict['features']['registration'] = support_dynamic_client_registration

        if not support_dynamic_client_registration:
            for attribute in configGuiStructure['supportsStaticClientRegistrationTextFields']:
                if attribute['id'] == 'client_id':
                    configFileDict['client']['client_id'] = attribute['textFieldContent']
                elif attribute['id'] == 'client_secret':
                    configFileDict['client']['client_secret'] = attribute['textFieldContent']

        else:
            try:
                del configFileDict['client']['client_id']
            except KeyError:
                pass

            try:
                del configFileDict['client']['client_secret']
            except KeyError:
                pass

        configFileDict['containsUnsupportedLoginFeatures'] = configGuiStructure['unsupportedLoginFeatures']

        return configFileDict

    def convertInteractionsFromOpConfigToConfigFile(self, configGuiStructure, configFileDict):
        """
        Converts interaction blocks in the internal data structure and updates the configDict
        which follows the "Configuration file structure", see setup.rst
        :param configGuiStructure: Data structure used to hold and show configuration information in the Gui
        :param configFileDict: configuration dictionary which follows the "Configuration file structure"
        :return Configuration dictionary updated with the new interaction blocks
        """
        convertedInteractionBlockList = []

        for interactionBlock in configGuiStructure["interactionsBlocks"]:
            for inputField in interactionBlock['inputFields']:
                if inputField['label'] == 'title':
                    title = inputField['textFieldContent']
                if inputField['label'] == 'url':
                    url = inputField['textFieldContent']
                if inputField['label'] == 'pageType':
                    pageType = inputField['textFieldContent']
                if inputField['label'] == 'index':
                    index = inputField['textFieldContent']
                if inputField['label'] == 'set':
                    set = inputField['textFieldContent']
                if inputField['label'] == 'type':
                    type = inputField['textFieldContent']

            if set != "":
                set = json.loads(set)
            else:
                set = {}

            newInteractionBlock = {
                "matches":{
                    "url" : url,
                    "title" : title
                },
                "page-type": pageType,
                "control" : {
                    "set" : set,
                    "type" : type,
                    "index" : index
                }
            }

            convertedInteractionBlockList.append(newInteractionBlock)

        configFileDict['interaction'] = convertedInteractionBlockList
        return configFileDict

    def convertInputFiledListToSimpleList(self, inputFieldValueList):
        """
        :param inputFieldValueList: A list of dictionaries, where every dictionary contains two keys named index and textFieldContent.
        :return A list where every element is the content of a STATIC_INPUT_FIELD_LIST, see Internal_data_structure
        """
        valueList = []

        for element in inputFieldValueList:
            valueList.append(element['textFieldContent'])

        return valueList

    def convertStaticInfoFromOpConfigToConfigFile(self, configGuiStructure, configFileDict):
        """
        Converts static information in the internal data structure and updates the configDict
        which follows the "Configuration file structure", see setup.rst
        :param configGuiStructure: Data structure used to hold and show configuration information in the Gui
        :param configFileDict: configuration dictionary which follows the "Configuration file structure"
        :return Configuration dictionary updated with the new static information
        """
        visibleInputFieldList = []
        providerAttributeDict = {}

        for inputField in configGuiStructure['fetchStaticInfoFromServer']['inputFields']:
            if inputField['show'] == True:
                visibleInputFieldList.append(inputField)

        for visibleInputField in visibleInputFieldList:
            attributId =  visibleInputField['id']

            if visibleInputField['isList']:
                providerAttributeDict[attributId] = self.convertInputFiledListToSimpleList(visibleInputField['values'])
            else:
                providerAttributeDict[attributId] = visibleInputField['values'][0]['textFieldContent']

        return configFileDict

    def convertOpConfigToConfigFile(self, configGuiStructure):
        """
        Converts the internal data structure to a dictionary which follows the "Configuration file structure", see setup.rst
        :param configGuiStructure: Data structure used to hold and show configuration information in the Gui
        :return A dictionary which follows the "Configuration file structure", see setup.rst
        """
        configString = self.getConfigFile()
        configDict = json.loads(configString)

        if configGuiStructure['fetchDynamicInfoFromServer']['showInputField'] == True:
            dynamicInputFieldValue = configGuiStructure['fetchDynamicInfoFromServer']['inputField']['value']
            configDict['provider'] = {"dynamic": dynamicInputFieldValue}

        elif configGuiStructure['fetchStaticInfoFromServer']['showInputFields'] == True:
            configDict = self.convertStaticInfoFromOpConfigToConfigFile(configGuiStructure, configDict);

        configDict = self.convertRequiredInfoFromOpConfigToConfigFile(configGuiStructure, configDict);
        configDict = self.convertInteractionsFromOpConfigToConfigFile(configGuiStructure, configDict);

        configDict['client']['preferences']['subject_type'] = configGuiStructure["clientSubjectType"]["value"]

        if configGuiStructure['loginCookies'] != "":
            configDict['login_cookies'] = configGuiStructure['loginCookies']

        return json.dumps(configDict)

    def handlePostOpConfigurations(self):
        """
        Saves the data added in the web interface to the session
        :param opConfigurations: Internal data structure containing all info gathered in the web interface
        :return A default Json structure, which should be ignored
        """
        opConfigurations = self.parameters['opConfigurations']
        self.setConfigFile(self.convertOpConfigToConfigFile(opConfigurations))
        return self.returnJSON({})

    def handleValidateCookies(self):
        cookies = self.parameters['cookies']

        cookie_temp_file = tempfile.NamedTemporaryFile()
        cookie_temp_file.write(cookies)

        cj = MyMozillaCookieJar(cookie_temp_file.name)
        cookie_temp_file.flush()

        try:
            cj.load()
            cookie_temp_file.close()
        except Exception as ve:
            return self.serviceError(ve.message)

        return self.returnJSON({})

    def isPyoidcMessageList(self, fieldType):
        if fieldType == REQUIRED_LIST_OF_SP_SEP_STRINGS:
            return True
        elif fieldType == OPTIONAL_LIST_OF_STRINGS:
            return True
        elif fieldType == OPTIONAL_LIST_OF_SP_SEP_STRINGS:
            return True
        elif fieldType == REQUIRED_LIST_OF_STRINGS:
            return True
        return False

    def generateStaticInputFields(self):
        """
        Generates all static input fields based on ProviderConfigurationResponse class localed in [your path]/pyoidc/scr/oic/oic/message.py
        :return The static input fields presented as the internal data structure
        """
        staticProviderConfigKeyList = ProviderConfigurationResponse.c_param.keys()
        staticProviderConfigKeyList.sort()
        staticProviderConfigFieldsDict = ProviderConfigurationResponse.c_param

        staticProviderConfigFieldsList = []

        for staticFieldLabel in staticProviderConfigKeyList:
            staticFieldType = staticProviderConfigFieldsDict[staticFieldLabel]
            configField = {"id": staticFieldLabel, "label": staticFieldLabel, "values": [{"index": 0, "textFieldContent": ""}], "show": False, "isList": self.isPyoidcMessageList(staticFieldType)}
            staticProviderConfigFieldsList.append(configField)

        return staticProviderConfigFieldsList

    def createNewConfigurationDict(self):
        """
        :return Returns a new configuration which follows the internal data structure
        """
        staticInputFieldsList = self.generateStaticInputFields();
        opConfigurations = {
            "fetchInfoFromServerDropDown": {
                "name": "How does the application fetch information from the server? If the provider supports discovery choose dynamic.",
                "value": "",
                "values": [{"type": "dynamic", "name": "dynamic"},
                           {"type": "static", "name": "static"}]
            },
            "fetchStaticInfoFromServer": {"showInputFields": False, "inputFields": staticInputFieldsList},
            "fetchDynamicInfoFromServer": {"showInputField": False,
                                           "inputField": {"label": "Dynamic (where to find the provider information)", "value": "", "show": False, "isList": False}},
            "dynamicClientRegistrationDropDown": {
                "label": "Do your application support dynamic client registration?",
                "value": "",
                "values": [{"type": "yes", "name": "yes"},
                           {"type": "no", "name": "no"}]
            },
            "supportsStaticClientRegistrationTextFields":[
                {"id": "client_id", "label": "Client id", "textFieldContent": ""},
                {"id": "client_secret", "label": "Client secret", "textFieldContent": ""}],

            "unsupportedLoginFeatures": {
                "label": "Do the OP login page contain javascript, caption or other unsupported features?",
                "value": "no",
                "values": [{"type": "yes", "name": "yes"},
                           {"type": "no", "name": "no"}]
            },

            "clientSubjectType":{
                "label": "Select subject identifier type which the client should use: ",
                "value": "",
                "values": [{"type": "public", "name": "public"},
                           {"type": "pairwise", "name": "pairwise"}]
            },

            "interactionsBlocks": [],

            "loginCookies": ""
        }
        return opConfigurations

    def containElements(self, any_structure):
        if any_structure:
            return True
        else:
            return False

    def convertDynamicProviderData(self, configFileDict, configGuiStructure):
        """
        Converts the configuration file structure to the Internal data structure
        :param configGuiStructure: Data structure used to hold and show configuration information in the Gui
        :param configFileDict: Internal data structure containing all info gathered in the web interface
        :return The updated presentation of the internal data structure
        """
        configGuiStructure["fetchInfoFromServerDropDown"]["value"] = "dynamic"
        configGuiStructure["fetchDynamicInfoFromServer"]["showInputField"] = True
        configGuiStructure["fetchDynamicInfoFromServer"]["inputField"]["value"] = configFileDict["provider"]["dynamic"]

        return configGuiStructure

    def isListInstance(self, element):
        return not isinstance(element, basestring)

    def convertSimpleListToGuiDict(self, simpleList):
        """
        Converts a simple static inputs field list to a valid text field representation
        :param simpleList: The list containing the values of a specific static input field
        :return The internal representation of a static input field
        """
        convertedList = []
        index = 0;

        for element in simpleList:
            convertedList.append({"index": index, "textFieldContent": element})
            index += 1

        return convertedList

    def convertStaticProviderData(self, configFileDict, configGuiStructure):
        """
        Converts a static provider from config file to a gui structure
        :param configGuiStructure: Data structure used to hold and show configuration information in the Gui
        :param configFileDict: The configuration file from which the configuration static provider data should be gathered
        :return The updated configuration GUI data structure
        """
        configGuiStructure["fetchInfoFromServerDropDown"]["value"] = "static"
        configGuiStructure["fetchStaticInfoFromServer"]["showInputFields"] = True

        for inputFieldId in configFileDict["provider"]:
            for inputField in configGuiStructure["fetchStaticInfoFromServer"]["inputFields"]:
                if inputField['id'] == inputFieldId:
                    inputField['show'] = True
                    if self.isListInstance(configFileDict["provider"][inputFieldId]):
                        inputField['values'] = self.convertSimpleListToGuiDict(configFileDict["provider"][inputFieldId])
                    else:
                        inputField['values'] = [{"index": 0, "textFieldContent": configFileDict["provider"][inputFieldId]}]

        return configGuiStructure

    def convertRequiredInfo(self, configFileDict, configGuiStructure):
        """
        Converts a required information from config file to a config GUI structure
        :param configGuiStructure: Data structure used to hold and show configuration information in the Gui
        :param configFileDict: The configuration file from which the configuration required information data should be gathered
        :return The updated configuration GUI data structure
        """
        containsRequiredInfo = True

        if "client_id" in configFileDict["client"]:
            containsRequiredInfo = False
            configGuiStructure["dynamicClientRegistrationDropDown"]["value"] = "no"

            for textFiled in configGuiStructure["supportsStaticClientRegistrationTextFields"]:
                if textFiled["id"] == "client_id":
                    textFiled["textFieldContent"] = configFileDict["client"]["client_id"]

        if "client_secret" in configFileDict["client"]:
            containsRequiredInfo = False
            configGuiStructure["dynamicClientRegistrationDropDown"]["value"] = "no"

            for textFiled in configGuiStructure["supportsStaticClientRegistrationTextFields"]:
                if textFiled["id"] == "client_secret":
                    textFiled["textFieldContent"] = configFileDict["client"]["client_secret"]

        if containsRequiredInfo:
            configGuiStructure["dynamicClientRegistrationDropDown"]["value"] = "yes"

        if "containsUnsupportedLoginFeatures" in configFileDict:
            configGuiStructure['unsupportedLoginFeatures'] = configFileDict['containsUnsupportedLoginFeatures']

        return configGuiStructure


    def convertInteractionBlocksToGuiStructure(self, configFileDict, configGuiStructure):
        """
        Converts a interaction blocks from a config file structure to a config GUI structure
        :param configGuiStructure: Data structure used to hold and show configuration information in the Gui
        :param configFileDict: The configuration file from which the configuration interaction blocks data should be gathered
        :return The updated configuration GUI data structure
        """

        if "interaction" in configFileDict:
            block_id = 0
            for interactionBlock in configFileDict["interaction"]:
                url = interactionBlock["matches"].get("url", "")
                title = interactionBlock["matches"].get("title", "")
                pageType = interactionBlock.get("page-type", "")
                set = interactionBlock["control"].get("set", {})
                type = interactionBlock["control"].get("type", "")
                index = interactionBlock["control"].get("index", 0)

                newInteractionBlock = {"id": block_id, "inputFields": [
                    {"label": "title", "textFieldContent": title},
                    {"label": "url", "textFieldContent": url},
                    {"label": "pageType", "textFieldContent": pageType},
                    {"label": "index", "textFieldContent": index},
                    {"label": "set", "textFieldContent": json.dumps(set)},
                    {"label": "type", "textFieldContent": type}
                ]}

                block_id += 1

                configGuiStructure["interactionsBlocks"].append(newInteractionBlock)

        return configGuiStructure

    def convertToConfigGuiStructure(self, configFileDict):
        """
        Converts a config file structure to a config GUI structure
        :param configFileDict: The configuration file from which should be converted
        :return The updated configuration GUI data structure
        """
        configStructureDict = self.createNewConfigurationDict()

        if "dynamic" in configFileDict["provider"]:
            configStructureDict = self.convertDynamicProviderData(configFileDict, configStructureDict)

        elif self.containElements(configFileDict["provider"]):
            #Now we know it's an static provider
            configStructureDict = self.convertStaticProviderData(configFileDict, configStructureDict)

        configStructureDict = self.convertRequiredInfo(configFileDict, configStructureDict)
        configStructureDict = self.convertInteractionBlocksToGuiStructure(configFileDict, configStructureDict)

        configStructureDict["clientSubjectType"]["value"] = configFileDict['client']['preferences']['subject_type'];

        if 'login_cookies' in configFileDict:
            configStructureDict['loginCookies'] = configFileDict['login_cookies']

        return configStructureDict

    def handleGetConfigGuiStructure(self):
        """
        Handles the get config Gui structure request
        :return A configuration Gui structure which is based on the configuration file saved in the session
        """
        if self.CONFIG_FILE_KEY in self.session:
            configString = self.getConfigFile()
            try:
                configDict = json.loads(configString)
                configGuiStructure = self.convertToConfigGuiStructure(configDict)
                return self.returnJSON(json.dumps(configGuiStructure))
            except ValueError:
                return self.serviceError("No JSON object could be decoded. Please check if the file is a valid json file")
        return self.serviceError("No file saved in this current session")


    #TODO enter Dirgs mail settings
    def handlePostErrorReport(self):
        """
        Sends a error report which contains a message and the last test results to Dirgs mail
        :return A default value which should be ignored
        """
        reportEmail = self.parameters['reportEmail']
        reportMessage = self.parameters['reportMessage']
        testResults = self.parameters['testResults']

        fromAdress = reportEmail
        toAddress  = 'drig@example.com'

        message = MIMEMultipart()
        message['From'] = fromAdress
        message['To'] = toAddress
        message['Subject'] = "Error report (saml2test)"

        filename = "error_report.txt"
        attachment = MIMEText(testResults)
        attachment.add_header('Content-Disposition', 'attachment', filename=filename)
        message.attach(attachment)

        message.attach(MIMEText(reportMessage, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login("gmail username", "gmail password")
        text = message.as_string()
        server.sendmail(fromAdress, toAddress, text)

        return self.returnJSON({})


    def handleDoesConfigFileExist(self):
        """
        Handles the request checking if the configuration file exists
        :return Returns a dictionary {"doesConfigFileExist" : true} if the session contains a config file else {"doesConfigFileExist" : false}
        """
        result = json.dumps({"doesConfigFileExist": (self.CONFIG_FILE_KEY in self.session)})
        return self.returnJSON(result)


    def handleShowPage(self, file):
        """
        Handles the request for specific web page
        :param file: The name of the .mako file requested by the user
        :return The html page which is based on the .mako file
        """
        resp = Response(mako_template=file,
                        template_lookup=self.lookup,
                        headers=[])
        argv = {
            "a_value": "Hello world"
        }

        return resp(self.environ, self.start_response, **argv)


    def generateTreeLayouts(self):
        """
        Generates the three tree layouts
        :return A dictionary contain the three tree layouts.
        """
        allTests = json.loads(self.cache["test_list"])
        childTestsList, rootTestsList = self.identifyRootTests(allTests)
        bottomUpTree = self.insertRemaningChildTestsBottomUp(childTestsList, rootTestsList)
        self.setupTestId(bottomUpTree)

        result = {
            "bottomUpTree": bottomUpTree,
        }
        return result

    def handleListTests(self):
        """
        Run the underlying script in order to get a list containing all available tests
        :return A list wit all the available tests
        """
        if "handleList_result" not in self.cache:

            if "test_list" not in self.cache:
                ok, p_out, p_err = self.runScript([self.config.OICC_PATH, '-l'])
                if ok:
                    self.cache["test_list"] = p_out
            else:
                ok = True

            result = self.generateTreeLayouts()

            self.cache["handleList_result"] = result
        else:
            result = self.cache["handleList_result"]
            ok = True

        if (ok):
            myJson = json.dumps(result)
        else:
            return self.serviceError("Cannot list the tests.")
        return self.returnJSON(myJson)


    def writeToConfig(self, password=None, username=None, usernameNameTag=None, passwordNameTag=None):
        """
        Write user login details to the config file
        """
        interactionParameters = self.getInteractions()

        title = interactionParameters['title']
        redirectUri = interactionParameters['redirectUri']
        pageType = interactionParameters['pageType']
        controlType = interactionParameters['controlType']

        configFileAsString = self.getConfigFile()
        configFileAsDict = json.loads(configFileAsString)

        #create the new interaction object based on the parameters
        if password == None or username == None:
            set = {}
        else:
            set = {usernameNameTag: username, passwordNameTag: password}

        newInteraction = [
            {
                "matches": {
                    "url": redirectUri,
                    "title": title
                },
                "page-type": pageType,
                "control": {
                    "index": 0,
                    "type": controlType,
                    "set": set
                }
            }
        ]

        if not('interaction' in configFileAsDict):
            configFileAsDict['interaction'] = []

        configFileAsDict['interaction'].extend(newInteraction)

        self.setConfigFile(json.dumps(configFileAsDict))

    config_tread_lock = threading.Lock()

    def getConfigFile(self):
        with Test.config_tread_lock:
            return self.session[self.CONFIG_FILE_KEY]

    def setConfigFile(self, configDict):
        with Test.config_tread_lock:
            self.session[self.CONFIG_FILE_KEY] = configDict

    interaction_tread_lock = threading.Lock()

    def getInteractions(self):
        with Test.interaction_tread_lock:
            return self.session['interactionParameters']

    def setInteractions(self, interactions):
        with Test.interaction_tread_lock:
            self.session['interactionParameters'] = interactions


    def handlePostFinalInteractionData(self):
        """
        Adds the username and the password in order to complete the interaction gathering cycle
        :return Returns a script tags which tells the gui to make a post back
        """
        try:
            usernameNameTag = self.parameters['usernameNameTag'][0]
            passwordNameTag = self.parameters['passwordNameTag'][0]

            username = self.parameters[usernameNameTag][0]
            password = self.parameters[passwordNameTag][0]

            self.writeToConfig(password, username, usernameNameTag, passwordNameTag)
        except KeyError:
            self.writeToConfig()

        htmlString = "<script>parent.postBack();</script>"
        return self.returnHTML(htmlString)


    def handlePostBasicInteractionData(self):
        """
        Adds the basic interaction information which doesn't need users input
        :return Default response, should be ignored
        """
        title = self.parameters['title']
        redirectUri = self.parameters['redirectUri']
        pageType = self.parameters['pageType']
        controlType = self.parameters['controlType']

        newInteraction = {"title": title, "redirectUri": redirectUri, "pageType": pageType, "controlType": controlType}
        self.setInteractions(newInteraction)

        return self.returnJSON(json.dumps(self.parameters['loginForm']))


    def handleResetInteraction(self):
        """
        Removes previously collected interaction details
        :return Default response, should be ignored
        """
        targetStringContent = self.getConfigFile()
        targetDict = ast.literal_eval(targetStringContent)
        targetDict['interaction'] = []
        self.setConfigFile(str(targetDict))

        return self.returnHTML("<h1>Data</h1>")


    def handleRunTest(self):
        """
        Executes a test
        :return The result of the executed test
        """
        testToRun = self.parameters['testname']

        if 'testid' in self.parameters:
            testid = self.parameters['testid']
        else:
            testid = None

        if self.checkIfIncomingTestIsLegal(testToRun):
            try:
                targetStringContent = self.getConfigFile()
                targetDict = json.loads(targetStringContent)
            except TypeError:
                return self.serviceError("No configurations available. Add configurations and try again")

            config_file = tempfile.NamedTemporaryFile()
            json.dump(targetDict, config_file)
            config_file.flush()

            parameterList = [self.config.OICC_PATH,'-H', self.config.HOST, '-J', config_file.name, '-d', '-e', testToRun]
            
            # if self.session[self.COOKIE_FILE_KEY]:
            #     cookie_temp_file = tempfile.NamedTemporaryFile()
            #     cookies = self.session[self.COOKIE_FILE_KEY]
            #     cookie_temp_file.write(cookies)
            #     cookie_temp_file.flush()
            #     parameterList.append("-Ki", cookie_temp_file)

            if self.config.VERIFY_CERTIFICATES == False:
                parameterList.append('-x')

            ok, p_out, p_err = self.runScript(parameterList, self.config.OICTEST_PATH)

            config_file.close()

            # if self.session[self.COOKIE_FILE_KEY]:
            #     cookie_temp_file.close()

            try:
                if (ok):
                    try:
                        result = json.loads(p_out)
                    except ValueError as ve:
                        return self.serviceError("Result for test " + testToRun + " could not be loaded: <br>" + p_out)


                    response = {
                        "result": result,
                        "traceLog": cgi.escape(p_err),
                        "testid": testid
                    }

                    if result['status'] == 5:
                        try:
                            usernameName, passwordName = self.identifyUsernameAndPasswordFields(result['htmlbody'])
                            response['usernameName'] = usernameName
                            response['passwordName'] = passwordName
                        except TypeError:
                            pass
                        except IndexError:
                            return self.serviceError("Could not identify a login form on page:", result['htmlbody'])
                        except Exception as ex:
                            return self.serviceError("Something went wrong when trying to identify username and password input fields")

                    return self.returnJSON(json.dumps(response))
                else:
                    return self.serviceError("Failed to run test")
            except ValueError:
                return self.serviceError("The configuration couldn't be decoded. Check that the configurations is correct and try again.");

        return self.serviceError("The test is not valid")


    def identifyUsernameAndPasswordFields(self, htmlBody):
        html = BeautifulSoup(htmlBody)
        formTags = list(html.find_all('form'))
        firstForm = formTags[0]

        usernameTag = None
        passwordTag = None

        for input in firstForm.find_all('input'):
            if input['type'] == 'text':
                usernameTag = input
            elif input['type'] == "password":
                passwordTag = input

        return usernameTag['name'], passwordTag['name']

    def handleCreateNewConfigFile(self):
        """
        Creates a new config file based on a temple and saves it in the session
        :return Default response, should be ignored
        """
        templateFile = open("src/oictestGui/template_config.json", "r")

        try:
            configString = templateFile.read()
            configDict = json.loads(configString)
            self.setConfigFile(json.dumps(configDict))
        finally:
            templateFile.close()

        print "Create: " + self.getConfigFile()
        return self.returnJSON({})


    def handleUploadConfigFile(self):
        """
        Adds a uploaded config file to the session
        :return Default response, should be ignored
        """
        self.setConfigFile(str(self.parameters['configFileContent']))
        print "Upload target: " + self.getConfigFile()
        return self.returnJSON({})


    def handleDownloadConfigFile(self):
        """
        :return Return the configuration file stored in the session
        """
        configString = self.getConfigFile()
        configDict = json.loads(configString)
        fileDict = json.dumps({"configDict": configDict})

        print "Download target: " + self.getConfigFile()
        return self.returnJSON(fileDict)


    def createNewTestDict(self, item, level=1):
        """
        Creates a new test dictionary
        :param testItem: The test item on which the new test dict should be based upon
        :param level: The level of the test or sub-test are 1 by default
        :return: The new test dict
        """
        newDict = {}
        newDict['id'] = str(item["id"])
        newDict['children'] = []
        newDict['level'] = level
        newDict['testid'] = ""
        newDict['descr'] = str(item["name"]) #TODO "name" ska bytas up mot "descr" men alla test innehåller inte dessa attribut
        return newDict


    def identifyRootTests(self, allTests):
        """
        Identifies the root tests which is all test which doesn't depend on any other test
        :param allTests: A list containing all tests
        :return First it returns a list containing all test tests which depend on other tests. Secondly it returns a
                list containing all root tests.
        """
        childTestsList = []
        rootTestsList = []
        for item in allTests:
            if not ('depends' in item):
                newDict = self.createNewTestDict(item)
                rootTestsList.append(newDict)
            else:
                childTestsList.append(item)
        return childTestsList, rootTestsList


    def setupTestId(self, tree, visible=True):
        """
        Gives every test a unique id add show the root nodes
        :param tree: The tree which should be traversed
        :param visible: Boolean which indicates if the tree node should be visible or not.
        """
        for element in tree:
            element["visible"] = visible
            element["testid"] = uuid.uuid4().urn
            if element["children"] is not None and len(element["children"])>0:
                self.setupTestId(element["children"], False)


    def insertRemaningChildTestsBottomUp(self, childTestsList, leafTestList):
        """
        Inserts the child node according to bottom up tree parsing algorithm
        :param childTestsList: The child tests which depends on other tests
        :param leafTestList: Leaf test are tests that no other test depends upon
        """
        tree = []

        while len(leafTestList) > 0:
            newleafTestsList = []
            leafsToRemove = []

            for leaf in leafTestList:
                for child in childTestsList:
                    parentList = child['depends']

                    for parent in parentList:
                        parent = str(parent)

                        if leaf['id'] == parent:
                            newChild = self.createNewTestDict(child)
                            newChild["children"].append(copy.deepcopy(leaf))
                            newChild["hasChildren"] = True
                            #Gå igenom alla barn och uppdatera deras level med 1
                            self.updateChildrensLevel(newChild);

                            newleafTestsList.append(newChild)
                            leafsToRemove.append(leaf)

            for leaf in leafTestList:
                if not (leaf in leafsToRemove):
                    tree.append(leaf)

            leafTestList = newleafTestsList

        return tree


    def updateChildrensLevel(self, child):
        """
        Updates the level of a specific test
        :param child: The test who level should be updated
        """
        childrenList = child['children']
        for unvisitedChild in childrenList:
            unvisitedChild['level'] = child['level'] + 1
            self.updateChildrensLevel(unvisitedChild)

    def getChildren(self, treeNode):
        """
        :return Collects and returns all children and sub children of a given node
        """
        childrenToVisitList = treeNode['children']
        allChildren = []

        while len(childrenToVisitList) > 0:
            newChildrenToVisitList = []
            for childToVisit in childrenToVisitList:
                grandchildren = childToVisit['children']
                for grandChild in grandchildren:
                    newChildrenToVisitList.append(grandChild)
                childToVisit['children'] = []
                childToVisit['hasChildren'] = False
                childToVisit['level'] = 2
                allChildren.insert(0, childToVisit)

            childrenToVisitList = newChildrenToVisitList
        return allChildren


    def checkIfIncomingTestIsLegal(self, testToVerify):
        """
        Checks if the incoming test is legal
        :param testToVerify: Test to verify
        :return Returns true if test exists in the list of all tests generated by the under lying script else false
        """
        testToRun = None
        if "verify_test_dict" not in self.cache:
            self.cache["verify_test_dict"] = {}
            if "test_list" not in self.cache:
                ok, p_out, p_err = self.runScript([self.config.OICC_PATH, '-l'])
                if ok:
                    self.cache["test_list"] = p_out
            tests = json.loads(self.cache["test_list"])
            for test in tests:
                self.cache["verify_test_dict"][test["id"]] = True
                #if test["id"] == tmpTest:
                #    testToRun = test["id"]
        if testToVerify in self.cache["verify_test_dict"] and self.cache["verify_test_dict"][testToVerify] is True:
            return True
        else:
            return False


    def returnJSON(self, text):
        """
        :return A response with the content type json
        """
        resp = Response(text, headers=[('Content-Type', "application/json")])
        return resp(self.environ, self.start_response)


    def returnHTML(self, text):
        """
        :return A response with the content type html
        """
        resp = Response(text, headers=[('Content-Type', "text/html")])
        return resp(self.environ, self.start_response)


    def returnXml(self, text):
        """
        :return A response with the content type xml
        """
        resp = Response(text, headers=[('Content-Type', "text/xml")])
        return resp(self.environ, self.start_response)


    def serviceError(self, message, html=None):
        """
        :return A error response which is used to show error messages in the client
        """
        message = {"ExceptionMessage": message, "HTML": html}
        resp = ServiceError(json.dumps(message))
        return resp(self.environ, self.start_response)


    def runScript(self, command, working_directory=None):
        """
        Runs a script on the server, by creating a new process on the server.
        :return A tuple where the first element confirms if the script where executed or not. The second is the output
        on stdout and the third is the output on stderr.
        """
        try:
            p = subprocess.Popen(command,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 cwd=working_directory)
            while(True):
                retcode = p.poll() #returns None while subprocess is running
                if(retcode is not None):
                    break
            p_out = p.stdout.read()
            p_err = p.stderr.read()
            return (True, p_out, p_err)
        except Exception as ex:
            self.logger.fatal("Can not run command: +" + ex.message)
            return (False, None, None)