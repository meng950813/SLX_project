//选中项
let tds = null;
let detail = null;
let identifier = null;
//当前是在修改数据还是在添加新的拜访记录
let isModifying = true;

/**
 * 点击修改按钮后的填充模态框函数
 * @param e
 */
function fillModal(e){
    //修改模态框标题
    $(".modal-title").text("修改拜访记录");
    //选择其他的兄弟
    tds = e.parent().siblings();
    isModifying = true;
    //将表格中的内容逐个取出，然后填到表单中去
    let input_model = $("#exampleModal .mod");
    for(let i = 1;i < tds.length;i++){
        input_model[i - 1].value = tds[i].innerText;
    }
    detail = e.parent('.operation').find('#detail');
    identifier = e.siblings('form').find('#identifier');
    $('#content').val(e.parent('.operation').find('#detail').val());
}

/**
 * 添加新的拜访记录
 */
function wantToNewRecord() {
    isModifying = false;
    $(".modal-title").text("添加拜访记录");
}

/*
function deleteRecord(element) {
    console.log('want delete');
    if (!confirm('确定删除此条记录?'))
        return;
    let record_id = element.parent().parent('.operation').find('#identifier').val();
    let csrf_token = element.parent().find('#csrf_token').val();
    //发送事件
    $.ajax({
        url: '/visit_record/delete',
        type: 'POST',
        data: {
            id: record_id,
            csrf_token: csrf_token,
        },
        dataType: 'json'
    }).done(function (data) {
        console.log(data);
        //删除此条记录
        element.parents('tr').remove();
        $('#total').text(parseInt($('#total').text()) - 1);
    });
}
 */

/*
修改，点击保存时改变所选那一行的数据 给要修改的那一行添加一个属性，利用这个属性去选择正在
修改的那一行，然后捕捉到关闭模态框的状态，关闭模态框时将这一行的属性去掉；
 */
function saveVisitedRecord(e){
    let date = $('#date').val();
    let title = $('#title').val();
    let school = $('#school').val();
    let institution = $('#institution').val();
    let teacher = $('#teacher').val();
    let content = $('#content').val();
    let id = null;
    let url = '';
    //回写
    if (isModifying){
        //模态框
        let input_model = $("#exampleModal .mod");
        for(let i = 1;i < tds.length;i++){
            tds[i].innerHTML = input_model[i - 1].value;
        }
        detail.val(content);
        id = parseInt(identifier.val());
        url = '/visit_record/edit';
    }else{
        url = '/visit_record/new';
    }
    tds = null;
    detail = null;
    //发送事件
    $.ajax({
        url: url,
        type: 'POST',
        data: {
            id: id,
            date: date,
            school: school,
            institution: institution,
            teacher: teacher,
            content: content,
            title: title,
            csrf_token: $('#csrf_token').val(),
        },
        dataType: 'json'
    }).done(function (data) {
        console.log(data);
        //添加新的拜访记录，则必须刷新页面
        if (!isModifying)
            window.location.reload();
    });
    //隐藏模态框
    $('#exampleModal').modal('hide');
}
