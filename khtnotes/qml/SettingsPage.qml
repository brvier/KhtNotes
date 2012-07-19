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
                    id: hostLabel
                    text: qsTr("WebDav Host :")
                    anchors.left: parent.left
                    anchors.leftMargin: 10
                    anchors.right: parent.right
                    anchors.rightMargin: 10
                    horizontalAlignment: Text.AlignHCenter


                }

                TextField {
                     id: host
                     text:Settings.webdavHost
                     placeholderText: "https://khertan.net"
                     anchors.left: parent.left
                     anchors.leftMargin: 10
                     anchors.right: parent.right
                     anchors.rightMargin: 10
                     onTextChanged: {Settings.webdavHost = host.text;}

                }

                Label {
                    id: pathLabel
                    text: qsTr('Path :')
                    anchors.left: parent.left
                    anchors.leftMargin: 10
                    anchors.right: parent.right
                    anchors.rightMargin: 10
                    horizontalAlignment: Text.AlignHCenter
                 }

                 TextField {
                    id: path
                    text:Setting.webdavBasePath
                    placeholderText: '/owncloud/files/webdav.php'
                    anchors.left: parent.left
                    anchors.leftMargin: 10
                    anchors.right: parent.right
                    anchors.rightMargin: 10
                    onTextChanged: {Settings.webdavBasePath = path.text;}
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
                     text: Settings.webdavLogin
                     anchors.left: parent.left
                     anchors.leftMargin: 10
                     anchors.right: parent.right
                     anchors.rightMargin: 10
                     onTextChanged: {Settings.webdavLogin = login.text;}

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
                     text:Settings.webdavPasswd
                     anchors.left: parent.left
                     anchors.leftMargin: 10
                     anchors.right: parent.right
                     anchors.rightMargin: 10
                     onTextChanged: {if (password.text !== '') Settings.webdavPasswd = password.text; } // Test if non null due to nasty bug on qml echoMode

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


