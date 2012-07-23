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

    ListView {
        id: notesView
        anchors.top: header.bottom
        anchors.bottom: parent.bottom
        height: parent.height - header.height
        width: parent.width
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
                             Note.load(model.uuid)
                             pageStack.push(fileEditPage, { modified: false});
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
        flickableItem: notesView
        z:3
        platformStyle: ScrollDecoratorStyle {
        }}

    onStatusChanged: {
         if (status == PageStatus.Active) {
              if (pageStack.currentPage.objectName == 'fileBrowserPage') {
                                        pageStack.currentPage.refresh();}
                                        
         }
    }

}
