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
            contentHeight: syncSettingsLabel.height + syncSettings.height + merge.height + importLabel.height + conboyImportButton.height + 100

            TitleLabel {
                id: syncSettingsLabel
                text: qsTr('Sync')
                anchors.left: parent.left
                anchors.leftMargin: 10
                anchors.right: parent.right
                anchors.rightMargin: 10
                anchors.topMargin: 20
                anchors.top: parent.top
            }
                
            Column {
                id: syncSettings
                spacing: 10
                anchors.left: parent.left
                anchors.leftMargin: 10
                anchors.right: parent.right
                anchors.rightMargin: 10
                anchors.top: syncSettingsLabel.bottom
                anchors.topMargin: 10
                
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
                    text:Settings.webdavBasePath
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

                Label {
                    id: remoteFolderLabel
                    text: qsTr("Remote Folder Name :")
                    anchors.left: parent.left
                    anchors.leftMargin: 10
                    anchors.right: parent.right
                    anchors.rightMargin: 10
                    horizontalAlignment: Text.AlignHCenter
                }

                TextField {
                     id: remoteFolder
                     text:Settings.remoteFolder
                     anchors.left: parent.left
                     anchors.leftMargin: 10
                     anchors.right: parent.right
                     anchors.rightMargin: 10
                     onTextChanged: {Settings.remoteFolder = remoteFolder.text; } 

                }
                }
            
            CheckBox {
                    id: merge
                    text: qsTr("Use auto merge feature")
                    anchors.topMargin: 20 
                    anchors.top: syncSettings.bottom
                    anchors.horizontalCenter: parent.horizontalCenter
                    checked: Settings.autoMerge
                    onClicked: {Settings.autoMerge = merge.checked;}
                     
                
            }
                
             TitleLabel {
                id: importLabel
                text: qsTr("<b>Import</b>")
                anchors.left: parent.left
                anchors.leftMargin: 10
                anchors.right: parent.right
                anchors.rightMargin: 10
                anchors.top: merge.bottom
                anchors.topMargin: 30
            }
            
                        
            Button {
                id: conboyImportButton
                width: 200; height: 50
                text: "Conboy / Tomboy"
                anchors.top: importLabel.bottom
                anchors.topMargin: 20
                anchors.left: parent.left
                anchors.leftMargin: 20
                anchors.right: busyindicatorImport.left
                anchors.rightMargin: 20
                onClicked: { Importer.launch(); }
            }
            
            BusyIndicator {
                id: busyindicatorImport
                platformStyle: BusyIndicatorStyle { size: "medium"; spinnerFrames: "image://theme/spinner"}
                running: Importer.running ? true : false;
                opacity: Importer.running ? 1.0 : 0.0;
                anchors.right: parent.right
                anchors.rightMargin: 20
                anchors.verticalCenter: conboyImportButton.verticalCenter
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
            MenuItem { text: qsTr("About"); onClicked: pushAbout()}
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


