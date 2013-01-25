import QtQuick 1.1
import com.nokia.meego 1.0

Dialog {
    property alias placeholder: textfield.placeholderText
    property alias text: textfield.text
    property alias titleText: titleField.text
    property alias model: view.model

    id: root
    title: Label {
        id: titleField
        width: parent.width
        color: "white"
        text: 'Title'
        height: 50
    }

    content:  //Item {
//        id: name
//        width: parent.width
//        height: root.height - 70
       //anchors.fill: parent
       //anchors.bottom: 

        Rectangle {
            //anchors.fill: parent
            //height: parent.height
            //spacing: 10
            //height: root.height - 70
            height: 250

            TextField {
                id: textfield
                width: parent.width
                anchors.top: parent.top
            }

            ListView {
                id: view
                height: parent.height - textfield.height - 10
                //height: parent.height
                anchors.bottom: parent.bottom
                width: parent.width
                clip: true

                model: ListModel {

                }

                delegate: Component{
                    id: listViewDelegate
                    Label {
                        text: model.name
                        color: 'white'
                        width:parent.width
                        height: 50
                        MouseArea {
                            anchors.fill: parent
                            onClicked: {
                                textfield.text = model.name;
                            }
                        }
                    }
                }
            }
        }
//    }

    buttons: ButtonRow {
        style: ButtonStyle { }
        anchors.horizontalCenter: parent.horizontalCenter
        Button {text: "OK"; onClicked: root.accept()}
    }
}
