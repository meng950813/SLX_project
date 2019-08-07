//echarts 对象
let myChart = echarts.init(document.getElementById('container'));

//树属性
let treeOption = {
    tooltip: {
        trigger: 'item',
        triggerOn: 'mousemove',
        formatter: function (params) {
            //设置提示框的内容和格式 节点和边都显示name属性
            return "todo"
        }
    },
    series:[{
        type: 'tree',
        data: [],
        top: '1%',
        left: '7%',
        bottom: '1%',
        right: '30%',
        symbolSize: 15,
        label: {
            normal: {
                position: 'left',
                verticalAlign: 'middle',
                align: 'right',
                fontSize: 12
            }
        },
        leaves: {
            label: {
                normal: {
                    position: 'right',
                    verticalAlign: 'middle',
                    align: 'left'
                }
            }
        },
        //height:600,

        roam: true,
        initialTreeDepth:2,
        expandAndCollapse: true,
        animationDuration: 550,
        animationDurationUpdate: 750
    }
    ]
};


/**
 * 显示行政关系
 */
function showTree() {
    let schoolName = $('#cur_school').val();
    myChart.showLoading();
    $.ajax({
        type: "get",
        url: "get_institution_info",
        dataType: "json",
        data: {
            school:schoolName
        },
        success: function (response) {
            data = response.data;
            myChart.hideLoading();
            echarts.util.each(data.children, function (datum, index) {
                index === 1 && (datum.collapsed = true);
            });
            treeOption.series[0].data = [data];
            myChart.setOption(treeOption);
            myChart.on('click', function (params) {
                if(params.name!="重点学院" && params.name!="非重点学院" && params.name!=schoolName) {
                    let url = schoolName + '/' + params.name;
                    //window.open(url);
                    window.location.href = url;
                }
            })
        },
        error: function(error){
            myChart.hideLoading();
        }

    });

}

showTree();