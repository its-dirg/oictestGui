Overview
========

What is oictestGui?
-------------------

OictestGui is a web based interface used which in combination with the oictest tool will allow an independent
validation of a specific instance of a OpenID Connect entity.

Functionality test OP site:
---------------------------

* List all available tests supported by the oictest tool
* Tests will be presented in a tree layout, where the leaf nodes doesn't depend on any other test.
* Tests could be executed at three levels:
    * Run a single test,
    * Run test and sub-tests
    * Run all available tests
* Overview of the test result are presented by color coding and in text
* Detailed result view and a trace log
* Export result to to a text or Excel file
* Send error reports to the developers, the result will be attached to the report
* If no interaction information is available the application could sometimes collect the necessary data.

Functionality configurate OP site:
----------------------------------
* Create new configuration in the web browser
* Upload configuration file
* Download configuration file
* Add/remove interaction blocks, used to log on to an idp
* Edit other configuration details