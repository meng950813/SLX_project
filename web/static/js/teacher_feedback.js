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

//获取研究领域的隐藏字段,若存在，则添加领域
if ($('#domain').val().length > 0) {
    let domains = $('#domain').val().split(';');
    for (let i = 0; i < domains.length; i++){
        addDomain($('#add-domain'), domains[i]);
    }
}

//移除指定的领域
function removeTheDomain($target) {
    $target.parent().remove();
}

/**
 * 添加可编辑的<span>,并带有焦点
 * @param $target "添加"按钮
 * @param value <span>对应的默认值
 */
function addDomain($target, value="") {
    //如果有一个为空，则不添加新的区域
    let $domains = $('.domain');
    for (let i = 0; i < $domains.length; i++){
        let text = $domains[i].innerHTML;
        if (text.length == 0)
            return;
    }

    //在添加按钮前添加新的<span> 标签
    $target.before(`
        <span>
            <span contenteditable="true" class="domain">${value}</span>
            <i class="mdui-icon material-icons" style="cursor: pointer" onclick="removeTheDomain($(this));">&#xe14c;</i>
        </span>`);
    //让最新产生的输入获得焦点
    $('.domain').focus();
}

/**
 * 提交form表单，在提交之前会组合所有的class="domain"的span的值，然后使用;拼接
 * 赋值给#domain中，之后发给后端
 */
function submitData() {
    let $domains = $('.domain');
    let content = [];
    for (let i = 0; i < $domains.length; i++){
        let text = $domains[i].innerHTML;
        content .push(text);
    }
    $('#domain').val(content.join(';'));

    document.getElementById('teacher-info').submit();
}

