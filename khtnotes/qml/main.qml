import QtQuick 1.1
import com.nokia.meego 1.0
import com.nokia.extras 1.1
import 'components'
import 'common.js' as Common

PageStackWindow {
    id: appWindow

    initialPage: fileBrowserPage

    MainPage {
        id: fileBrowserPage
        objectName: 'fileBrowserPage'
    }


    EditPage {
        id: fileEditPage
    }

    PreviewPage {
        id: previewPage
    }

    SettingsPage {
        id: settingsPage
    }

    ItemMenu {
        id: itemMenu
    }

    ToolBarLayout {
        id: mainTools
        visible: true

        ToolIcon {
            platformIconId: "toolbar-add" 
  //          anchors.left: (parent === undefined) ? undefined : parent.left 
            onClicked: pageStack.push(fileEditPage, {uuid:'new'});
        }

        ToolIcon {
                    platformIconId: Sync.running ? 'toolbar-mediacontrol-stop' : 'toolbar-refresh';
                        //        anchors.right: (parent === undefined) ? undefined : parent.right
                                    onClicked: Sync.launch();
                                            }
                                            
        ToolIcon {
            platformIconId: "toolbar-view-menu"
    //        anchors.right: (parent === undefined) ? undefined : parent.right
            onClicked: (myMenu.status === DialogStatus.Closed) ? myMenu.open() : myMenu.close()
        }
    }


    ToolBarLayout {
        id: commonTools
        visible: false
        ToolIcon {
            platformIconId: "toolbar-back"
            anchors.left: (parent === undefined) ? undefined : parent.left
            onClicked: pageStack.pop();
        }

        ToolIcon {
            platformIconId: "toolbar-view-menu"
            anchors.right: (parent === undefined) ? undefined : parent.right
            onClicked: (myMenu.status === DialogStatus.Closed) ? myMenu.open() : myMenu.close()
        }
    }


    Menu {
        id: myMenu
        visualParent: pageStack
        MenuLayout {
            MenuItem { text: qsTr("About"); onClicked: about.open()}
            MenuItem { text: qsTr("Preferences"); onClicked: pageStack.push(settingsPage); }
        }
    }

    InfoBanner{
                      id:notYetAvailableBanner
                      text: 'This feature is not yet available'
                      timerShowTime: 5000
                      timerEnabled:true
                      anchors.top: parent.top
                      anchors.topMargin: 60
                      anchors.horizontalCenter: parent.horizontalCenter
                 }

    InfoBanner{
                      id:errorBanner
                      text: 'An error occur while creating new folder'
                      timerShowTime: 15000
                      timerEnabled:true
                      anchors.top: parent.top
                      anchors.topMargin: 60
                      anchors.horizontalCenter: parent.horizontalCenter
                 }

    function onError(errMsg) {
        errorEditBanner.text = errMsg;
        errorEditBanner.show();
    }

    InfoBanner{
                      id:errorEditBanner
                      text: ''
                      timerShowTime: 15000
                      timerEnabled:true
                      anchors.top: parent.top
                      anchors.topMargin: 60
                      anchors.horizontalCenter: parent.horizontalCenter
                 }

   showStatusBar: true

    QueryDialog {
        property string uuid
        id: deleteQueryDialog
        icon: Qt.resolvedUrl('../icons/khtsimpletext.png')
        titleText: "Delete"
        message: "Are you sure you want to delete this note ?"
        acceptButtonText: qsTr("Delete")
        rejectButtonText: qsTr("Cancel")
        onAccepted: {
                if (!(Note(uuid).rm())) {
                    errorBanner.text = 'An error occur while deleting item';
                    errorBanner.show();
                }
                else {fileBrowserPage.refresh();}
        }
    }

    // About Dialog
    QueryDialog {
                id: about
                icon: Qt.resolvedUrl('../icons/khtnotes.png')
                titleText: 'About KhtNotes'
                message: 'Version ' + __version__ +
                         '\nBy Benoît HERVIER (Khertan)\n' +
                         '\nA note taking application with sync' +
                         '\nfor MeeGo and Harmattan.\n' +
                         'Licenced under GPLv3\n' +
                         'Web Site : http://khertan.net/khtnotes'
                }

    //State used to detect when we should refresh view
    states: [
            State {
                        name: "fullsize-visible"
                        when: platformWindow.viewMode === WindowState.Fullsize && platformWindow.visible
                        StateChangeScript {
                                 script: {
                                 console.log('objectName:'+pageStack.currentPage.objectName);
                                 if (pageStack.currentPage.objectName === 'fileBrowserPage') {
                                 	pageStack.currentPage.refresh();}
                                 }       }
                  }
            ]
}
