import QtQuick 1.1
import com.nokia.meego 1.0
//import '../common.js' as Common

Menu {
    id: itemMenu
    visualParent: pageStack

    property string uuid
    property int index

    MenuLayout {
        MenuItem {
            text: qsTr("Favorite")
            onClicked: {
                //Note.favorite(uuid);
                
            notesModel.favorite(index)
            }   
        }
        MenuItem {
            text: qsTr("Duplicate")
            onClicked: notesModel.duplicate(index);
        }
        MenuItem {
            text: qsTr("Delete")
            onClicked: {
              deleteQueryDialog.index = index;
              deleteQueryDialog.open();
            }
        }
    }
}
