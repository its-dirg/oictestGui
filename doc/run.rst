Run
####

The explains how to run the test server

Go to your oictestGui folder and open a terminal enter::

    python server.py server_conf

Create oictest configuration for an OP:
******************************************

In order to run tests you have to create or upload an oictest configuration for an OP. To do this you need to start the server.

#. Open a web browser go to:
#. https://[server url]:[server port]
#. Click on the tab called "Configure OP"
#. Click on "Create configurations"
#. Enter entity_id
#. You shouldn't need to change the name_format
#. Remove the generated interaction-block, in some cases the application can gather this information by itself.



Start simple test OP:
**********************

Insert info/link for how to start a simple OP

Run test:

Now you should be able to run tests.

#. Go to the page named "Test OP"
#. Run one or multiple tests
#. If you didn't add any interaction-blocks the application will most likely ask whether to gather the information by itself or not. Note that while gathering infomation you need to run the test multpile time until all the infomation has been gathered.
