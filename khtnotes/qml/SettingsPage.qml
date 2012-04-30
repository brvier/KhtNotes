import QtQuick 1.1
import com.nokia.meego 1.0
import 'components'
import 'common.js' as Common

Page {
    tools: simpleBackTools
    id: settingsPage

    signal refresh();

    onRefresh: {
               }

    function exitFile() {
        pageStack.pop();
    }

    PageHeader {
         id: header
         title: 'KhtNotes'
    }


    Flickable {
            id: flick
            anchors.top: header.bottom
            anchors.bottom: parent.bottom
            anchors.left: parent.left
            anchors.right: parent.right
            
            contentWidth: parent.width
            contentHeight: prefs.height + 60

            Column {
                id: prefs
                spacing: 10
                anchors.left: parent.left
                anchors.leftMargin: 10
                anchors.right: parent.right
                anchors.rightMargin: 10

                Label {
                    id: syncServerUrlLabel
                    text: qsTr("Sync server URL :")
                    anchors.left: parent.left
                    anchors.leftMargin: 10
                    anchors.right: parent.right
                    anchors.rightMargin: 10
                    horizontalAlignment: Text.AlignHCenter


                }

                TextField {
                     id: syncServerUrl
                     text:Settings.syncUrl
                     placeholderText: "https://khertan.net/khtnotes/sync.php"
                     anchors.left: parent.left
                     anchors.leftMargin: 10
                     anchors.right: parent.right
                     anchors.rightMargin: 10
                     onTextChanged: {Settings.syncUrl = syncServerUrl.text;}

                }

                Label {
                    id: loginLabel
                    text: qsTr("Login :")
                    anchors.left: parent.left
                    anchors.leftMargin: 10
                    anchors.right: parent.right
                    anchors.rightMargin: 10
                    horizontalAlignment: Text.AlignHCenter
                }

                TextField {
                     id: login
                     text: Settings.syncLogin
                     anchors.left: parent.left
                     anchors.leftMargin: 10
                     anchors.right: parent.right
                     anchors.rightMargin: 10
                     onTextChanged: {Settings.syncLogin = login.text;}

                }

                Label {
                    id: passwordLabel
                    text: qsTr("Password :")
                    anchors.left: parent.left
                    anchors.leftMargin: 10
                    anchors.right: parent.right
                    anchors.rightMargin: 10
                    horizontalAlignment: Text.AlignHCenter

                }

                TextField {
                     id: password
                     echoMode: TextInput.PasswordEchoOnEdit
                     text:Settings.syncPassword
                     anchors.left: parent.left
                     anchors.leftMargin: 10
                     anchors.right: parent.right
                     anchors.rightMargin: 10
                     onTextChanged: {if (password.text !== '') Settings.syncPassword = password.text; } // Test if non null due to nasty bug on qml echoMode

                }
            }
        }


    ScrollDecorator {
        flickableItem: flick
        platformStyle: ScrollDecoratorStyle {
        }}

    Menu {
        id: editMenu
        visualParent: pageStack
        MenuLayout {
            MenuItem { text: qsTr("About"); onClicked: about.open()}
         }
    }

    ToolBarLayout {
        id: simpleBackTools
        visible: true
        ToolIcon {
            platformIconId: "toolbar-back"
            anchors.left: (parent === undefined) ? undefined : parent.left
            onClicked: {
                    pageStack.pop();
                   }
        }

        ToolIcon {
            platformIconId: "toolbar-view-menu"
            anchors.right: (parent === undefined) ? undefined : parent.right
            onClicked: (editMenu.status === DialogStatus.Closed) ? editMenu.open() : editMenu.close()
        }
    }
}


