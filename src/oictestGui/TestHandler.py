# -*- coding: utf-8 -*-
import cgi
import copy

import json
import subprocess
from saml2.httputil import Response, ServiceError

import uuid
import ast
import tempfile
import urllib2

import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from oic.oic.message import ProviderConfigurationResponse
from oic.oauth2.message import REQUIRED_LIST_OF_SP_SEP_STRINGS
from oic.oauth2.message import SINGLE_OPTIONAL_STRING
from oic.oauth2.message import OPTIONAL_LIST_OF_STRINGS
from oic.oauth2.message import SINGLE_REQUIRED_STRING
from oic.oauth2.message import OPTIONAL_LIST_OF_SP_SEP_STRINGS
from oic.oauth2.message import SINGLE_OPTIONAL_INT
from oic.oauth2.message import REQUIRED_LIST_OF_STRINGS

__author__ = 'haho0032'

class Test:
    OICC = '/usr/local/bin/oicc.py'
    #Only used to check to check for new config files this which does nothing useful at the moment
    #CONFIG_FILE_PATH = 'saml2test/configFiles/'
    CONFIG_FILE_KEY = "target"

    def __init__(self, environ, start_response, session, logger, lookup, config, parameters, cache):
        """
        Constructor for the class.
        :param environ:        WSGI enviroment
        :param start_response: WSGI start_respose
        :param session:        Beaker session
        :param logger:         Class to perform logging.
        """
        self.environ = environ
        self.start_response = start_response
        self.session = session
        self.logger = logger
        self.lookup = lookup
        self.config = config
        self.parameters = parameters
        self.urls = {
            #Calles from test_idp
            "test_idp" : "test_idp.mako",
            "list_tests" : None,
            "run_test" : None,
            "post_final_interaction_data" : None,
            "post_basic_interaction_data" : None,
            "reset_interaction" : None,
            "post_error_report": None,

            #Calles from config
            "idp_config" : "idp_config.mako",
            "download_config_file" : None,
            "upload_config_file" : None,
            "create_new_config_file": None,
            "does_config_file_exist": None,
            "get_op_config": None,
            "post_op_config": None,

            #Calles from home
            "" : "home.mako"
        }
        self.cache = cache

    def verify(self, path):
        for url, file in self.urls.iteritems():
            if path == url:
                return True


    def handle(self, path):
        #Calles from test_idp
        if path == "test_idp":
            return self.handleTestIDP(self.urls[path])
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
        elif path == "idp_config":
            return self.handleConfigIDP(self.urls[path])
        elif path == "download_config_file":
            return self.handleDownloadConfigFile()
        elif path == "upload_config_file":
            return self.handleUploadConfigFile()
        elif path == "create_new_config_file":
            return self.handleCreateNewConfigFile()
        elif path == "does_config_file_exist":
            return self.handleDoesConfigFileExist()
        elif path == "get_op_config":
            return self.handleGetOpConfigurations()
        elif path == "post_op_config":
            return self.handlePostOpConfigurations()

        #Calls made from home
        elif path == "":
            return self.handleHomePage(self.urls[path])

    def convertRequiredInfoFromOpConfigToConfigFile(self, opConfigurations, configDict):
        if opConfigurations['requiredInfoDropDown']['value'] == 'no':
            for attribute in opConfigurations['requiredInfoTextFields']:
                if attribute['id'] == 'client_id':
                    configDict['client']['client_id'] = attribute['textFieldContent']
                elif attribute['id'] == 'client_secret':
                    configDict['client']['client_secret'] = attribute['textFieldContent']
        return configDict

    def convertInteractionsFromOpConfigToConfigFile(self, opConfigurations, configDict):
        convertedInteractionBlockList = []

        for interactionBlock in opConfigurations["interactionsBlocks"]:
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

            newInteractionBlock = {
               "matches":{
                  "url" : url,
                  "title" : title
               },
               "page-type": pageType,
               "control" : {
                  "set" : json.loads(set),
                  "type" : type,
                  "index" : index
               }
            }

            convertedInteractionBlockList.append(newInteractionBlock)

        configDict['interaction'] = convertedInteractionBlockList
        return configDict

    def convertInputFiledListToSimpleList(self, inputFieldValueList):
        valueList = []

        for element in inputFieldValueList:
            valueList.append(element['textFieldContent'])

        return valueList

    def convertStaticInfoFromOpConfigToConfigFile(self, opConfigurations, configDict):
        visibleInputFieldList = []
        providerAttributeDict = {}

        for inputField in opConfigurations['fetchStaticInfoFromServer']['inputFields']:
            if inputField['show'] == True:
                visibleInputFieldList.append(inputField)

        for visibleInputField in visibleInputFieldList:
            attributId =  visibleInputField['id']

            if visibleInputField['isList']:
                providerAttributeDict[attributId] = self.convertInputFiledListToSimpleList(visibleInputField['values'])
            else:
                providerAttributeDict[attributId] = visibleInputField['values'][0]['textFieldContent']

        return configDict

    def convertOpConfigToConfigFile(self, opConfigurations):
        configString = self.session[self.CONFIG_FILE_KEY]
        configDict = json.loads(configString)

        if opConfigurations['fetchDynamicInfoFromServer']['showInputField'] == True:
            dynamicInputFieldValue = opConfigurations['fetchDynamicInfoFromServer']['inputField']['value']
            configDict['provider'] = {"dynamic": dynamicInputFieldValue}

        elif opConfigurations['fetchStaticInfoFromServer']['showInputFields'] == True:
            configDict = self.convertStaticInfoFromOpConfigToConfigFile(opConfigurations, configDict);

        configDict = self.convertRequiredInfoFromOpConfigToConfigFile(opConfigurations, configDict);
        configDict = self.convertInteractionsFromOpConfigToConfigFile(opConfigurations, configDict);
        return json.dumps(configDict)

    def handlePostOpConfigurations(self):
        #Convert from structur to config file
        opConfigurations = self.parameters['opConfigurations']
        self.session[self.CONFIG_FILE_KEY] = self.convertOpConfigToConfigFile(opConfigurations)
        return self.returnJSON({"asd": 1})

    def isList(self, fieldType):
        if (fieldType == REQUIRED_LIST_OF_SP_SEP_STRINGS):
            return True
        elif (fieldType== OPTIONAL_LIST_OF_STRINGS):
            return True
        elif (fieldType == OPTIONAL_LIST_OF_SP_SEP_STRINGS):
            return True
        elif (fieldType == REQUIRED_LIST_OF_STRINGS):
            return True

        return False


    def generateStaticInputFields(self):
        staticProviderConfigKeyList = ProviderConfigurationResponse.c_param.keys()
        staticProviderConfigKeyList.sort()
        staticProviderConfigFieldsDict = ProviderConfigurationResponse.c_param

        staticProviderConfigFieldsList = []

        for staticFieldLabel in staticProviderConfigKeyList:
            staticFieldType = staticProviderConfigFieldsDict[staticFieldLabel]
            configField = {"id": staticFieldLabel, "label": staticFieldLabel, "values": [{"index": 0, "textFieldContent": ""}], "show": False, "isList": self.isList(staticFieldType)}
            staticProviderConfigFieldsList.append(configField)

        return staticProviderConfigFieldsList

    def createNewConfigurationDict(self):
        staticInputFieldsList = self.generateStaticInputFields();
        configurationDict = {
            "fetchInfoFromServerDropDown": {
                "name": "How does the application fetch information from the server?",
                "value": "",
                "values": [{"type": "dynamic", "name": "dynmic"},
                           {"type": "static", "name": "static"}]
            },
            "fetchStaticInfoFromServer": {"showInputFields": False, "inputFields": staticInputFieldsList},
            "fetchDynamicInfoFromServer": {"showInputField": False,
                                  "inputField": {"label": "dynamic", "value": "", "show": False, "isList": False}},
            "requiredInfoDropDown": {
                "label": "Do your application support dynamic client registration?",
                "value": "",
                "values": [{"type": "yes", "name": "yes"},
                           {"type": "no", "name": "no"}]
            },
            "requiredInfoTextFields":[
                {"id": "client_id", "label": "Client id", "textFieldContent": ""},
                {"id": "client_secret", "label": "Client secret", "textFieldContent": ""}],
            "interactionsBlocks": []
        }
        return configurationDict

    def containElements(self, any_structure):
        if any_structure:
            return True
        else:
            return False

    def convertDynamicProviderData(self, configFileDict, configStructureDict):
        configStructureDict["fetchInfoFromServerDropDown"]["value"] = "dynamic"
        configStructureDict["fetchDynamicInfoFromServer"]["showInputField"] = True
        configStructureDict["fetchDynamicInfoFromServer"]["inputField"]["value"] = configFileDict["provider"]["dynamic"]

        return configStructureDict

    def isListInstance(self, element):
        return not isinstance(element, basestring)

    def convertListToListOfDict(self, list):
        convertedList = []
        index = 0;

        for element in list:
            convertedList.append({"index": index, "textFieldContent": element})
            index += 1

        return convertedList

    def convertStaticProviderData(self, configFileDict, configStructureDict):
        configStructureDict["fetchInfoFromServerDropDown"]["value"] = "static"
        configStructureDict["fetchStaticInfoFromServer"]["showInputFields"] = True

        for inputFieldId in configFileDict["provider"]:
            for inputField in configStructureDict["fetchStaticInfoFromServer"]["inputFields"]:
                if inputField['id'] == inputFieldId:
                    inputField['show'] = True
                    if self.isListInstance(configFileDict["provider"][inputFieldId]):
                        inputField['values'] = self.convertListToListOfDict(configFileDict["provider"][inputFieldId])
                    else:
                        inputField['values'] = [{"index": 0, "textFieldContent": configFileDict["provider"][inputFieldId]}]

        return configStructureDict

    def convertRequiredInfo(self, configFileDict, configStructureDict):
        containsRequiredInfo = True

        if "client_id" in configFileDict["client"]:
            containsRequiredInfo = False
            configStructureDict["requiredInfoDropDown"]["value"] = "no"

            for textFiled in configStructureDict["requiredInfoTextFields"]:
                if textFiled["id"] == "client_id":
                    textFiled["textFieldContent"] = configFileDict["client"]["client_id"]

        if "client_secret" in configFileDict["client"]:
            containsRequiredInfo = False
            configStructureDict["requiredInfoDropDown"]["value"] = "no"

            for textFiled in configStructureDict["requiredInfoTextFields"]:
                if textFiled["id"] == "client_secret":
                    textFiled["textFieldContent"] = configFileDict["client"]["client_secret"]

        if containsRequiredInfo:
            configStructureDict["requiredInfoDropDown"]["value"] = "yes"

        return configStructureDict


    def convertInteractionBlocks(self, configFileDict, configStructureDict):

        numberOfBlocks = len(configStructureDict["interactionsBlocks"])

        if "interaction" in configFileDict:
            for interactionBlock in configFileDict["interaction"]:
                url = interactionBlock["matches"].get("url", "")
                title = interactionBlock["matches"].get("title", "")
                pageType = interactionBlock.get("page-type", "")
                set = interactionBlock["control"].get("set", {})
                type = interactionBlock["control"].get("type", "")
                index = interactionBlock["control"].get("index", 0)

                newInteractionBlock = {"id": numberOfBlocks, "inputFields": [
                                {"label": "title", "textFieldContent": title},
                                {"label": "url", "textFieldContent": url},
                                {"label": "pageType", "textFieldContent": pageType},
                                {"label": "index", "textFieldContent": index},
                                {"label": "set", "textFieldContent": json.dumps(set)},
                                {"label": "type", "textFieldContent": type}
                            ]}

                configStructureDict["interactionsBlocks"].append(newInteractionBlock)

        return configStructureDict

    def convertToConfigDataStructure(self, configFileDict):
        configStructureDict = self.createNewConfigurationDict()

        if "dynamic" in configFileDict["provider"]:
            configStructureDict = self.convertDynamicProviderData(configFileDict, configStructureDict)

        elif self.containElements(configFileDict["provider"]):
            #Now we know it's an static provider
            configStructureDict = self.convertStaticProviderData(configFileDict, configStructureDict)

        configStructureDict = self.convertRequiredInfo(configFileDict, configStructureDict)
        configStructureDict = self.convertInteractionBlocks(configFileDict, configStructureDict)

        return configStructureDict

    def handleGetOpConfigurations(self):
        if self.CONFIG_FILE_KEY in self.session:
            configString = self.session[self.CONFIG_FILE_KEY]
            try:
                configDict = json.loads(configString)
                configStructureDict = self.convertToConfigDataStructure(configDict)
                return self.returnJSON(json.dumps(configStructureDict))
            except ValueError:
                return self.serviceError("No JSON object could be decoded. Please check if the file is a valid json file")
        return self.serviceError("No file saved in this current session")


    #TODO enter Dirgs mail settings
    def handlePostErrorReport(self):

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

        return self.returnJSON({"asd": 1})


    def doesConfigFileExist(self):
        if self.CONFIG_FILE_KEY in self.session:
            return True
        else:
            return False


    def handleDoesConfigFileExist(self):
        result = json.dumps({"doesConfigFileExist": self.doesConfigFileExist()})
        return self.returnJSON(result)


    def handleTestIDP(self, file):
        resp = Response(mako_template=file,
                        template_lookup=self.lookup,
                        headers=[])
        argv = {
            "a_value": "Hello world"
        }

        #TODO only used in development purposes
        #f = open(self.CONFIG_FILE_PATH + "working.json", "r+")
        #self.session[self.CONFIG_KEY] = f.read();
        #f.close()

        return resp(self.environ, self.start_response, **argv)


    def handleConfigIDP(self, file):

        resp = Response(mako_template=file,
                        template_lookup=self.lookup,
                        headers=[])

        argv = {
            "a_value": "Hello world"
        }

        return resp(self.environ, self.start_response, **argv)


    def handleHomePage(self, file):

        resp = Response(mako_template=file,
                        template_lookup=self.lookup,
                        headers=[])

        argv = {
            "a_value": "Hello world"
        }

        return resp(self.environ, self.start_response, **argv)


    def handleListTests(self):
        if "handleList_result" not in self.cache:

            if "test_list" not in self.cache:
                ok, p_out, p_err = self.runScript([self.OICC, '-l'])
                if ok:
                    self.cache["test_list"] = p_out
            else:
                ok = True

            allTests = json.loads(self.cache["test_list"])

            childTestsList, rootTestsList = self.identifyRootTests(allTests)

            topDownChildList = copy.deepcopy(childTestsList)
            topDownRootList = copy.deepcopy(rootTestsList)

            topDownTree = self.insertRemaningChildTestsTopdown(topDownChildList, topDownRootList)
            bottomUpTree = self.insertRemaningChildTestsBottomUp(childTestsList, rootTestsList)

            self.setupTestId(topDownTree)
            self.setupTestId(bottomUpTree)

            flatBottomUpTree = self.convertToFlatBottomTree(bottomUpTree)

            result = {
                "topDownTree": topDownTree,
                "bottomUpTree": bottomUpTree,
                "flatBottomUpTree": flatBottomUpTree
            }

            self.cache["handleList_result"] = result
        else:
            result = self.cache["handleList_result"]
            ok = True

        if (ok):
            myJson = json.dumps(result)
        else:
            return self.serviceError("Cannot list the tests.")
        return self.returnJSON(myJson)


    def writeToConfig(self, password=None, username=None):

        interactionParameters = self.session['interactionParameters']

        title = interactionParameters['title']
        redirectUri = interactionParameters['redirectUri']
        pageType = interactionParameters['pageType']
        controlType = interactionParameters['controlType']

        configFileAsString = self.session[self.CONFIG_FILE_KEY]
        configFileAsDict = json.loads(configFileAsString)

        #create the new interaction object based on the parameters
        if password == None and username == None:
            set = {}
        else:
            set = {"login": username, "password": password}

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

        self.session[self.CONFIG_FILE_KEY] = json.dumps(configFileAsDict)


    def handlePostFinalInteractionData(self):
        try:
            username = self.parameters['login'][0]
            password = self.parameters['password'][0]

            self.writeToConfig(password, username)
        except KeyError:
            self.writeToConfig()

        htmlString = "<script>parent.postBack();</script>"
        return self.returnHTML(htmlString)


    def handlePostBasicInteractionData(self):
        title = self.parameters['title']
        redirectUri = self.parameters['redirectUri']
        pageType = self.parameters['pageType']
        controlType = self.parameters['controlType']

        self.session['interactionParameters'] = {"title": title, "redirectUri": redirectUri, "pageType": pageType, "controlType": controlType}

        return self.returnJSON({"asd": "asd"})


    def handleResetInteraction(self):
        targetStringContent = self.session[self.CONFIG_FILE_KEY]
        targetDict = ast.literal_eval(targetStringContent)
        targetDict['interaction'] = []
        self.session[self.CONFIG_FILE_KEY] = str(targetDict)

        return self.returnHTML("<h1>Data</h1>")


    def handleRunTest(self):
        testToRun = self.parameters['testname']

        if 'testid' in self.parameters:
            testid = self.parameters['testid']
        else:
            testid = None

        if self.checkIfIncommingTestIsLeagal(testToRun):
            try:
                targetStringContent = self.session[self.CONFIG_FILE_KEY]
                targetDict = json.loads(targetStringContent)
            except TypeError:
                return self.serviceError("No configurations available. Add configurations and try again")

            outfile = tempfile.NamedTemporaryFile()

            json.dump(targetDict, outfile)
            outfile.flush()

            #Directs to the folder containing the saml2test config file
            ok, p_out, p_err = self.runScript([self.OICC,'-H', "localhost", '-J', outfile.name, '-d', '-i', testToRun], "./oictest")

            outfile.close()

            try:
                if (ok):
                    response = {
                        "result": json.loads(p_out),
                        "traceLog": cgi.escape(p_err),
                        "testid": testid
                    }
                    return self.returnJSON(json.dumps(response))
                else:
                    return self.serviceError("Failed to run test")
            except ValueError:
                return self.serviceError("The configuration couldn't be decoded, it's possible that the metadata isn't correct. Check that the configurations is correct and try again.");

        return self.serviceError("The test is not valid")



    def handleCreateNewConfigFile(self):
        templateFile = open("src/oictestGui/template_config.json", "r")

        try:
            configString = templateFile.read()
            configDict = json.loads(configString)
            self.session[self.CONFIG_FILE_KEY] = json.dumps(configDict)
        finally:
            templateFile.close()

        print "Create: " + self.session[self.CONFIG_FILE_KEY]
        return self.returnJSON({"asd": 1})


    def handleUploadConfigFile(self):
        self.session[self.CONFIG_FILE_KEY] = str(self.parameters['configFileContent'])
        print "Upload target: " + self.session[self.CONFIG_FILE_KEY]
        return self.returnJSON({"target": "asd"})


    def handleDownloadConfigFile(self):
        configString = self.session[self.CONFIG_FILE_KEY]
        configDict = json.loads(configString)
        fileDict = json.dumps({"configDict": configDict})

        print "Download target: " + self.session[self.CONFIG_FILE_KEY]
        return self.returnJSON(fileDict)


    def createNewTestDict(self, item, level=1):
        newDict = {}
        newDict['id'] = str(item["id"])
        newDict['children'] = []
        newDict['level'] = level
        newDict['testid'] = ""
        newDict['descr'] = str(item["name"]) #"name" ska bytas up mot "descr" men alla test innehåller inte dessa attribut
        return newDict


    def identifyRootTests(self, allTests):
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
        for element in tree:
            element["visible"] = visible
            element["testid"] = uuid.uuid4().urn
            if element["children"] is not None and len(element["children"])>0:
                self.setupTestId(element["children"], False)


    def insertRemaningChildTestsBottomUp(self, childTestsList, leafTestList):
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
        childrenList = child['children']
        for unvisitedChild in childrenList:
            unvisitedChild['level'] = child['level'] + 1
            self.updateChildrensLevel(unvisitedChild)


    def convertToFlatBottomTree(self, bottomUpTree):
        flatBottomUpTree = []
        for rootTest in bottomUpTree:
            newTest = copy.deepcopy(rootTest)
            children = self.getChildren(newTest)
            newTest['children'] = children
            flatBottomUpTree.append(newTest)
        return flatBottomUpTree


    def getChildren(self, child):
        childrenToVisitList = child['children']
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


    def insertRemaningChildTestsTopdown(self, childTestsList, parentList):
        tree = parentList

        while len(childTestsList) > 0:
            newParentTestsList = []
            newChildTestsList = []

            for parent in parentList:
                for child in childTestsList:
                    parentID = child['depends']

                    if len(parentID) == 1:
                        parentID = str(parentID[0])
                    else:
                        pass
                        #Kasta ett fel.

                    if parent['id'] == parentID:
                        childLevel = parent["level"] + 1
                        newChild = self.createNewTestDict(child, childLevel)
                        parent["children"].append(newChild)
                        parent["hasChildren"] = True
                        newParentTestsList.append(newChild)

            for child in childTestsList:
                for newParent in newParentTestsList:
                    if not (child['id'] == newParent['id']):
                        if not (child in newChildTestsList):
                            newChildTestsList.append(child)


            childTestsList = newChildTestsList
            parentList = newParentTestsList
        return tree


    def checkIfIncommingTestIsLeagal(self, tmpTest):
        testToRun = None
        if "verify_test_dict" not in self.cache:
            self.cache["verify_test_dict"] = {}
            if "test_list" not in self.cache:
                ok, p_out, p_err = self.runScript([self.OICC, '-l'])
                if ok:
                    self.cache["test_list"] = p_out
            tests = json.loads(self.cache["test_list"])
            for test in tests:
                self.cache["verify_test_dict"][test["id"]] = True
                #if test["id"] == tmpTest:
                #    testToRun = test["id"]
        if tmpTest in self.cache["verify_test_dict"] and self.cache["verify_test_dict"][tmpTest] is True:
            return True
        else:
            return False


    def returnJSON(self, text):
        resp = Response(text, headers=[('Content-Type', "application/json")])
        return resp(self.environ, self.start_response)


    def returnHTML(self, text):
        resp = Response(text, headers=[('Content-Type', "text/html")])
        return resp(self.environ, self.start_response)


    def returnXml(self, text):
        resp = Response(text, headers=[('Content-Type', "text/xml")])
        return resp(self.environ, self.start_response)


    def serviceError(self, message):
        message = {"ExceptionMessage": message}
        resp = ServiceError(json.dumps(message))
        return resp(self.environ, self.start_response)


    def runScript(self, command, working_directory=None):
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