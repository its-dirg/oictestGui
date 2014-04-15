Setup
#####

Here follows a guide on how to setup and configure the the test tool.

Configurate the server:
***********************

    1. Go to your oictestGui folder and open the server_conf.py
    2. If you want to use https you need certficates.
        * If you have access to production certificates you need to point them out. Point out all your certificates in the varaiables SERVER_CERT, SERVER_KEY and CERT_CHAIN.
        * If you do not have any production certificates you can generate self signed certificates by running the script [..]/httpsCert/create_key.sh. If you use this method the server_conf.py file need no changes.
        * To activate https you also need to set the variable HTTPS to True.
    3. You must take a look at all the settings in server_conf.py and adjust them for your needs.
    4. Set PORT to the port you want to use. If HTTPS is True, this is your https port.

Generate test tool metadata:
----------------------------

    #. Open the oictest folder
    #. Open [your path]/oictest/tests/oic_op
    There a list of configurations (.py) will be presented. In order to see an example of a configuration file read paragraph named **Configuration file structure**
    #. Copy one of the existing files, like localhost.py
    #. Edit the file. The most important infomation is:
        * BASE = the url too the test tool and port
        * Entityid
        * And the path to the Key and Certificate files
    #. Open a termanial
    #. Open [your path]/oictest/tests/oic_op
    #. Enter::

        make_metadata.py your_config_file.py > test_tool_metadata.xml

Configurate a simple test OP:
******************************

In order to do this you need the pyoidc application.

Configure the OP:

    #. Go to [your path]/pyoidc/oc3/
    #. Rename the file oc_config.py.example to oc_config.py
    #. Open the file oc_config.py
    #. Edit the necessary information, the most important information is the:
        * Baseurl which is the OP url


Configuration file structure
****************************

This is an example of how a configuration file structure ::

    {
       "interaction":[
          {
             "matches":{
                "url":"https://localhost:8092/authorization",
                "title":"Open id connect"
             },
             "control":{
                "set":{
                   "login":"diana",
                   "password":"krall"
                },
                "type":"form"
             },
             "page-type":"login"
          }
       ],
       "provider":{
          "dynamic":"https://localhost:8092/"
       },
       "client":{
          "redirect_uris":[
             "https://%s/authz_cb"
          ],
          "preferences":{
             "default_acr_values":[
                "2",
                "1",
                "PASSWORD"
             ],
             "subject_type":"public",
             "response_types":[
                "code",
                "token",
                "id_token",
                "token id_token",
                "code id_token",
                "code token",
                "code token id_token"
             ],
             "token_endpoint_auth_methods":[
                "client_secret_basic",
                "client_secret_post",
                "client_secret_jwt",
                "private_key_jwt"
             ],
             "default_max_age":3600,
             "request_object_signing_algs":[
                "RS256",
                "RS384",
                "RS512",
                "HS512",
                "HS384",
                "HS256"
             ],
             "id_token_signed_response_algs":[
                "RS256",
                "RS384",
                "RS512",
                "HS512",
                "HS384",
                "HS256"
             ],
             "grant_types":[
                "authorization_code",
                "implicit",
                "refresh_token",
                "urn:ietf:params:oauth:grant-type:jwt-bearer:"
             ],
             "require_auth_time":true,
             "userinfo_signed_response_algs":[
                "RS256",
                "RS384",
                "RS512",
                "HS512",
                "HS384",
                "HS256"
             ]
          },
          "contacts":[
             "roland.hedberg@adm.umu.se"
          ],
          "keys":{
             "RSA":{
                "use":[
                   "enc",
                   "sig"
                ],
                "key":"keys/pyoidc"
             }
          },
          "application_type":"web",
          "client_name":"OIC test tool",
          "client_id":"10TVL0SAM30000004901OIC10000000000000000",
          "client_secret":"46795C66-6DE3-F26C-7951-678E072AB3CA",
          "key_export_url":"http://%s:8090/"
       },
       "features":{
          "key_export":true,
          "discovery":true,
          "session_management":false,
          "registration":true
       },
       "versions":{
          "oauth":"2.0",
          "openid":"3.0"
       }
    }
