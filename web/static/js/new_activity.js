/**
 * 增/删参数项
 */
$("#params-list").on("click", (e)=>{
    let $target = $(e.target);
    // 添加参数项
    if($target.hasClass("plus-icon")){
        let insert_content = `
        <div class="param-items">
            <input type="text" class="params-key" placeholder="参数名">
            <input type="text" class="params-value" placeholder="参数值">
            <i class="fa fa-plus-circle plus-icon"></i>
            <i class="fa fa-minus-circle minus-icon"></i>
        </div>`;
        $target.parent().after(insert_content);
    }
    else if ($target.hasClass("minus-icon")){
        $target.parent().remove();
    }
});

