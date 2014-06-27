/**
 * Created by johniak on 6/4/14.
 */
$(function () {
    editableGrid = new EditableGrid("LangGrid");
    editableGrid.tableLoaded = function () {
        this.renderGrid("tablecontent", "testgrid");
    };
    editableGrid.loadJSON("/json/share/cells/" + hash_key + "/");
    editableGrid.modelChanged = function (rowIndex, columnIndex, oldValue, newValue) {
        console.log(editableGrid.getRowValues(rowIndex).key + " " + editableGrid.getColumnName(columnIndex) + " " + newValue)
        postModifiedCell(editableGrid.getRowValues(rowIndex).key, newValue, editableGrid.getColumnName(columnIndex))
    }
});

function postModifiedCell(key, value, lang) {
    $.post("/json/share/modify/cell/" + hash_key + "/", { key: key, value: value, lang: lang, csrfmiddlewaretoken: getCookie('csrftoken') })
        .done(function (data) {
            console.log("Data Loaded: " + data);
        });
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

$(function () {
    $("#add-row-submit").click(function () {
        $.post("/json/share/modify/cell/" + hash_key + "/",$('#add-row-cell').serialize(), function (data) {
            console.log(data);
            $('#add-row-modal').modal('hide')
            editableGrid.loadJSON("/json/share/cells/" + hash_key + "/");
            var id = "#LangGrid_" + $('#add-row-cell input[name="key"]').val();
            editableGrid.tableLoaded = function () {
                this.renderGrid("tablecontent", "testgrid");
                console.log("loaded" + id);
                $.scrollTo(id, {offset: {left: 0, top: -51 }});
                console.log("loaded");
                $(id).css("background-color", "#00ff00");
                $(id).animate({
                    backgroundColor: "#ffffff"
                }, 1000);
            };
            $('#add-row-cell input[name="key"]').val("");
            $('#add-row-cell textarea[name="value"]').val("");
        })
    });
});

