import QtQuick 1.1
import com.nokia.meego 1.0
import 'components'
import 'common.js' as Common

Page {
    tools: editTools
    id: editPage

    property bool modified;
    property alias text: textEditor.text;

    function exitFile() {
        modified = false;
        pageStack.pop();
    }

    function saveFile() {
        if ((modified == true)) {
            if (Note.write(textEditor.text)) {
                modified = false;
                fileBrowserPage.refresh();
                return true;
            }
            else {return false;}
        }
        return true;
    }

    PageHeader {
         id: header
         title: 'KhtNote'
    }

     BusyIndicator {
        id: busyindicator
        platformStyle: BusyIndicatorStyle { size: "large" }
        running: Note.ready ? false : true;
        opacity: Note.ready ? 0.0 : 1.0;
        anchors.centerIn: parent
    }

    Flickable {
         id: flick
         opacity: Note.ready ? 1.0 : 0.0
         flickableDirection: Flickable.HorizontalAndVerticalFlick
         anchors.top: header.bottom
         anchors.left: parent.left
         anchors.leftMargin: -2
         anchors.right: parent.right
         anchors.rightMargin: -2
         anchors.bottom: parent.bottom
         anchors.bottomMargin: -2
         anchors.topMargin: -2
         clip: true

         contentWidth: textEditor.width
         contentHeight: textEditor.height
         pressDelay: 200


             TextArea {
                 id: textEditor
                 anchors.top: parent.top
                 height: Math.max (implicitHeight, flick.height + 4, editPage.height, 720)
                 width:  flick.width + 4
                 wrapMode: TextEdit.WordWrap
                 inputMethodHints: Qt.ImhAutoUppercase | Qt.ImhNoPredictiveText
                 textFormat: TextEdit.StyledText
                 font { bold: false; 
                        family: Settings.fontFamily; 
                        pixelSize:  Settings.fontSize;}
                 onTextChanged: { modified = true; console.log('text changed')}
                 Component.onDestruction: {
                        if (modified == true) {
                            Note.write(textEditor.text);
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
            MenuItem { text: qsTr("MarkDown Preview"); onClicked: pageStack.push(Qt.createComponent(Qt.resolvedUrl("Harmattan_PreviewPage.qml")), {atext:textEditor.text}); }
        }
    }

    ToolBarLayout {
        id: editTools
        visible: true
        ToolIcon {
            platformIconId: "toolbar-back"
            anchors.left: (parent === undefined) ? undefined : parent.left
            onClicked: {
                   if (saveFile() == true)
                      exitFile();
                   }
        }

        ToolIcon {
            platformIconId: "toolbar-view-menu"
            anchors.right: (parent === undefined) ? undefined : parent.right
            onClicked: (editMenu.status === DialogStatus.Closed) ? editMenu.open() : editMenu.close()
        }
    }
}

