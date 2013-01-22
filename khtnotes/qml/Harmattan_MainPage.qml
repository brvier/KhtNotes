import QtQuick 1.1
import com.nokia.meego 1.0
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

    SearchField {
        id: search
        anchors { top: header.bottom; left: parent.left; right: parent.right }
        anchors.leftMargin: 16
        anchors.rightMargin: 16
        anchors.topMargin: 10
        onTextChanged: notesModel.setFilterFixedString(text)
    }
    
    Component {
        id: notesCategory
        Rectangle {
            width: notesView.width
            height: 40
            color: "#555"

            Label {
                text: section
                font.bold: true
                font.family: "Nokia Pure Text"
                font.pixelSize: 18
                color: "white"
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                anchors.fill: parent
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
                

                Image {
                    anchors.right: parent.right
                    anchors.rightMargin: 10
                    anchors.verticalCenter: parent.verticalCenter
                    source: "image://theme/icon-m-toolbar-favorite-mark"
                    visible: favorited
                    opacity: favorited ? 1.0 : 0.0
                }

                MouseArea {
                    anchors.fill: parent
                    onPressed: background.opacity = 1.0;
                    onReleased: background.opacity = 0.0;
                    onPositionChanged: background.opacity = 0.0;

                    onClicked: {
                        Note.load(model.uuid);

                        var editingPage = Qt.createComponent(Qt.resolvedUrl("Harmattan_EditPage.qml"));
                        pageStack.push(editingPage, {text: Note.data,
                                           modified: false});
                    }
                    onPressAndHold: {
                        //itemMenu.uuid = model.uuid;
                        itemMenu.index = model.index;
                        itemMenu.open();
                    }
                }
            }
        }

        section.property: "category"
        section.criteria: ViewSection.FullString
        section.delegate: notesCategory
    }

    ScrollDecorator {
        id: scrollDecorator
        flickableItem: notesView
        z:3
        platformStyle: ScrollDecoratorStyle {
        }}

}
