import QtQuick 1.1
import com.nokia.meego 1.0

    Rectangle {
        id:header

        property alias title: headerlabel.text

        anchors.top: parent.top
        width:parent.width
        height:Settings.displayHeader ? 70 : 0
        color:'#663366'
        z:2
        visible: Settings.displayHeader ? 1.0 : 0.0
        opacity: visible
        
        Text{
            id:headerlabel
            anchors.right: busyindicatorsmall.left
            anchors.left: parent.left
            anchors.verticalCenter: parent.verticalCenter
            anchors.leftMargin: 10
            anchors.rightMargin: 10
            font { bold: false; family: "Nokia Pure Text"; pixelSize: 36; }
            color:"white"
            text:'KhtNotes'
            
        }
        
         BusyIndicator {
                 id: busyindicatorsmall
                 platformStyle: BusyIndicatorStyle { size: "medium"; spinnerFrames: "image://theme/spinnerinverted"}
                 running: Sync.running ? true : false;
                 opacity: Sync.running ? 1.0 : 0.0;
                 anchors.right: header.right
                 anchors.rightMargin: 10                                                 
                 anchors.verticalCenter: header.verticalCenter
                 /*onOpacityChanged:{
                    if ((opacity === 0.0) && (pageStack)) {
                        if (pageStack.currentPage.objectName === 'fileBrowserPage') {
                            pageStack.currentPage.refresh();
                        }
                    }
                 }   */                                            
     
         }
    }
