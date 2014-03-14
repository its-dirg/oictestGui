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
            "get_provider_config" : None,
            "post_provider_config" : None,
            "get_interaction_config" : None,
            "post_interaction_config" : None,
            "post_metadata_file" : None,
            "download_config_file" : None,
            "upload_config_file" : None,
            "create_new_config_file": None,
            "does_config_file_exist": None,
            "temp_get_metadata": None,
            "post_metadata_url": None,
            "get_advanced_config_fields": None,
            "get_required_information_config": None,
            "post_required_information_config": None,
            "get_op_config": None,

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
        elif path == "get_provider_config":
            return self.handleGetProviderConfig()
        elif path == "post_provider_config":
            return self.handlePostProviderConfig()
        elif path == "get_interaction_config":
            return self.handleGetInteractionConfig()
        elif path == "post_interaction_config":
            return self.handlePostInteractionConfig()
        elif path == "post_metadata_file":
            return self.handlePostMetadataFile()
        elif path == "download_config_file":
            return self.handleDownloadConfigFile()
        elif path == "upload_config_file":
            return self.handleUploadConfigFile()
        elif path == "create_new_config_file":
            return self.handleCreateNewConfigFile()
        elif path == "does_config_file_exist":
            return self.handleDoesConfigFileExist()
        elif path == "temp_get_metadata":
            return self.handleGetMetadata()
        elif path == "post_metadata_url":
            return self.handlePostMetadataUrl()
        elif path == "get_advanced_config_fields":
            return self.handleGetAdvancedConfigFields()
        elif path == "get_required_information_config":
            return self.handleGetRequiredInformationConfig()
        elif path == "post_required_information_config":
            return self.handlePostRequiredInformationConfig()

        elif path == "get_op_config":
            return self.handleGetOpConfigurations()

        #Calls made from home
        elif path == "":
            return self.handleHomePage(self.urls[path])

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

    def convertRequiredInfo(self, configFileDict, configStructureDict):
        if "client_id" in configFileDict["client"]:
            configStructureDict["requiredInfoDropDown"]["value"] = "no"

            for textFiled in configStructureDict["requiredInfoTextFields"]:
                if textFiled["id"] == "client_id":
                    textFiled["textFieldContent"] = configFileDict["client"]["client_id"]

        if "client_secret" in configFileDict["client"]:
            configStructureDict["requiredInfoDropDown"]["value"] = "no"

            for textFiled in configStructureDict["requiredInfoTextFields"]:
                if textFiled["id"] == "client_secret":
                    textFiled["textFieldContent"] = configFileDict["client"]["client_secret"]
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
                                {"label": "set", "textFieldContent": set},
                                {"label": "type", "textFieldContent": type}
                            ]}

                configStructureDict["interactionsBlocks"].append(newInteractionBlock)

        return configStructureDict

    def convertToConfigDataStructure(self, configFileDict):
        configStructureDict = self.createNewConfigurationDict()

        if "dynamic" in configFileDict["provider"]:
            configStructureDict = self.convertDynamicProviderData(configFileDict, configStructureDict)
            configStructureDict = self.convertRequiredInfo(configFileDict, configStructureDict)
            configStructureDict = self.convertInteractionBlocks(configFileDict, configStructureDict)

        elif self.containElements(configFileDict["provider"]):
            #Now we know it's an static provider
            return

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



    def handleGetRequiredInformationConfig(self):
        configString = self.session[self.CONFIG_FILE_KEY]
        configDict = json.loads(configString)

        try:
            supportsDynamciClientRegistration = configDict['client']['supports_dynamc_client_registration']
            client_id = configDict['client']['client_id']
            client_secret = configDict['client']['client_secret']

            reqiuredInformationDictonary = {"supportsDynamciClientRegistration": supportsDynamciClientRegistration, "client_id": client_id, "client_secret": client_secret}
        except KeyError:
            reqiuredInformationDictonary = {"supportsDynamciClientRegistration": "-", "client_id": "", "client_secret": ""}

        return self.returnJSON(json.dumps(reqiuredInformationDictonary))

    def handlePostRequiredInformationConfig(self):
        configString = self.session[self.CONFIG_FILE_KEY]
        configDict = json.loads(configString)

        requiredInformationSummaryDictonay = self.parameters['provider_required_information_summary']

        configDict['client']['client_id'] = requiredInformationSummaryDictonay['client_id']
        configDict['client']['client_secret'] = requiredInformationSummaryDictonay['client_secret']
        configDict['client']['supports_dynamc_client_registration'] = requiredInformationSummaryDictonay['supportsDynamciClientRegistration']

        self.session[self.CONFIG_FILE_KEY] = json.dumps(configDict)

        return self.returnJSON({"asd": 1})


    def convertAdvancedConfigFieldsDictonary(self, advancedConfigFields):

        newDict = {}

        for key in advancedConfigFields:
            if (advancedConfigFields[key] == REQUIRED_LIST_OF_SP_SEP_STRINGS):
                newDict[key] = "REQUIRED_LIST_OF_SP_SEP_STRINGS"

            elif (advancedConfigFields[key] == SINGLE_OPTIONAL_STRING):
                newDict[key] = "SINGLE_OPTIONAL_STRING"

            elif (advancedConfigFields[key] == OPTIONAL_LIST_OF_STRINGS):
                newDict[key] = "OPTIONAL_LIST_OF_STRINGS"

            elif (advancedConfigFields[key] == SINGLE_REQUIRED_STRING):
                newDict[key] = "SINGLE_REQUIRED_STRING"

            elif (advancedConfigFields[key] == OPTIONAL_LIST_OF_SP_SEP_STRINGS):
                newDict[key] = "OPTIONAL_LIST_OF_SP_SEP_STRINGS"

            elif (advancedConfigFields[key] == SINGLE_OPTIONAL_INT):
                newDict[key] = "SINGLE_OPTIONAL_INT"

            elif (advancedConfigFields[key] == REQUIRED_LIST_OF_STRINGS):
                newDict[key] = "REQUIRED_LIST_OF_STRINGS"

        newDict['dynamic'] = "SINGLE_OPTIONAL_STRING"

        return newDict

    def handleGetAdvancedConfigFields(self):

        advancedConfigFields = ProviderConfigurationResponse.c_param

        convertedAdvancedConfigFields = self.convertAdvancedConfigFieldsDictonary(advancedConfigFields)

        print "Get advanced config fields: " + json.dumps(convertedAdvancedConfigFields)

        return self.returnJSON(json.dumps(convertedAdvancedConfigFields))

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


    def handlePostMetadataUrl(self):
        metadataUrl = self.parameters['metadataUrl']
        metadata = urllib2.urlopen(metadataUrl).read()
        self.addMetdataToSession(metadata)

        print "Post metadata url: " + self.session[self.CONFIG_FILE_KEY]
        return self.returnJSON({"asd": 1})


    def handleGetMetadata(self):
        return self.returnXml("<?xml version='1.0' encoding='UTF-8'?>\n<ns0:EntityDescriptor xmlns:ns0=\"urn:oasis:names:tc:SAML:2.0:metadata\" xmlns:ns1=\"http://www.w3.org/2000/09/xmldsig#\" entityID=\"http://localhost:8088/idp.xml\"><ns0:IDPSSODescriptor WantAuthnRequestsSigned=\"false\" protocolSupportEnumeration=\"urn:oasis:names:tc:SAML:2.0:protocol\"><ns0:KeyDescriptor use=\"encryption\"><ns1:KeyInfo><ns1:X509Data><ns1:X509Certificate>MIIC8jCCAlugAwIBAgIJAJHg2V5J31I8MA0GCSqGSIb3DQEBBQUAMFoxCzAJBgNV\nBAYTAlNFMQ0wCwYDVQQHEwRVbWVhMRgwFgYDVQQKEw9VbWVhIFVuaXZlcnNpdHkx\nEDAOBgNVBAsTB0lUIFVuaXQxEDAOBgNVBAMTB1Rlc3QgU1AwHhcNMDkxMDI2MTMz\nMTE1WhcNMTAxMDI2MTMzMTE1WjBaMQswCQYDVQQGEwJTRTENMAsGA1UEBxMEVW1l\nYTEYMBYGA1UEChMPVW1lYSBVbml2ZXJzaXR5MRAwDgYDVQQLEwdJVCBVbml0MRAw\nDgYDVQQDEwdUZXN0IFNQMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDkJWP7\nbwOxtH+E15VTaulNzVQ/0cSbM5G7abqeqSNSs0l0veHr6/ROgW96ZeQ57fzVy2MC\nFiQRw2fzBs0n7leEmDJyVVtBTavYlhAVXDNa3stgvh43qCfLx+clUlOvtnsoMiiR\nmo7qf0BoPKTj7c0uLKpDpEbAHQT4OF1HRYVxMwIDAQABo4G/MIG8MB0GA1UdDgQW\nBBQ7RgbMJFDGRBu9o3tDQDuSoBy7JjCBjAYDVR0jBIGEMIGBgBQ7RgbMJFDGRBu9\no3tDQDuSoBy7JqFepFwwWjELMAkGA1UEBhMCU0UxDTALBgNVBAcTBFVtZWExGDAW\nBgNVBAoTD1VtZWEgVW5pdmVyc2l0eTEQMA4GA1UECxMHSVQgVW5pdDEQMA4GA1UE\nAxMHVGVzdCBTUIIJAJHg2V5J31I8MAwGA1UdEwQFMAMBAf8wDQYJKoZIhvcNAQEF\nBQADgYEAMuRwwXRnsiyWzmRikpwinnhTmbooKm5TINPE7A7gSQ710RxioQePPhZO\nzkM27NnHTrCe2rBVg0EGz7QTd1JIwLPvgoj4VTi/fSha/tXrYUaqc9AqU1kWI4WN\n+vffBGQ09mo+6CffuFTZYeOhzP/2stAPwCTU4kxEoiy0KpZMANI=\n</ns1:X509Certificate></ns1:X509Data></ns1:KeyInfo></ns0:KeyDescriptor><ns0:KeyDescriptor use=\"signing\"><ns1:KeyInfo><ns1:X509Data><ns1:X509Certificate>MIIC8jCCAlugAwIBAgIJAJHg2V5J31I8MA0GCSqGSIb3DQEBBQUAMFoxCzAJBgNV\nBAYTAlNFMQ0wCwYDVQQHEwRVbWVhMRgwFgYDVQQKEw9VbWVhIFVuaXZlcnNpdHkx\nEDAOBgNVBAsTB0lUIFVuaXQxEDAOBgNVBAMTB1Rlc3QgU1AwHhcNMDkxMDI2MTMz\nMTE1WhcNMTAxMDI2MTMzMTE1WjBaMQswCQYDVQQGEwJTRTENMAsGA1UEBxMEVW1l\nYTEYMBYGA1UEChMPVW1lYSBVbml2ZXJzaXR5MRAwDgYDVQQLEwdJVCBVbml0MRAw\nDgYDVQQDEwdUZXN0IFNQMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDkJWP7\nbwOxtH+E15VTaulNzVQ/0cSbM5G7abqeqSNSs0l0veHr6/ROgW96ZeQ57fzVy2MC\nFiQRw2fzBs0n7leEmDJyVVtBTavYlhAVXDNa3stgvh43qCfLx+clUlOvtnsoMiiR\nmo7qf0BoPKTj7c0uLKpDpEbAHQT4OF1HRYVxMwIDAQABo4G/MIG8MB0GA1UdDgQW\nBBQ7RgbMJFDGRBu9o3tDQDuSoBy7JjCBjAYDVR0jBIGEMIGBgBQ7RgbMJFDGRBu9\no3tDQDuSoBy7JqFepFwwWjELMAkGA1UEBhMCU0UxDTALBgNVBAcTBFVtZWExGDAW\nBgNVBAoTD1VtZWEgVW5pdmVyc2l0eTEQMA4GA1UECxMHSVQgVW5pdDEQMA4GA1UE\nAxMHVGVzdCBTUIIJAJHg2V5J31I8MAwGA1UdEwQFMAMBAf8wDQYJKoZIhvcNAQEF\nBQADgYEAMuRwwXRnsiyWzmRikpwinnhTmbooKm5TINPE7A7gSQ710RxioQePPhZO\nzkM27NnHTrCe2rBVg0EGz7QTd1JIwLPvgoj4VTi/fSha/tXrYUaqc9AqU1kWI4WN\n+vffBGQ09mo+6CffuFTZYeOhzP/2stAPwCTU4kxEoiy0KpZMANI=\n</ns1:X509Certificate></ns1:X509Data></ns1:KeyInfo></ns0:KeyDescriptor><ns0:SingleLogoutService Binding=\"urn:oasis:names:tc:SAML:2.0:bindings:SOAP\" Location=\"http://localhost:8088/slo/soap\" /><ns0:SingleLogoutService Binding=\"urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST\" Location=\"http://localhost:8088/slo/post\" /><ns0:SingleLogoutService Binding=\"urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect\" Location=\"http://localhost:8088/slo/redirect\" /><ns0:ManageNameIDService Binding=\"urn:oasis:names:tc:SAML:2.0:bindings:SOAP\" Location=\"http://localhost:8088/mni/soap\" /><ns0:ManageNameIDService Binding=\"urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST\" Location=\"http://localhost:8088/mni/post\" /><ns0:ManageNameIDService Binding=\"urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect\" Location=\"http://localhost:8088/mni/redirect\" /><ns0:ManageNameIDService Binding=\"urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Artifact\" Location=\"http://localhost:8088/mni/art\" /><ns0:NameIDFormat>urn:oasis:names:tc:SAML:2.0:nameid-format:transient</ns0:NameIDFormat><ns0:NameIDFormat>urn:oasis:names:tc:SAML:2.0:nameid-format:persistent</ns0:NameIDFormat><ns0:SingleSignOnService Binding=\"urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect\" Location=\"http://localhost:8088/sso/redirect\" /><ns0:SingleSignOnService Binding=\"urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST\" Location=\"http://localhost:8088/sso/post\" /><ns0:SingleSignOnService Binding=\"urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Artifact\" Location=\"http://localhost:8088/sso/art\" /><ns0:SingleSignOnService Binding=\"urn:oasis:names:tc:SAML:2.0:bindings:SOAP\" Location=\"http://localhost:8088/sso/ecp\" /><ns0:NameIDMappingService Binding=\"urn:oasis:names:tc:SAML:2.0:bindings:SOAP\" Location=\"http://localhost:8088/nim\" /><ns0:AssertionIDRequestService Binding=\"urn:oasis:names:tc:SAML:2.0:bindings:URI\" Location=\"http://localhost:8088/airs\" /></ns0:IDPSSODescriptor><ns0:AuthnAuthorityDescriptor protocolSupportEnumeration=\"urn:oasis:names:tc:SAML:2.0:protocol\"><ns0:KeyDescriptor use=\"encryption\"><ns1:KeyInfo><ns1:X509Data><ns1:X509Certificate>MIIC8jCCAlugAwIBAgIJAJHg2V5J31I8MA0GCSqGSIb3DQEBBQUAMFoxCzAJBgNV\nBAYTAlNFMQ0wCwYDVQQHEwRVbWVhMRgwFgYDVQQKEw9VbWVhIFVuaXZlcnNpdHkx\nEDAOBgNVBAsTB0lUIFVuaXQxEDAOBgNVBAMTB1Rlc3QgU1AwHhcNMDkxMDI2MTMz\nMTE1WhcNMTAxMDI2MTMzMTE1WjBaMQswCQYDVQQGEwJTRTENMAsGA1UEBxMEVW1l\nYTEYMBYGA1UEChMPVW1lYSBVbml2ZXJzaXR5MRAwDgYDVQQLEwdJVCBVbml0MRAw\nDgYDVQQDEwdUZXN0IFNQMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDkJWP7\nbwOxtH+E15VTaulNzVQ/0cSbM5G7abqeqSNSs0l0veHr6/ROgW96ZeQ57fzVy2MC\nFiQRw2fzBs0n7leEmDJyVVtBTavYlhAVXDNa3stgvh43qCfLx+clUlOvtnsoMiiR\nmo7qf0BoPKTj7c0uLKpDpEbAHQT4OF1HRYVxMwIDAQABo4G/MIG8MB0GA1UdDgQW\nBBQ7RgbMJFDGRBu9o3tDQDuSoBy7JjCBjAYDVR0jBIGEMIGBgBQ7RgbMJFDGRBu9\no3tDQDuSoBy7JqFepFwwWjELMAkGA1UEBhMCU0UxDTALBgNVBAcTBFVtZWExGDAW\nBgNVBAoTD1VtZWEgVW5pdmVyc2l0eTEQMA4GA1UECxMHSVQgVW5pdDEQMA4GA1UE\nAxMHVGVzdCBTUIIJAJHg2V5J31I8MAwGA1UdEwQFMAMBAf8wDQYJKoZIhvcNAQEF\nBQADgYEAMuRwwXRnsiyWzmRikpwinnhTmbooKm5TINPE7A7gSQ710RxioQePPhZO\nzkM27NnHTrCe2rBVg0EGz7QTd1JIwLPvgoj4VTi/fSha/tXrYUaqc9AqU1kWI4WN\n+vffBGQ09mo+6CffuFTZYeOhzP/2stAPwCTU4kxEoiy0KpZMANI=\n</ns1:X509Certificate></ns1:X509Data></ns1:KeyInfo></ns0:KeyDescriptor><ns0:KeyDescriptor use=\"signing\"><ns1:KeyInfo><ns1:X509Data><ns1:X509Certificate>MIIC8jCCAlugAwIBAgIJAJHg2V5J31I8MA0GCSqGSIb3DQEBBQUAMFoxCzAJBgNV\nBAYTAlNFMQ0wCwYDVQQHEwRVbWVhMRgwFgYDVQQKEw9VbWVhIFVuaXZlcnNpdHkx\nEDAOBgNVBAsTB0lUIFVuaXQxEDAOBgNVBAMTB1Rlc3QgU1AwHhcNMDkxMDI2MTMz\nMTE1WhcNMTAxMDI2MTMzMTE1WjBaMQswCQYDVQQGEwJTRTENMAsGA1UEBxMEVW1l\nYTEYMBYGA1UEChMPVW1lYSBVbml2ZXJzaXR5MRAwDgYDVQQLEwdJVCBVbml0MRAw\nDgYDVQQDEwdUZXN0IFNQMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDkJWP7\nbwOxtH+E15VTaulNzVQ/0cSbM5G7abqeqSNSs0l0veHr6/ROgW96ZeQ57fzVy2MC\nFiQRw2fzBs0n7leEmDJyVVtBTavYlhAVXDNa3stgvh43qCfLx+clUlOvtnsoMiiR\nmo7qf0BoPKTj7c0uLKpDpEbAHQT4OF1HRYVxMwIDAQABo4G/MIG8MB0GA1UdDgQW\nBBQ7RgbMJFDGRBu9o3tDQDuSoBy7JjCBjAYDVR0jBIGEMIGBgBQ7RgbMJFDGRBu9\no3tDQDuSoBy7JqFepFwwWjELMAkGA1UEBhMCU0UxDTALBgNVBAcTBFVtZWExGDAW\nBgNVBAoTD1VtZWEgVW5pdmVyc2l0eTEQMA4GA1UECxMHSVQgVW5pdDEQMA4GA1UE\nAxMHVGVzdCBTUIIJAJHg2V5J31I8MAwGA1UdEwQFMAMBAf8wDQYJKoZIhvcNAQEF\nBQADgYEAMuRwwXRnsiyWzmRikpwinnhTmbooKm5TINPE7A7gSQ710RxioQePPhZO\nzkM27NnHTrCe2rBVg0EGz7QTd1JIwLPvgoj4VTi/fSha/tXrYUaqc9AqU1kWI4WN\n+vffBGQ09mo+6CffuFTZYeOhzP/2stAPwCTU4kxEoiy0KpZMANI=\n</ns1:X509Certificate></ns1:X509Data></ns1:KeyInfo></ns0:KeyDescriptor><ns0:AuthnQueryService Binding=\"urn:oasis:names:tc:SAML:2.0:bindings:SOAP\" Location=\"http://localhost:8088/aqs\" /></ns0:AuthnAuthorityDescriptor><ns0:AttributeAuthorityDescriptor protocolSupportEnumeration=\"urn:oasis:names:tc:SAML:2.0:protocol\"><ns0:KeyDescriptor use=\"encryption\"><ns1:KeyInfo><ns1:X509Data><ns1:X509Certificate>MIIC8jCCAlugAwIBAgIJAJHg2V5J31I8MA0GCSqGSIb3DQEBBQUAMFoxCzAJBgNV\nBAYTAlNFMQ0wCwYDVQQHEwRVbWVhMRgwFgYDVQQKEw9VbWVhIFVuaXZlcnNpdHkx\nEDAOBgNVBAsTB0lUIFVuaXQxEDAOBgNVBAMTB1Rlc3QgU1AwHhcNMDkxMDI2MTMz\nMTE1WhcNMTAxMDI2MTMzMTE1WjBaMQswCQYDVQQGEwJTRTENMAsGA1UEBxMEVW1l\nYTEYMBYGA1UEChMPVW1lYSBVbml2ZXJzaXR5MRAwDgYDVQQLEwdJVCBVbml0MRAw\nDgYDVQQDEwdUZXN0IFNQMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDkJWP7\nbwOxtH+E15VTaulNzVQ/0cSbM5G7abqeqSNSs0l0veHr6/ROgW96ZeQ57fzVy2MC\nFiQRw2fzBs0n7leEmDJyVVtBTavYlhAVXDNa3stgvh43qCfLx+clUlOvtnsoMiiR\nmo7qf0BoPKTj7c0uLKpDpEbAHQT4OF1HRYVxMwIDAQABo4G/MIG8MB0GA1UdDgQW\nBBQ7RgbMJFDGRBu9o3tDQDuSoBy7JjCBjAYDVR0jBIGEMIGBgBQ7RgbMJFDGRBu9\no3tDQDuSoBy7JqFepFwwWjELMAkGA1UEBhMCU0UxDTALBgNVBAcTBFVtZWExGDAW\nBgNVBAoTD1VtZWEgVW5pdmVyc2l0eTEQMA4GA1UECxMHSVQgVW5pdDEQMA4GA1UE\nAxMHVGVzdCBTUIIJAJHg2V5J31I8MAwGA1UdEwQFMAMBAf8wDQYJKoZIhvcNAQEF\nBQADgYEAMuRwwXRnsiyWzmRikpwinnhTmbooKm5TINPE7A7gSQ710RxioQePPhZO\nzkM27NnHTrCe2rBVg0EGz7QTd1JIwLPvgoj4VTi/fSha/tXrYUaqc9AqU1kWI4WN\n+vffBGQ09mo+6CffuFTZYeOhzP/2stAPwCTU4kxEoiy0KpZMANI=\n</ns1:X509Certificate></ns1:X509Data></ns1:KeyInfo></ns0:KeyDescriptor><ns0:KeyDescriptor use=\"signing\"><ns1:KeyInfo><ns1:X509Data><ns1:X509Certificate>MIIC8jCCAlugAwIBAgIJAJHg2V5J31I8MA0GCSqGSIb3DQEBBQUAMFoxCzAJBgNV\nBAYTAlNFMQ0wCwYDVQQHEwRVbWVhMRgwFgYDVQQKEw9VbWVhIFVuaXZlcnNpdHkx\nEDAOBgNVBAsTB0lUIFVuaXQxEDAOBgNVBAMTB1Rlc3QgU1AwHhcNMDkxMDI2MTMz\nMTE1WhcNMTAxMDI2MTMzMTE1WjBaMQswCQYDVQQGEwJTRTENMAsGA1UEBxMEVW1l\nYTEYMBYGA1UEChMPVW1lYSBVbml2ZXJzaXR5MRAwDgYDVQQLEwdJVCBVbml0MRAw\nDgYDVQQDEwdUZXN0IFNQMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDkJWP7\nbwOxtH+E15VTaulNzVQ/0cSbM5G7abqeqSNSs0l0veHr6/ROgW96ZeQ57fzVy2MC\nFiQRw2fzBs0n7leEmDJyVVtBTavYlhAVXDNa3stgvh43qCfLx+clUlOvtnsoMiiR\nmo7qf0BoPKTj7c0uLKpDpEbAHQT4OF1HRYVxMwIDAQABo4G/MIG8MB0GA1UdDgQW\nBBQ7RgbMJFDGRBu9o3tDQDuSoBy7JjCBjAYDVR0jBIGEMIGBgBQ7RgbMJFDGRBu9\no3tDQDuSoBy7JqFepFwwWjELMAkGA1UEBhMCU0UxDTALBgNVBAcTBFVtZWExGDAW\nBgNVBAoTD1VtZWEgVW5pdmVyc2l0eTEQMA4GA1UECxMHSVQgVW5pdDEQMA4GA1UE\nAxMHVGVzdCBTUIIJAJHg2V5J31I8MAwGA1UdEwQFMAMBAf8wDQYJKoZIhvcNAQEF\nBQADgYEAMuRwwXRnsiyWzmRikpwinnhTmbooKm5TINPE7A7gSQ710RxioQePPhZO\nzkM27NnHTrCe2rBVg0EGz7QTd1JIwLPvgoj4VTi/fSha/tXrYUaqc9AqU1kWI4WN\n+vffBGQ09mo+6CffuFTZYeOhzP/2stAPwCTU4kxEoiy0KpZMANI=\n</ns1:X509Certificate></ns1:X509Data></ns1:KeyInfo></ns0:KeyDescriptor><ns0:AttributeService Binding=\"urn:oasis:names:tc:SAML:2.0:bindings:SOAP\" Location=\"http://localhost:8088/attr\" /><ns0:NameIDFormat>urn:oasis:names:tc:SAML:2.0:nameid-format:transient</ns0:NameIDFormat><ns0:NameIDFormat>urn:oasis:names:tc:SAML:2.0:nameid-format:persistent</ns0:NameIDFormat></ns0:AttributeAuthorityDescriptor><ns0:Organization><ns0:OrganizationName xml:lang=\"en\">Rolands Identiteter</ns0:OrganizationName><ns0:OrganizationDisplayName xml:lang=\"en\">Rolands Identiteter</ns0:OrganizationDisplayName><ns0:OrganizationURL xml:lang=\"en\">http://www.example.com</ns0:OrganizationURL></ns0:Organization><ns0:ContactPerson contactType=\"technical\"><ns0:GivenName>Roland</ns0:GivenName><ns0:SurName>Hedberg</ns0:SurName><ns0:EmailAddress>technical@example.com</ns0:EmailAddress></ns0:ContactPerson><ns0:ContactPerson contactType=\"support\"><ns0:GivenName>Support</ns0:GivenName><ns0:EmailAddress>support@example.com</ns0:EmailAddress></ns0:ContactPerson></ns0:EntityDescriptor>\n")


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

    def handleGetProviderConfig(self):
        if self.CONFIG_FILE_KEY in self.session:
            configString = self.session[self.CONFIG_FILE_KEY]
            try:
                configDict = json.loads(configString)
                providerConfig = {"provider": configDict['provider']}
                return self.returnJSON(json.dumps(providerConfig))
            except ValueError:
                return self.serviceError("No JSON object could be decoded. Please check if the file is a valid json file")
        return self.serviceError("No file saved in this current session")

    def handlePostProviderConfig(self):
        targetStringContent = self.session[self.CONFIG_FILE_KEY]
        targetDict = json.loads(targetStringContent)

        targetDict["provider"] = self.parameters['provider_config_summary']
        targetAsString = json.dumps(targetDict)

        self.session[self.CONFIG_FILE_KEY] = targetAsString

        print "Post basic config: " + self.session[self.CONFIG_FILE_KEY]
        return self.returnJSON({"asd": 1})


    def handleGetInteractionConfig(self):
        if self.CONFIG_FILE_KEY in self.session:
            configString = self.session[self.CONFIG_FILE_KEY]
            try:
                configDict = json.loads(configString)
                interactionConfigList = self.createInteractionConfigList(configDict)
                return self.returnJSON(json.dumps(interactionConfigList))
            except ValueError:
                return self.serviceError("No JSON object could be decoded. Please check if the file is a valid json file")
        return self.serviceError("No file saved in this current session")


    def handlePostInteractionConfig(self):
        interactionList = self.parameters['interactionList']
        interactionConfigList = []

        for entry in interactionList:
            interactionConfigList.append(entry['entry'])

        configString = self.session[self.CONFIG_FILE_KEY]
        configDict = json.loads(configString)

        configDict["interaction"] = interactionConfigList
        self.session[self.CONFIG_FILE_KEY] = json.dumps(configDict)

        print "Post interaction config: " + self.session[self.CONFIG_FILE_KEY]
        return self.returnJSON({"asd": 1})


    def addMetdataToSession(self, metadata):
        if (metadata.startswith('<?xml')):
            metadata = metadata.replace('\n', "")
            metadata = metadata.replace('\"', "\'")

            configString = self.session[self.CONFIG_FILE_KEY]
            configDict = ast.literal_eval(configString)

            configDict["metadata"] = ""

            newConfigString = json.dumps(configDict)
            newConfigString = newConfigString.replace("\"metadata\": \"\"", "\"metadata\": \"" + metadata + "\"")

            self.session[self.CONFIG_FILE_KEY] = newConfigString


    def handlePostMetadataFile(self):
        metadata = str(self.parameters['metadataFile'])

        self.addMetdataToSession(metadata)

        print "Post metadata file: " + self.session[self.CONFIG_FILE_KEY]
        return self.returnJSON({"asd": 1})


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


    def setDefaultValueInDict(self, key, dict, defaultValue):
        if key in dict:
            pass
        else:
            dict[key] = defaultValue
        return dict[key]

    def createInteractionConfigList(self, targetDict):
        if not('interaction' in targetDict):
            targetDict['interaction'] = []

        interactionList = targetDict['interaction']
        newInteractionList = []

        loopIndex = 0;
        for entry in interactionList:
            entry['control']['index'] = self.setDefaultValueInDict("index", entry['control'], 0)
            entry['control']['set'] = self.setDefaultValueInDict("set", entry['control'], {})

            entry = {"id": loopIndex,
                     "entry": entry
            }

            newInteractionList.append(entry)
            loopIndex += 1
        return newInteractionList


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


    def updateChildrensLevelFlat(self, child):
        childrenList = child['children']
        for unvisitedChild in childrenList:
            if (child['level'] + 1) > 2:
                unvisitedChild['level'] = 2;
            else:
                unvisitedChild['level'] = child['level'] + 1
            self.updateChildrensLevel(unvisitedChild)


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