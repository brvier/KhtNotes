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
        interactive: true
        anchors.top: header.bottom
        anchors.right: parent.right
        anchors.left: parent.left
        anchors.bottom: parent.bottom
        contentWidth: parent.width
        contentHeight: settingsColumn.height + 30
        clip: true

        Column {
            id: settingsColumn
            spacing: 10
            width: parent.width - 40
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.top: parent.top
            anchors.topMargin: 20
            
            TitleLabel {
                text: qsTr("Appearance")
            }

            Label {
                text: qsTr("Display Header")
                width: parent.width
                height: displayHeaderSwitch.height
                verticalAlignment: Text.AlignVCenter
                Switch {
                    id: displayHeaderSwitch
                    anchors.right: parent.right
                    checked: Settings.displayHeader
                    Binding {
                        target: Settings
                        property: "displayHeader"
                        value: displayHeaderSwitch.checked
                    }
                }
            }

            Label {
                text: qsTr("Font size")
                width: parent.width
                height: fontSlider.height
                verticalAlignment: Text.AlignVCenter
                Slider {
                    id: fontSlider
                    minimumValue: 9
                    maximumValue: 40
                    stepSize: 1
                    width: 300
                    valueIndicatorVisible: true
                    value: Settings.fontSize
                    anchors.right: fontSliderLabel.left
                    Binding {
                        target: Settings
                        property: "fontSize"
                        value: fontSlider.value
                    }
                }
                Label {
                    id: fontSliderLabel
                    text: fontSlider.value
                    width: 50
                    anchors.right: parent.right
                    anchors.verticalCenter: parent.verticalCenter
                }
            }
            
            TitleLabel {
                text: qsTr('Virtual Keyboard')
            }

            Label {
                width: parent.width
                height: hideVkbSwitch.height
                verticalAlignment: Text.AlignVCenter
                text: qsTr("Hide")

                Switch {
                    id: hideVkbSwitch
                    checked: Settings.hideVkb
                    anchors.right: parent.right
                    Binding {
                        target: Settings
                        property: "hideVkb"
                        value: hideVkbSwitch.checked
                    }
                }
            }
                        
            TitleLabel {
                text: qsTr('Webdav')
            }


            Label {
                text: qsTr("Host")
            }

            TextField {
                id: host
                text:Settings.webdavHost
                width: parent.width
                placeholderText: "https://khertan.net"
                Binding {
                    target: Settings
                    property: "webdavHost"
                    value: host.text
                }
            }

            Label {
                text: qsTr('Path')
            }

            TextField {
                id: path
                text:Settings.webdavBasePath
                width: parent.width
                placeholderText: '/owncloud/files/webdav.php'
                Binding {
                    target: Settings
                    property: "webdavBasePath"
                    value: path.text
                }
            }

            Label {
                text: qsTr("Login")
            }

            TextField {
                id: login
                text: Settings.webdavLogin
                width: parent.width
                Binding {
                    target: Settings
                    property: "webdavLogin"
                    value: login.text
                }

            }

            Label {
                text: qsTr("Password")
            }

            TextField {
                id: password
                echoMode: TextInput.PasswordEchoOnEdit
                text:Settings.webdavPasswd
                width: parent.width
                onTextChanged: {if (password.text !== '') Settings.webdavPasswd = password.text; } // Test if non null due to nasty bug on qml echoMode

            }

            Label {
                text: qsTr("Remote Folder Name")
            }

            TextField {
                id: remoteFolder
                text:Settings.remoteFolder
                width: parent.width
                Binding {
                    target: Settings
                    property: "remoteFolder"
                    value: remoteFolder.text
                }
            }

            TitleLabel {
                text: qsTr("Sync")
            }

            Label {
                width: parent.width
                height: mergeSwitch.height
                verticalAlignment: Text.AlignVCenter
                text: qsTr("Use auto merge feature")

                Switch {
                    id: mergeSwitch
                    checked: Settings.autoMerge
                    anchors.right: parent.right
                    Binding {
                        target: Settings
                        property: "autoMerge"
                        value: mergeSwitch.checked
                    }
                }
            }


            Label {
                width: parent.width
                height: autoSwitch.height
                verticalAlignment: Text.AlignVCenter
                text: qsTr("Use auto sync feature")

                Switch {
                    id: autoSwitch
                    checked: Settings.autoSync
                    anchors.right: parent.right
                    Binding {
                        target: Settings
                        property: "autoSync"
                        value: autoSwitch.checked
                    }
                }
            }

            TitleLabel {
                text: qsTr("<b>Import</b>")
            }
            

            Button {
                id: conboyImportButton
                width: 350; height: 50
                text: "Conboy / Tomboy"
                onClicked: { Importer.launch(); }
                

                BusyIndicator {
                    id: busyindicatorImport
                    platformStyle: BusyIndicatorStyle { size: "medium"; spinnerFrames: "image://theme/spinner"}
                    running: Importer.running ? true : false;
                    opacity: Importer.running ? 1.0 : 0.0;
                    anchors.right: parent.right
                    anchors.rightMargin: 20
                    //anchors.verticalCenter: conboyImportButton.verticalCenter
                }
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


