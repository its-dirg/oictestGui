## index.html
<%inherit file="base.mako"/>

<%block name="script">
    <!-- Add more script imports here! -->
</%block>

<%block name="css">
    <!-- Add more css imports here! -->
</%block>

<%block name="title">
    oictest application
</%block>

<%block name="header">
    ${parent.header()}
</%block>

<%block name="headline">
    <div menu></div>

    <div ng-controller="IndexCtrl">
</%block>


<%block name="body">

    <h2>About the service</h2>
    <span style="font-size:17px">
        Oictest is a test tool developed by DIRG. It allows the user an independent validation of a specific instance of a OpenID connect entity.
        It will test if the instance works according to the OpenID connect standard. In order to start testing your
        OpenID provider visit <a href="https://dirg.org.umu.se/page/OictestService" target="_blank">www.dirg.org.umu.se</a>
     </span>

</%block>

<%block name="footer">
    </div>

    <script type="text/javascript" src="/static/home.js"></script>
    ${parent.footer()}
</%block>