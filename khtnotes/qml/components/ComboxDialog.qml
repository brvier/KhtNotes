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

    content:Item {
        id: name
        width: parent.width
        height: 450

        Column {
            anchors.fill: parent
            spacing: 10

            TextField {
                id: textfield
            }

            ListView {
                id: view
                height: 250
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
    }

    buttons: ButtonRow {
        style: ButtonStyle { }
        anchors.horizontalCenter: parent.horizontalCenter
        Button {text: "OK"; onClicked: root.accept()}
    }
}
