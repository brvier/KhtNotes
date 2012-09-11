import QtQuick 1.1
import com.nokia.meego 1.0
import Qt.labs.folderlistmodel 1.0
import 'components'
import 'common.js' as Common

Page {
    tools: mainTools

    function refresh() {        
         notesView.model.reload();
    }
    
    
    PageHeader {
         id: header
         title: 'KhtNotes'
    }
            
    TextField {
        id: search
        platformStyle: TextFieldStyle {
            backgroundSelected: "image://theme/color6-meegotouch-textedit-background-selected"
        }
        placeholderText: "Search"
        anchors { top: header.bottom; left: parent.left; right: parent.right }
        anchors.leftMargin: 16
        anchors.rightMargin: 16
        anchors.topMargin: 10
        inputMethodHints: Qt.ImhNoPredictiveText | Qt.ImhPreferLowercase | Qt.ImhNoAutoUppercase
        onTextChanged: notesModel.setFilterFixedString(text)

        Image {
            anchors { top: parent.top; right: parent.right; margins: 5 }
            smooth: true
            fillMode: Image.PreserveAspectFit
            source: search.text ? "image://theme/icon-m-input-clear" : "image://theme/icon-m-common-search"
            height: parent.height - platformStyle.paddingMedium * 2
            width: parent.height - platformStyle.paddingMedium * 2

            MouseArea {
                anchors.fill: parent
                anchors.margins: -10 // Make area bigger then image
                enabled: search.text
                onClicked: search.text = ""
            }
        }
    }
    
    ListView {
        id: notesView
        anchors.top: search.bottom
        anchors.topMargin: 10
        anchors.bottom: parent.bottom
        height: search.height - header.height
        width: parent.width
        clip: true
        z:1
        
        model: notesModel
        
        delegate: Component {
            id: fileDelegate
            Rectangle {
                width:parent.width
                height: 80
                anchors.leftMargin: 10
                color:"white"

                Rectangle {
                    id: background
                    anchors.fill: parent
                    color: "darkgray";
                    opacity: 0.0 
                    Behavior on opacity { NumberAnimation {} }
                }

                Column {
                    spacing: 10
                    anchors.leftMargin:10
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.verticalCenter: parent.verticalCenter
                    Label {text:'<b>'+model.title+'</b>'
                        font.family: "Nokia Pure Text"
                        font.pixelSize: 24
                        color:"black"
                        anchors.left: parent.left
                        anchors.right: parent.right
                    }

                    Label {
                        text: model.timestamp;
                        font.family: "Nokia Pure Text"
                        font.pixelSize: 16
                        color: "#cc6633"
                        anchors.left: parent.left;
                        anchors.right: parent.right
                        elide: Text.ElideRight
                        maximumLineCount: 1
                        }
                }


                MouseArea {
                    anchors.fill: parent
                    onPressed: background.opacity = 1.0;
                    onReleased: background.opacity = 0.0;
                    onPositionChanged: background.opacity = 0.0;

                    onClicked: {
                             Note.load(model.uuid);
                            
                             var editingPage = Qt.createComponent(Qt.resolvedUrl("Harmattan_EditPage.qml"));
                             //editingPage.textEditor.text = Note.data
                             //editingPage.setData()
                             pageStack.push(editingPage, {text: Note.data,
                                                          modified: false});
                    //    }
                    }
                    onPressAndHold: {
                        itemMenu.uuid = model.uuid;
                        itemMenu.open();
                   }
                }
            }
        }
    }        

    ScrollDecorator {
        id: scrollDecorator
        flickableItem: notesView
        z:3
        platformStyle: ScrollDecoratorStyle {
        }}

}
