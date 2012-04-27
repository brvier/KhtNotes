import QtQuick 1.1
import com.nokia.meego 1.0
//import '../common.js' as Common

Menu {
    id: itemMenu
    visualParent: pageStack

    property string filePath
    property string fileName
  
    MenuLayout {
        MenuItem {
            text: qsTr("Duplicate")
            onClicked: console.log('Duplicate not implemented yet');
        }
        MenuItem {
            text: qsTr("Delete")
            onClicked: {
              deleteQueryDialog.filepath = filePath;
              deleteQueryDialog.open();
            }
        }
    }
}
