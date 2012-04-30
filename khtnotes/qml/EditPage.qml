import QtQuick 1.1
import com.nokia.meego 1.0
import 'components'
import 'common.js' as Common

Page {
    tools: editTools
    id: editPage

    property string uuid;
    property bool modified;

    onUuidChanged: {
        if (uuid !== '') {
            console.log('onUuidChanged:'+uuid)
            Note.load(uuid)
            modified = false;
            flick.returnToBounds();
            }
    }

    function exitFile() {
        uuid = '';
        modified = false;
        pageStack.pop();
    }

    function saveFile() {
        if (textEditor.text!='') {
            Note.write(textEditor.text);        
            modified = false; }
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
                 text: Note.data
                 height: Math.max (implicitHeight, flick.height + 4, editPage.height, 720)
                 width:  flick.width + 4
                 wrapMode: TextEdit.WordWrap
                 inputMethodHints: Qt.ImhAutoUppercase | Qt.ImhPredictiveText;
                 textFormat: TextEdit.AutoText
                 font { bold: false; family: Settings.fontFamily; pixelSize: Settings.fontSize;}
                 onTextChanged: { modified = true;}
         }
         
         onOpacityChanged: {
           if (flick.opacity == 1.0) modified = false;
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
            MenuItem { text: qsTr("MarkDown Preview"); onClicked: pageStack.push(previewPage, {atext:textEditor.text}); }
//            MenuItem { text: qsTr("Save"); onClicked: saveFile()}
            /*MenuItem { text: qsTr("Preferences"); onClicked: notYetAvailableBanner.show(); }*/
        }
    }

    ToolBarLayout {
        id: editTools
        visible: true
        ToolIcon {
            platformIconId: "toolbar-back"
            anchors.left: (parent === undefined) ? undefined : parent.left
            onClicked: {
                   saveFile();
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


