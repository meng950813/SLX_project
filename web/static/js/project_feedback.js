//当学校切换时会请求该学校的所有学院
$('#school').on('change', function () {
    let school = $('#school').val();
    //请求获取学院
    $.ajax({
        url: '/scholar/get_institutions/' + school,
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
 * 添加Span 会先判断该老师是否存在
 */
function addSpan() {
    //在添加按钮前添加新的<span> 标签
    let personName = $('#person-name').val();

    if (personName.length == 0){
        toggle_alert(false, "", "请输入名字");
        return;
    }
    //检查该老师是否存在
    else{
        $.ajax({
            url: '/scholar/get_teachers/' + personName,
            type: 'GET',
            dataType: 'json',
            data: {'is_json': true},
        }).done(addSpanCallback);
    }
}

function addSpanCallback(teachers) {
    //获取学校学院和人名
    let school = $('#school').val();
    let institution = $('#institution').val();
    let personName = $('#person-name').val();

    if (teachers == null || teachers.length == 0){
        toggle_alert(false, "", "未找到该老师，请先添加该老师");
        return;
    }
    //默认获取第一个老师的id
    let teacherID = teachers[0].id;
    //优先输入领导者
    let $target = null;
    if ($('#leader').children().length == 0){
        $target = $('#leader');
    }else
    {
        $target = $('#other');
    }

    $target.append(`
        <span>
            <span class="member" data-school="${school}" data-institution="${institution}" data-id="${teacherID}">${personName}</span>
            <i class="mdui-icon material-icons" style="cursor: pointer" onclick="removeTheSpan($(this));">&#xe14c;</i>
        </span>`);
}

//移除指定的span
function removeTheSpan($target) {
    $target.parent().remove();
}

/**
 * 提交form表单，在提交之前会组合所有的class="domain"的span的值，然后使用;拼接
 * 赋值给#domain中，之后发给后端
 */
function submitData() {
    //获取class="member"的所有成员
    let $members = $('.member');
    let data = [];
    for (let i = 0; i < $members.length; i++){
        let member = $members[i];
        let datum = {
            'school': member.getAttribute('data-school'),
            'institution': member.getAttribute('data-institution'),
            'id': member.getAttribute('data-id'),
            'name': member.innerText,
        };
        data.push(datum);
    }
    //把值添加到隐藏字段members中
    $('#members').val(JSON.stringify(data));

    //提交表单
    document.getElementById('project-form').submit();
}

