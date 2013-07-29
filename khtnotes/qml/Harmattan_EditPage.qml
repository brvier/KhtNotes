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
                if ((! Sync.running) && (Settings.autoSync)) {Sync.launch()};
                return true;
            }
            else {return false;}
        }
        return true;
    }

    PageHeader {
        id: header
        title: 'KhtNotes'
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

        function ensureVisible(r)
        {
            if (contentX >= r.x)
                contentX = r.x;
            else if (contentX+width <= r.x+r.width)
                contentX = r.x+r.width-width;
            if (contentY >= r.y)
                contentY = r.y;
            else if (contentY+height <= r.y+r.height)
                contentY = r.y+r.height-height;
        }
        onContentYChanged: {
            if ((flick.contentY == 0) && (textEditor.cursorPosition != 0)) {
                flick.ensureVisible(
                            textEditor.positionToRectangle(textEditor.cursorPosition));
            }
        }

        TextArea {
            id: textEditor
            anchors.top: parent.top
            height: Math.max (implicitHeight, flick.height + 4, editPage.height, 720)
            width:  flick.width + 4
            wrapMode: TextEdit.WrapAnywhere
            inputMethodHints: Qt.ImhAutoUppercase | Qt.ImhNoPredictiveText
            textFormat: TextEdit.RichText
            font { bold: false;
                family: Settings.fontFamily;
                pixelSize:  Settings.fontSize;}
            onTextChanged: {
                if(focus){
                    modified = true;
                    autoTimer.restart();
                }
            }
            onActiveFocusChanged: {
		   console.log('ActiveFocus');
                   if ((textEditor.activeFocus) && (Settings.hideVkb) )
                       
			console.log('activeFocus and settings.hideVkb');
			textEditor.closeSoftwareInputPanel();
               }

           Connections {
            target: inputContext

            onSoftwareInputPanelVisibleChanged: {
                if ((activeFocus) && (Settings.hideVkb) )
                    textEditor.closeSoftwareInputPanel();
            }

            onSoftwareInputPanelRectChanged: {
                if ((activeFocus) && (Settings.hideVkb) )
                    textEditor.closeSoftwareInputPanel();
            }
        }

            Component.onDestruction: {
                console.log('On destruction called');
                if (modified == true) {
                    Note.write(textEditor.text);
                }
            }

            Timer {
                id: autoTimer
                interval: 2000
                onTriggered: {
                    if (modified) {
                        var curPos = textEditor.cursorPosition;
                        textEditor.text = Note.reHighlight(textEditor.text);
                        textEditor.cursorPosition = curPos;
                    }
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
            MenuItem { text: qsTr("MarkDown Preview"); 
                                    onClicked: pageStack.push(Qt.createComponent(Qt.resolvedUrl("Harmattan_PreviewPage.qml")), {html:Note.previewMarkdown(textEditor.text)}); }
            MenuItem { text: qsTr("ReStructuredText Preview"); onClicked: pageStack.push(Qt.createComponent(Qt.resolvedUrl("Harmattan_PreviewPage.qml")), {html:Note.previewReStructuredText(textEditor.text)}); }
            MenuItem { text: qsTr("Publish to Scriptogr.am"); 
                       visible: Settings.scriptogramUserId != '' ? true : false;
                       onClicked: {Note.publishToScriptogram(textEditor.text); }}
            MenuItem { text: qsTr("Publish as Post to KhtCms"); 
                       visible: Settings.khtcmsApiKey != '' ? true : false;
                       onClicked: {Note.publishAsPostToKhtCMS(textEditor.text); }}
            MenuItem { text: qsTr("Publish as Page to KhtCms"); 
                       visible: Settings.khtcmsApiKey != '' ? true : false;
                       onClicked: {Note.publishAsPageToKhtCMS(textEditor.text); }}
            MenuItem { text: qsTr("Share"); 
                       onClicked: {saveFile(); Note.exportWithShareUI(); }}
          
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