import QtQuick 1.1
import com.nokia.meego 1.0

    Rectangle {
        id:header

        property alias title: headerlabel.text

        anchors.top: parent.top
        width:parent.width
        height:70
        color:'#663366'
        z:2

        Text{
            id:headerlabel
            anchors.right: parent.right
            anchors.left: parent.left
            anchors.verticalCenter: parent.verticalCenter
            anchors.leftMargin: 10
            anchors.rightMargin: 10
            font { bold: false; family: "Nokia Pure Text"; pixelSize: 36; }
            color:"white"
            text:'KhtNotes'
        }
    }