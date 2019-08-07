//echarts 对象
let myChart = echarts.init(document.getElementById('container'));

//树属性
let treeOption = {
    tooltip: {
        trigger: 'item',
        triggerOn: 'mousemove',
        formatter: function (params) {
            //设置提示框的内容和格式 节点和边都显示name属性
            return "行政关系。。。"
        }
    },
    series:[{
                type: 'tree',
                data: [],
                top: '1%',
                left: '7%',
                bottom: '1%',
                right: '20%',
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
                height:600,

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
    var schoolname = document.getElementById("charge_school").innerText
    myChart.showLoading();
    $.ajax({
        type: "get",
        url: "get_institution_info",
        dataType: "json",
        data: {
            school:schoolname
        },
        success: function (response) {
            $.get('../static/relation_data/back_tree.json', function (data) {
                data = response.data
                myChart.hideLoading();
                echarts.util.each(data.children, function (datum, index) {
                    index === 1 && (datum.collapsed = true);
                });
                treeOption.series[0].data = [data];
                myChart.setOption(treeOption);
                myChart.on('click', function (params) {
                        if(params.name!="重点学院" && params.name!="非重点学院" && params.name!=schoolname) {
                            url = schoolname + '/' + params.name;
                            window.open(url);
                            // getInstitutionGraphData(schoolname,params.name)
                            // $.ajax({
                            //     type:"get",
                            //     url:"/<school>/<institution>",
                            //     dataType: "json",
                            //     data:{
                            //         school:schoolname,
                            //         institution:params.name,
                            //     }
                            // })
                        }

            });
            })
        },
        error: function(error){
            myChart.hideLoading();
        }

    });

}

showTree()