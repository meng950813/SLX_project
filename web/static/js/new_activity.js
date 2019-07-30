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

    console.log(teachers);

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
    //添加行
    let $target = $('#results');
    let order = $target.children().length + 1;
    $target.append(`
    <tr>
        <th scope="row">${order}</th>
        <td>
            <span class="member" data-school="${school}" data-institution="${institution}" data-id="${teacherID}">${personName}</span>
        </td>
        <td>
            <input type="text" name="other" class="other form-control" placeholder="企业名称">
        </td>
        <td>
            <i class="mdui-icon material-icons" style="cursor: pointer" onclick="removeTheSpan($(this));">&#xe14c;</i>
        </td>
    </tr>`);
    //让最新产生的输入获得焦点
    $('.other').focus();
}

//移除指定的行
function removeTheSpan($target) {
    $target.parent().parent().remove();
}

/**
 * 提交form表单，在提交之前会组合所有的class="domain"的span的值，然后使用;拼接
 * 赋值给#domain中，之后发给后端
 */
function submitData() {
    let results = $('#results').children();
    let relations = [];
    for (let i = 0; i < results.length; i++){
        let result = results[i];
        //获取老师
        let list1 = result.getElementsByClassName('member');
        //获取公司
        let list2 = result.getElementsByClassName('other');

        if (list1.length > 0 && list2.length > 0){
            let teacher = list1[0];
            let other = list2[0];
            //获取名字
            let school = teacher.getAttribute('data-school');
            let institution = teacher.getAttribute('data-institution');
            let id = teacher.getAttribute('data-id');
            let name = teacher.innerHTML;
            let company = $(other).val();

            if (company.length == 0){
                toggle_alert(false, "", "请输入企业的名称");
                return;
            }
            relations.push('' + id + " " + company);
        }
    }
    console.log(relations);
    //document.getElementById('teacher-info').submit();
}

