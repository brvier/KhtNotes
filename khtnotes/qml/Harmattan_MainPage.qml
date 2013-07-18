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
        id: pageHeader
        title: 'KhtNotes'
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

    SearchField {
            id: searchField
            onTextChanged: notesModel.setFilterFixedString(text)
            anchors {
                top: pageHeader.bottom
                left: parent.left
                right: parent.right
            }
        }
    
    ListView {
        id: notesView
        anchors.top: searchField.bottom
        anchors.bottom: parent.bottom
        height: pageHeader.height
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
                    Label {text: model.title
                        font.family: "Nokia Pure Text"
                        font.pixelSize: 24
                        font.weight: Font.Bold
                        color:"black"
                        anchors.left: parent.left
                        anchors.right: parent.right
                        elide: Text.ElideRight
                        maximumLineCount: 1
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

    SectionScroller {
            id:sectionScroller
            listView: notesView
            z:4
        }
        
    ScrollDecorator {
        id: scrollDecorator
        flickableItem: notesView
        z:3
        platformStyle: ScrollDecoratorStyle {
        }
    }

} 