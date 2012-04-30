import QtQuick 1.1
import com.nokia.meego 1.0
import 'components'
import 'common.js' as Common

Page {
    tools: simpleBackTools
    id: previewPage

    property string atext;

    signal refresh();
    
    onRefresh: {
               }                            
    
    function exitFile() {    
        pageStack.pop();
    }

    /*function previewText() {    
        textEditor.text = Document.previewMarkdown(text);
    }*/
        
        PageHeader {
         id: header
         title: 'KhtNotes'
    }


    Flickable {
         id: flick
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
                 height: Math.max (850, implicitHeight)
                 width: Math.max(flick.width, implicitWidth) //previewPage.width + 4
                 wrapMode: TextEdit.NoWrap
                 textFormat: TextEdit.RichText
                 text: Note.previewMarkdown(atext)
                 font { bold: false; family: "Nokia Pure Text"; pixelSize: 18;}
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


