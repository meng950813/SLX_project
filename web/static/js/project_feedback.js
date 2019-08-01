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
    //老师对应的ID
    let teacherID = null;
    for (let i = 0; i < teachers.length; i++){
        let teacher = teachers[i];
        if (teacher.school == school && teacher.institution == institution){
            teacherID = teacher.id;
            break;
        }
    }
    if (teacherID == null){
        toggle_alert(false, "", "未找到该老师，请先添加该老师");
        return;
    }
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
 * 检测一些输入是否合法
 * 比如起止时间，和必须有负责人
 * @returns {boolean}
 */
function checkValid() {
    //名称
    if ($('#name').val().length == 0){
        toggle_alert(false, "", "请输入项目名称");
        return false;
    }
    if ($('#fund').val().length == 0){
        toggle_alert(false, "", "请输入项目资金");
        return false;
    }
    //获取起止时间
    if ($('#start_time').val().length == 0){
        toggle_alert(false, "", "请输入开始时间");
        return false;
    }
    if ($('#end_time').val().length == 0){
        toggle_alert(false, "", "请输入截至时间");
        return false;
    }
    //保证开始时间小于截至日期
    let start_time = new Date($('#start_time').val());
    let end_time = new Date($('#end_time').val());

    if (start_time > end_time){
        toggle_alert(false, "", "起止时间输入有误，请确认后重新输入");
        return false;
    }
    //保证有负责人
    if ($('#leader').children().length == 0){
        toggle_alert(false, "", "请输入负责人");
        return false;
    }
    if ($('#company').val().length == 0){
        toggle_alert(false, "", "请输入支撑单位");
        return false;
    }
    return true;
}
/**
 * 提交form表单，在提交之前会组合所有的class="domain"的span的值，然后使用;拼接
 * 赋值给#domain中，之后发给后端
 */
function submitData() {
    //检测输入是否合法
    if (!checkValid()){
        return;
    }
    //获取class="member"的所有成员
    let $members = $('.member');
    let data = [];
    for (let i = 0; i < $members.length; i++){
        let member = $members[i];
        let datum = {
            'school': member.getAttribute('data-school'),
            'institution': member.getAttribute('data-institution'),
            'id': parseInt(member.getAttribute('data-id')),
            'name': member.innerText,
        };
        data.push(datum);
    }
    //把值添加到隐藏字段members中
    $('#members').val(JSON.stringify(data));

    //提交表单
    document.getElementById('project-form').submit();
}

