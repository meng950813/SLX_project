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

/**
 * 删除拜访记录
 * @param element
 */
function deleteRecord(element) {
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
        if(data.success){
            toggle_alert(true, "删除成功");
            //删除此条记录
            element.parents('tr').remove();
            $('#total').text(parseInt($('#total').text()) - 1);
        }
    });
}
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
    let csrf_token = $('#csrf_token').val();
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
            csrf_token: csrf_token,
        },
        dataType: 'json'
    }).done(function (data) {
        console.log(data);
        //新的拜访记录添加成功
        if (!isModifying){
            if (!data.success){
                toggle_alert(false, "拜访记录添加失败");
                return ;
            }
            let record_id = data.record_id;
            let total = parseInt($('#total').text()) + 1;
            let insert_html =
                `<tr><td>${total}</td><td>${date}</td><td><a>${title}</a></td><td>${school}</td> <td>${institution}</td> <td>${teacher}</td> 
                <td class="operation">
                    <button class="btn btn-info" href="#" data-toggle="modal" data-target="#exampleModal" onclick="fillModal($(this));">修改</button>
                    <form style="display: inline">
                        <input type="hidden" id="csrf_token" name="csrf_token" value="${csrf_token}"/>
                        <input type="hidden" id="identifier" name="id" value="${record_id}">
                        <button class="btn btn-danger" type="button" onclick="deleteRecord($(this));">删除</button>
                    </form>
                    <input type="hidden" id="detail" value="${content}">
                </td></tr>`;
            let $tr=$("#tab tr").eq(-2);
            $tr.after(insert_html);
            //修改总数目
            $('#total').text(total);

            toggle_alert(true, "拜访记录添加成功");
        }
        else if(data.success){
            toggle_alert(true, "修改成功");
        }
    });
    //隐藏模态框
    $('#exampleModal').modal('hide');
}

/**
 * 显示/隐藏提示框
 * @param {boolean} isSuccess
 * @param {string} text 要显示的文本
 */
function toggle_alert(isSuccess, text){
    let success = $("#alert-box-success");
    let error = $("#alert-box-danger");
    // 显示操作成功的提示框
    if(isSuccess){
        error.hide();
        success.show(200);
        success.text(text);
        setTimeout(()=>{
            success.hide(200);
        }, 2000)
    }else{
        success.hide();
        error.show(200);
        error.text(text);
        setTimeout(()=>{
            error.hide(200);
        },2000);
    }
}
