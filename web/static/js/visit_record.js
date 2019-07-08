function modify_medol(e){
    //修改模态框标题
    console.log(e)
    c = e

    $(".modal-title").text("修改拜访记录");

    //将表格中的内容添加在表单中
    //选择修改a标签所在的单元格
    let target = $(e.target);
    //选择其他的兄弟
    let tds = e.parent().siblings();
    console.log(target, tds)
    //将表格中的内容逐个取出，然后填到表单中去
    input_model = $("#exampleModal .mod");
    for(var i=0;i<input_model.length;i++){
        input_model[i].value = tds[i].textContent;
    }
    //给这个正在修改的行添加一个属性
    target.parent().parent().addClass("modifying");

}
//点击“修改”，触发修改拜访记录功能
$(".modify-btn").on("click", modify_medol);

//修改，点击保存时改变所选那一行的数据 给要修改的那一行添加一个属性，利用这个属性去选择正在修改的那一行，然后捕捉到关闭模态框的状态，关闭模态框时将这一行的属性去掉；
$(".preservation").on("click",function (e){
    mod_title = $(".modal-title");
    if (mod_title.text() === "修改拜访记录"){
        //选中正在被修改的那一行的子元素
        let td = $(".modifying");
        tds = td.children();
        //模态框
        input_model = $("#exampleModal .mod");
        for(var i=0;i<=input_model.length;i++){
            tds[i].textContent=input_model[i].value
        }
    }else{
        //模态框
        input_model = $("#exampleModal .mod");
        var insert_html = `<tr><td>2019-06-28</td><td>上海交融大学</td> <td>计算机学院</td> <td>罗军舟</td> <td><a href=#>关于计算机科学产学研合</a></td>
                        <td class="operation"><a class="modify-btn"  data-toggle="modal" data-target="#exampleModal"  onclick="modify_medol($(this))" >修改</a>
                        <a class="delete" href=#>删除</a></td> </tr>`

        var $tr=$("#tab tr").eq(-2);
        $tr.after(insert_html);
    }


});


//关闭模态框时，将被选中的那一行modifying属性去掉
$(function () { $('#exampleModal').on('hide.bs.modal', function () {

    let td = $(".modifying");
    td.removeClass("modifying");
})

});



//点击“添加新纪录”，触发添加新纪录功能
$("#add-new-record").on("click", function (e) {
    mod_title = $(".modal-title");
    mod_title.text("添加拜访记录");
    //选择a标签所在的单元格
    input_model = $("#exampleModal .mod");
    for(var i=0;i<input_model.length;i++){
        input_model[i].value = "";
    }
});

//删除一条记录
$(".delete").on("click", function (e) {
    let target = $(e.target);
    //选择其他的兄弟
    let td = target.parent().parent();
    var res=confirm("确定要删除么？");
    if(res){
        //删除界面元素，当前行
        td.remove();
        alert("删除成功")
    }
});


// 增加新纪录，点击保存时，与修改点击同一个按钮，所以要判断；
// 点击保存时，在倒数第二行下面添加一行






