//当学校切换时会请求该学校的所有学院
$('#school').on('change', function () {
    let school = $('#school').val();
    //请求获取学院
    $.ajax({
        url: '/get_institutions/' + school,
        type: 'GET',
        dataType: 'json'
    }).done(function (institutions) {
        //先删除之前的选项
        $('#institution option').remove();
        // 进行数值的填充
        let $institution = $('#institution');
        for (let index = 0; index < institutions.length; index++){
            let institution = institutions[index];
            $institution.append(`<option value="${institution.name}">${institution.name}</option>`)
        }
    });
});

/**
 * 添加参与人员
 * @param value 默认的值
 */
function addDomain(value="") {
    //在添加按钮前添加新的<span> 标签
    //获取学校学院和人名
    let school = $('#school').val();
    let institution = $('#institution').val();
    let person = $('#person').val();

    if (person.length == 0){
        toggle_alert(false, "", "请输入名字");
        return;
    }
    //检查该老师是否存在
    else{

    }
    let $target = null;
    if ($('#leader').children().length == 0){
        $target = $('#leader');
    }else
    {
        $target = $('#people');
    }

    $target.append(`
        <span>
            <span class="member">${person}</span>
            <i class="mdui-icon material-icons" style="cursor: pointer" onclick="removeTheDomain($(this));">&#xe14c;</i>
        </span>`);
    //让最新产生的输入获得焦点
}
//移除指定的领域
function removeTheDomain($target) {
    $target.parent().remove();
}
