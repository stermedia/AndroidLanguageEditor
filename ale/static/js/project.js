/**
 * Created by johniak on 6/4/14.
 */
$(function () {
    editableGrid = new EditableGrid("LangGrid");
    editableGrid.tableLoaded = function () {
        this.renderGrid("tablecontent", "testgrid");
    };
    editableGrid.loadJSON("/json/project/" + project_path + "/");
    editableGrid.modelChanged = function (rowIndex, columnIndex, oldValue, newValue) {
        console.log(editableGrid.getRowValues(rowIndex).key + " " + editableGrid.getColumnName(columnIndex) + " " + newValue)
        postModifiedCell(editableGrid.getRowValues(rowIndex).key, newValue, editableGrid.getColumnName(columnIndex))
    }
    $("#share_modal_menu").click(function () {
        refreshSharesTable();
    });
    $("#add-share").click(function () {
        $.post("/json/share/project/" + project_path + "/", { csrfmiddlewaretoken: getCookie('csrftoken') })
            .done(function (data) {
                console.log("Data Loaded: " + data);
                refreshSharesTable();
            });
    });
});

function postModifiedCell(key, value, lang) {
    $.post("/json/project/" + project_path + "/cell/modify/", { key: key, value: value, lang: lang, csrfmiddlewaretoken: getCookie('csrftoken') })
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
        $.post("/json/project/" + project_path + "/cell/modify/", $('#add-row-cell').serialize(), function (data) {
            console.log(data);
            $('#add-row-modal').modal('hide')
            editableGrid.loadJSON("/json/project/" + project_path + "/");
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

function refreshSharesTable() {
    $.get("/json/shares/project/" + project_path + "/", function (data) {
        var table_body = $("#shares-table");
        table_body.html("");
        for (var i = 0; i < data.length; i++) {
            var item = data[i]
            var $tr = $('<tr>').append(
                $('<td>').text(i + 1),
                $('<td>').html($('<a>').text(item.hash).attr("href", "/share/" + item.hash + "/")),
                $('<td>').html($('<button>').attr('data-id', item.hash).attr('class', 'btn-xs btn btn-danger center-ver center-hor remove-share').html($('<i>').attr('class', "glyphicon glyphicon-remove")))
            );
            table_body.append($tr)
        }
        $('.remove-share').click(function () {
            $.post("/json/share/remove/project/" + project_path + "/", { hash: $(this).attr('data-id'), csrfmiddlewaretoken: getCookie('csrftoken') })
                .done(function (data) {
                    console.log("Data Loaded: " + data);
                    refreshSharesTable();
                });
        });
    });
}