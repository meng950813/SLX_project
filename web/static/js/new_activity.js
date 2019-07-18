
function addNewRow(target) {
    // 添加参数项
    let insert_content = `
        <div class="form-row">
            <div class="col-md-12 form-group">
                <input type="text" id="partner1" placeholder="合作人">
                <input type="text" id="partner2" placeholder="合作人">
                <input type="file" id="agreement">
                <i class="mdui-icon material-icons" onclick="addNewRow($(this));">&#xe148;</i>
                <i class="mdui-icon material-icons" onclick="removeRow($(this));">&#xe15d;</i>
            </div>
        </div>`;
    target.parent().parent().after(insert_content);
}

function removeRow(target) {
    target.parent().parent().remove();
}