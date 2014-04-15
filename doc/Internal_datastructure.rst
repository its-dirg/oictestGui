Internal datastructure
**********************

Internal datastructure used by the application to build the configuration site.

The data written in uppercase letters has been described in separate structures::

    {
       "fetchInfoFromServerDropDown":{
          "name":"How does the application fetch information from the server?",
          "value":"",
          "values":[
             {
                "type":"dynamic",
                "name":"dynmic"
             },
             {
                "type":"static",
                "name":"static"
             }
          ]
       },
       "fetchStaticInfoFromServer":{
          "showInputFields":False,
          "inputFields": STATIC_INPUT_FIELD_LIST
       },
       "fetchDynamicInfoFromServer":{
          "showInputField":False,
          "inputField":{
             "label":"dynamic",
             "value":"",
             "show":False,
             "isList":False
          }
       },
       "requiredInfoDropDown":{
          "label":"Do your application support dynamic client registration?",
          "value":"",
          "values":[
             {
                "type":"yes",
                "name":"yes"
             },
             {
                "type":"no",
                "name":"no"
             }
          ]
       },
       "requiredInfoTextFields":[
          {
             "id":"client_id",
             "label":"Client id",
             "textFieldContent":""
          },
          {
             "id":"client_secret",
             "label":"Client secret",
             "textFieldContent":""
          }
       ],
       "interactionsBlocks": LIST_OF_INTERACTION_BLOCKS
    }


STATIC_INPUT_FIELD_LIST
***********************
::

    [
       {
          "id":"input field id",
          "label":"input field label",
          "values":[
             {
                "index":0,
                "textFieldContent":"First list element"
             },
             {
                "index":1,
                "textFieldContent":"Second list element"
             }
          ],
          "show":True,
          "isList":True
       },
       {
          "id":"input field id",
          "label":"input field label",
          "values":[
             {
                "index":0,
                "textFieldContent":"Only element"
             }
          ],
          "show":True,
          "isList":False
       }
    ]

LIST_OF_INTERACTION_BLOCKS
**************************
::

    [
       {
          "id":numberOfBlocks,
          "inputFields":[
             {
                "label":"title",
                "textFieldContent":"title content"
             },
             {
                "label":"url",
                "textFieldContent": "url content"
             },
             {
                "label":"pageType",
                "textFieldContent": "page-type content"
             },
             {
                "label":"index",
                "textFieldContent": "index content"
             },
             {
                "label":"set",
                "textFieldContent": "set content"
             },
             {
                "label":"type",
                "textFieldContent": "type content"
             }
          ]
       }
    ]
