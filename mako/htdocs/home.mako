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

    <h2>Home page</h2>
    <span style="font-size:17px">
        Intersting text about oictest
    </span>

</%block>

<%block name="footer">
    </div>

    <script type="text/javascript" src="/static/home.js"></script>
    ${parent.footer()}
</%block>