import QtQuick 1.1
import com.nokia.meego 1.0

Menu {
    id: itemMenu
    visualParent: pageStack

    property string uuid
    property int index

    MenuLayout {
        MenuItem {
            text: qsTr("Favorite")
            onClicked: {
                notesModel.favorite(index)
            }
        }
        MenuItem {
            text: qsTr("Category")
            onClicked: {
                var categories = notesModel.getCategories().split("\n");
                console.log(categories)
                var idx = 0;
                categoryQueryDialog.model.clear();
                for (;idx < categories.length; idx++) {
                    categoryQueryDialog.model.append({"name":categories[idx]});
                }
                categoryQueryDialog.index = index;
                categoryQueryDialog.open();
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
